from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from client.openai_client import client
from env_var import model
from tools.tools import tools, tool_map
import json
import uuid

app = FastAPI(
    title="Customer Support Agent API",
    description="AI powered customer support agent",
    version="1.0.0"
)

# ✅ Allow Flutter/Web apps to call this API
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# ✅ Session storage — one history per user
sessions: dict = {}

SYSTEM_PROMPT = """You are a professional customer support assistant.
You have access to tools — use them whenever needed:
- Questions about products or FAQs → search_document
- Math or price calculations → calculate
- Weather → get_weather
- Time → get_current_time
- General questions → answer directly

Rules:
- Always be polite and professional
- Keep answers clear and concise
- If you cannot find an answer, say "I'll escalate this to our team"
"""

def get_session(session_id: str) -> list:
    if session_id not in sessions:
        sessions[session_id] = [
            {"role": "system", "content": SYSTEM_PROMPT}
        ]
    return sessions[session_id]


# ─────────────────────────────────────────
# ✅ REQUEST / RESPONSE MODELS
# ─────────────────────────────────────────

class ChatRequest(BaseModel):
    session_id: str
    message: str

class ChatResponse(BaseModel):
    session_id: str
    reply: str
    tools_used: list[str]  # ✅ tells client which tools were called

class NewSessionResponse(BaseModel):
    session_id: str
    message: str


# ─────────────────────────────────────────
# ✅ ROUTES
# ─────────────────────────────────────────

# Health check
@app.get("/")
def root():
    return {
        "status": "running",
        "agent": "Customer Support AI 🤖"
    }

# ✅ Create new session — call this when user opens app
@app.post("/session/new", response_model=NewSessionResponse)
def new_session():
    session_id = str(uuid.uuid4())  # unique ID for each user
    get_session(session_id)          # initialize history
    return NewSessionResponse(
        session_id=session_id,
        message="Session created successfully"
    )

# ✅ Main chat endpoint
@app.post("/chat", response_model=ChatResponse)
def chat(request: ChatRequest):
    if not request.message.strip():
        raise HTTPException(status_code=400, detail="Message cannot be empty")

    history = get_session(request.session_id)
    history.append({"role": "user", "content": request.message})

    tools_used = []

    # Agent loop
    response = client.chat.completions.create(
        model=model,
        messages=history,
        tools=tools
    )
    message = response.choices[0].message

    while message.tool_calls:
        tool_call = message.tool_calls[0]
        tool_name = tool_call.function.name
        tool_args = json.loads(tool_call.function.arguments)

        print(f"  [🔧 Tool: {tool_name} | Args: {tool_args}]")

        tool_result = tool_map[tool_name](**tool_args)
        tools_used.append(tool_name)  # ✅ track tools used

        print(f"  [📦 Result: {tool_result}]")

        history.append(message)
        history.append({
            "role": "tool",
            "tool_call_id": tool_call.id,
            "content": tool_result
        })

        response = client.chat.completions.create(
            model=model,
            messages=history,
            tools=tools
        )
        message = response.choices[0].message

    reply = message.content
    history.append({"role": "assistant", "content": reply})

    return ChatResponse(
        session_id=request.session_id,
        reply=reply,
        tools_used=tools_used
    )

# ✅ Get chat history of a session
@app.get("/session/{session_id}/history")
def get_history(session_id: str):
    if session_id not in sessions:
        raise HTTPException(status_code=404, detail="Session not found")

    history = sessions[session_id]

    # Filter out system message — only return user/assistant messages
    visible = [
        msg for msg in history
        if isinstance(msg, dict) and msg.get("role") in ["user", "assistant"]
    ]
    return {"session_id": session_id, "history": visible}

# ✅ Clear a session
@app.delete("/session/{session_id}")
def clear_session(session_id: str):
    if session_id in sessions:
        del sessions[session_id]
    return {"status": "cleared", "session_id": session_id}

# ✅ List all active sessions (useful for admin/debugging)
@app.get("/sessions")
def list_sessions():
    return {
        "active_sessions": len(sessions),
        "session_ids": list(sessions.keys())
    }
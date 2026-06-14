from client.openai_client import client
from env_var import model
from tools.tools import tools, tool_map
import json

# ✅ AGENT LOOP
history = [
    {
        "role": "system",
        "content": """You are a smart personal assistant.
        You have access to tools — use them whenever needed.
        - For questions about customer and products FAQ → use search_documents
        - For math → use calculate  
        - For weather → use get_weather
        - For time → use get_current_time
        - For general questions → answer directly
        Always give clear and concise answers."""
    }
]

print("🤖 Personal AI Assistant ready! Type 'quit' to exit\n")

while True:
    user_input = input("You: ")

    if user_input.lower() == "quit":
        break

    history.append({"role": "user", "content": user_input})

    # ✅ First AI Call
    response = client.chat.completions.create(
        model= model,
        messages=history,
        tools=tools
    )
    message =response.choices[0].message

    # ✅ Handle tool call
    while message.tool_calls:
        tool_call = message.tool_calls[0]
        tool_name = tool_call.function.name
        tool_args = json.loads(tool_call.function.arguments)

        print(f"  [🔧 Tool: {tool_name} | Args: {tool_args}]")

        # ✅ Run the tool
        tool_result = tool_map[tool_name](**tool_args)

        print(f"  [📦 Result: {tool_result}]")

        # ✅ Add to history
        history.append(message)
        history.append({"role": "tool", "tool_call_id": tool_call.id ,"content": tool_result})

        # Call AI again with tool result
        response = client.chat.completions.create(
            model=model,
            messages=history,
            tools=tools
        )
        message = response.choices[0].message

    reply = message.content
    history.append({"role": "assistant", "content": reply})
    print(f"\n🤖 AI: {reply}\n")










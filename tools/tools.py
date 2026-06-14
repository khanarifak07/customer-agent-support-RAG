import requests
from datetime import datetime
from embedding.embedding import embedding_model
from client.chroma_client import collection

# TOOL 1
def search_document(query: str) -> str:
    question_embedding = embedding_model.encode(query).tolist()
    results = collection.query(
        query_embeddings=[question_embedding],
        n_results=3
    )
    return "\n".join(results["documents"][0])

# TOOL 2
def calculate(expression: str) -> str:
    try:
        return str(eval(expression))
    except:
        return "Invalid expression"

# TOOL 3
def get_weather(city: str) -> str:
    try:
        response = requests.get(f"https://wttr.in/{city}?format=3", timeout=5)
        return response.text
    except:
        return f"Could not found weather for {city}"

# TOOL 4
def get_current_time():
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")


tools = [
    {
        "type": "function",
        "function": {
            "name": "search_document",
            "description": "Search document to answers question about products FAQs",
            "parameters": {
                "type": "object",
                "properties": {
                    "query": {
                        "type": "string",
                        "description": "Search query"
                    }
                },
                "required": ["query"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "calculate",
            "description": "To solve any math expression",
            "parameters": {
                "type": "object",
                "properties": {
                    "expression": {
                        "type": "string",
                        "description": "Math expression like 10 * 10"
                    }
                },
                "required": ["expression"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "get_weather",
            "description": "To get the current weather of city",
            "parameters": {
                "type": "object",
                "properties": {
                    "city": {
                        "type": "string",
                        "description": "City name"
                    }
                }
            },
            "required": ["city"]
        }
    },
{
        "type": "function",
        "function": {
            "name": "get_current_time",
            "description": "To get the current tine",
            "parameters": {
                "type": "object",
                "properties": {},
                "required": []
            }
        }
    },
]

tool_map = {
    "search_document": search_document,
    "calculate": calculate,
    "get_weather": get_weather,
    "get_current_time": get_current_time
}


import json
from openai import OpenAI
import os
from dotenv import load_dotenv

load_dotenv()
api_key = os.getenv("API_KEY")
url = os.getenv("URL")

client = OpenAI(
    base_url=url,
    api_key=api_key
)


def ask_llm(messages, tools):
    return client.chat.completions.create(
        model="anthropic/claude-sonnet-4",
        messages=messages,
        tools=tools,
    )

def get_tool_calls(response):
    message = response.choices[0].message

    if not message.tool_calls:
        return []

    return [
        {
            "id": tool_call.id,
            "name": tool_call.function.name,
            "arguments": json.loads(tool_call.function.arguments),
        }
        for tool_call in message.tool_calls
    ]

def convert_mcp_tools(mcp_tools):
    return [
        {
            "type": "function",
            "function": {
                "name": tool.name,
                "description": tool.description,
                "parameters": tool.input_schema,
            },
        }
        for tool in mcp_tools
    ]

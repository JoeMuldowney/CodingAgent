import json

from ollama import chat

# def mcp_tool_to_ollama(tool):
#     return {
#         "type": "function",
#         "function": {
#             "name": tool.name,
#             "description": tool.description or "",
#             "parameters": tool.input_schema,
#         },
#     }

TOOLS = [
{
    "type": "function",
    "function": {
        "name": "search_all_files",
        "description": (
            "List the files available in the project. "
            "Use this when you need to discover files "
            "before reading one."
        ),
        "parameters": {
            "type": "object",
            "properties": {},
        },
    },
},
    {
        "type": "function",
        "function": {
            "name": "read_file",
            "description": "Read the complete contents of a project file.",
            "parameters": {
                "type": "object",
                "properties": {
                    "filename": {
                        "type": "string",
                        "description": "Path to the file relative to the project root.",
                    }
                },
                "required": ["filename"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "edit_file",
            "description": (
                "Make a targeted change to an existing project file. "
                "You must first read the file and identify exact existing "
                "text to use as a unique anchor. "
                "Use 'before' or 'after' to insert new text around the anchor, "
                "or 'replace' to replace the anchor itself. "
                "Never use an empty anchor."
            ),
            "parameters": {
                "type": "object",
                "properties": {
                    "filename": {
                        "type": "string",
                        "description": (
                            "Path to the file relative to the project root."
                        ),
                    },
                    "anchor": {
                        "type": "string",
                        "description": (
                            "Exact existing text from the file that identifies "
                            "where the edit should occur. The anchor must not "
                            "be empty and must occur exactly once."
                        ),
                    },
                    "new_text": {
                        "type": "string",
                        "description": (
                            "The new text to insert or use as the replacement."
                        ),
                    },
                    "position": {
                        "type": "string",
                        "enum": ["before", "after", "replace"],
                        "description": (
                            "Whether to insert before the anchor, insert after "
                            "the anchor, or replace the anchor."
                        ),
                    },
                },
                "required": [
                    "filename",
                    "anchor",
                    "new_text",
                    "position",
                ],
            },
        },
    },
]

def ask_llm(messages: list, tools: list | None = None):
    return chat(
        model="qwen2.5-coder:7b",
        messages=messages,
        tools=TOOLS,
    )


def get_tool_calls(response):
    # Native Ollama tool calls
    if response.message.tool_calls:
        return response.message.tool_calls

    # Qwen sometimes returns the tool call as JSON
    # embedded inside normal text.
    content = response.message.content

    if not content:
        return []

    decoder = json.JSONDecoder()

    for index, char in enumerate(content):
        if char != "{":
            continue

        try:
            data, _ = decoder.raw_decode(content[index:])
        except json.JSONDecodeError:
            continue

        if (
            isinstance(data, dict)
            and "name" in data
            and "arguments" in data
        ):
            return [
                {
                    "name": data["name"],
                    "arguments": data["arguments"],
                }
            ]

    return []
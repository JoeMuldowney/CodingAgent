import asyncio
from fastmcp import Client

client = Client("http://127.0.0.1:8000/mcp")

from coding_agent.llm_openrouter import (
    ask_llm,
    get_tool_calls,
    convert_mcp_tools,
)


async def main():
    messages = [
        {
            "role": "system",
            "content": (
                "You are a coding agent. "
                "Use tools only when necessary to complete the user's request. "
                "If the user asks what files are available, use "
                "search_all_files and then answer using that result. "
                "Do not read individual files unless the user asks for "
                "their contents or the task requires inspecting them. "

                "When modifying a file: "
                "Read the target file before editing it. "
                "Identify exact existing text from the file to use as a unique anchor. "
                "For edit_file, always provide a non-empty anchor that exactly matches "
                "text in the file. "
                "The anchor must identify the intended location of the change. "
                "Never invent an anchor or use an empty anchor. "
                "Preserve all unrelated code. "
                "If you cannot identify a safe edit, explain the problem instead "
                "of calling the editing tool."
            ),
        },
        {
            "role": "user",
            "content": "What files are available in the application?"


        },
    ]
    async with client:
        mcp_tools = await client.list_tools()

        tools = convert_mcp_tools(mcp_tools)
        while True:
            response = ask_llm(messages, tools)

            message = response.choices[0].message

            print("\nLLM response:")
            print(response)

            # Preserve the assistant response, including tool calls.
            messages.append(
                {
                    "role": "assistant",
                    "content": message.content,
                    "tool_calls": [
                        {
                            "id": tool_call.id,
                            "type": tool_call.type,
                            "function": {
                                "name": tool_call.function.name,
                                "arguments": tool_call.function.arguments,
                            },
                        }
                        for tool_call in (message.tool_calls or [])
                    ],
                }
            )

            tool_calls = get_tool_calls(response)

            if not tool_calls:
                print("\nFinal answer:")
                print(message.content)
                break

            for tool_call in tool_calls:
                tool_name = tool_call["name"]
                arguments = tool_call["arguments"]

                print(f"\nLLM requested tool: {tool_name}")
                print(f"Arguments: {arguments}")

                result = await client.call_tool(
                    tool_name,
                    arguments,
                )

                print("\nTool result:")
                result_text = "\n".join(
                    item.text
                    for item in result.content
                    if hasattr(item, "text")
                )

                messages.append(
                    {
                        "role": "tool",
                        "tool_call_id": tool_call["id"],
                        "content": result_text,
                    }
                )


if __name__ == "__main__":
    asyncio.run(main())
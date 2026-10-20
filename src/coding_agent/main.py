import asyncio

from coding_agent.llm_ollama import (
     ask_llm,
     get_tool_calls,
)

from coding_agent.tools import (
    search_all_files,
    read_file,
    edit_file,
)


def call_tool(name, arguments):
    if name == "search_all_files":
        return search_all_files()

    if name == "read_file":
        return read_file(**arguments)

    if name == "edit_file":
        return edit_file(**arguments)

    raise ValueError(f"Unknown tool: {name}")


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
                "Identify exact existing text from the file to use as a unique anchor."
                "For edit_file, always provide a non-empty anchor that exactly matches text in the file."
                "The anchor must identify the intended location of the change."
                "Never invent an anchor or use an empty anchor."
                "Preserve all unrelated code. "
                "If you cannot identify a safe edit, explain the problem instead of calling the editing tool."
            ),
        },
        {
            "role": "user",
            "content": "what files can you see?",
        },
    ]

    while True:
        response = ask_llm(messages)

        print("\nLLM response:")
        print(response)

        # Preserve the complete assistant response,
        # including any tool calls.
        messages.append(response.message)

        tool_calls = get_tool_calls(response)

        if not tool_calls:
            print("\nFinal answer:")
            print(response.message.content)
            break

        for tool_call in tool_calls:

            if hasattr(tool_call, "function"):
                tool_name = tool_call.function.name
                arguments = tool_call.function.arguments

            else:
                tool_name = tool_call["name"]
                arguments = tool_call["arguments"]

            print(f"\nLLM requested tool: {tool_name}")
            print(f"Arguments: {arguments}")

            result = call_tool(
                tool_name,
                arguments,
            )

            print("\nTool result:")
            print(result)

            messages.append(
                {
                    "role": "tool",
                    "content": result,
                }
            )


asyncio.run(main())
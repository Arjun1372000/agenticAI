from __future__ import annotations

from typing import Any

from mcp import Client
from ollama import AsyncClient


MCP_URL = "http://127.0.0.1:8001/mcp"
OLLAMA_MODEL = "llama3.2"


SYSTEM_PROMPT = """
You are an industrial predictive-maintenance assistant.

You assist a maintenance or condition-monitoring engineer
with bearing vibration diagnostics.

You have access to deterministic MCP tools that provide:
- current bearing health
- recent degradation trends
- maintenance recommendations

IMPORTANT RULES:
1. Never invent sensor measurements, probabilities, RUL values,
   failure times, or diagnostic values.
2. Use MCP tools when the user asks about bearing condition,
   degradation, trends, or maintenance.
3. For a general bearing assessment, use the available diagnostic
   tools to gather sufficient evidence before answering.
4. Treat Healthy, Degraded, and Severe as condition/degradation
   assessments, not definitive proof of physical failure.
5. Do not claim imminent failure or certain failure unless a
   validated prediction explicitly supports it.
6. Clearly distinguish measured evidence from interpretation.
7. Base the final answer only on evidence returned by the tools.
8. When maintenance priority is High, recommend inspection and
   maintenance planning rather than claiming confirmed failure.
9. Keep the final response concise and useful to an engineer.
"""


def mcp_tools_to_ollama(
    mcp_tools: list[Any],
) -> list[dict[str, Any]]:

    return [
        {
            "type": "function",
            "function": {
                "name": tool.name,
                "description": tool.description or "",
                "parameters": tool.input_schema,
            },
        }
        for tool in mcp_tools
    ]


def extract_tool_text(result: Any) -> str:

    parts = []

    for block in result.content:
        text = getattr(block, "text", None)

        if text:
            parts.append(text)

    return "\n".join(parts) or "The tool returned no textual result."


async def ask_agent(
    user_query: str,
) -> str:

    async with Client(MCP_URL) as mcp_client:

        mcp_result = await mcp_client.list_tools()

        ollama_tools = mcp_tools_to_ollama(
            mcp_result.tools
        )

        messages: list[Any] = [
            {
                "role": "system",
                "content": SYSTEM_PROMPT,
            },
            {
                "role": "user",
                "content": user_query,
            },
        ]

        ollama_client = AsyncClient()

        for _ in range(5):

            response = await ollama_client.chat(
                model=OLLAMA_MODEL,
                messages=messages,
                tools=ollama_tools,
            )

            tool_calls = response.message.tool_calls

            if not tool_calls:
                return (
                    response.message.content
                    or "The agent returned no response."
                )

            messages.append(response.message)

            for tool_call in tool_calls:

                tool_name = tool_call.function.name

                arguments = dict(
                    tool_call.function.arguments
                )

                result = await mcp_client.call_tool(
                    tool_name,
                    arguments,
                )

                tool_output = extract_tool_text(
                    result
                )

                messages.append(
                    {
                        "role": "tool",
                        "content": tool_output,
                        "tool_name": tool_name,
                    }
                )

        return (
            "The agent reached the maximum number "
            "of tool-calling steps."
        )
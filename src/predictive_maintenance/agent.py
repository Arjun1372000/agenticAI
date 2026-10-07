from __future__ import annotations

from typing import Any

from mcp import Client
from ollama import AsyncClient


MCP_URL = "http://127.0.0.1:8001/mcp"
OLLAMA_MODEL = "llama3.2"


SYSTEM_PROMPT = """
You are an industrial predictive-maintenance decision-support agent.

You help a maintenance or condition-monitoring engineer interpret
historical bearing telemetry.

Available MCP tools:
- get_bearing_health
- get_bearing_trend
- get_maintenance_recommendation
- compare_bearings

IMPORTANT:
1. Use MCP tools to obtain actual engineering evidence.
2. Never invent sensor values, failure probabilities, RUL values,
   or measurements.
3. Healthy, Degraded, and Severe are degradation assessments,
   not proof of physical failure.
4. Never claim imminent or certain failure unless a validated
   tool explicitly provides such evidence.
5. For a bearing assessment, use health and trend evidence.
6. Use the maintenance tool when recommending action.
7. For questions about which bearing needs the most attention,
   use compare_bearings.
8. Base the final answer on MCP evidence.
9. Clearly distinguish evidence from interpretation.
10. Keep the final answer concise and useful for an engineer.
"""


def mcp_tools_to_ollama(mcp_tools: list[Any]) -> list[dict[str, Any]]:
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


def is_compare_request(user_query: str) -> bool:
    text = user_query.lower()

    comparison_phrases = [
        "compare bearings",
        "compare all bearings",
        "compare the bearings",
        "which bearing needs the most attention",
        "which bearing requires the most attention",
        "which bearing is worst",
        "which bearing is in the worst condition",
        "rank the bearings",
        "prioritize the bearings",
    ]

    return any(phrase in text for phrase in comparison_phrases)


async def run_compare_flow(
    mcp_client: Client,
    ollama_client: AsyncClient,
    user_query: str,
    observation_index: int | None,
) -> dict[str, Any]:

    if observation_index is None:
        raise ValueError(
            "A fixed observation_index is required for bearing comparison."
        )

    result = await mcp_client.call_tool(
        "compare_bearings",
        {
            "observation_index": observation_index,
        },
    )

    tool_output = extract_tool_text(result)

    response = await ollama_client.chat(
        model=OLLAMA_MODEL,
        messages=[
            {
                "role": "system",
                "content": SYSTEM_PROMPT,
            },
            {
                "role": "user",
                "content": (
                    f"User request:\n{user_query}\n\n"
                    f"MCP comparison result:\n{tool_output}\n\n"
                    "Interpret the MCP result for the engineer. "
                    "Identify the bearing requiring the most attention "
                    "and explain the evidence. "
                    "Do not invent any additional measurements."
                ),
            },
        ],
    )

    return {
        "answer": response.message.content
        or "The agent returned no response.",
        "tools_used": ["compare_bearings"],
    }


async def run_agent(
    user_query: str,
    bearing_id: int = 1,
    observation_index: int | None = None,
) -> dict[str, Any]:

    async with Client(MCP_URL) as mcp_client:
        mcp_result = await mcp_client.list_tools()

        ollama_tools = mcp_tools_to_ollama(mcp_result.tools)

        if observation_index is None:
            snapshot_text = "Use the latest available telemetry."
        else:
            snapshot_text = (
                f"The fixed analysis snapshot is observation index "
                f"{observation_index} for Bearing {bearing_id}. "
                "All telemetry analysis must refer only to data "
                "available up to this observation."
            )

        ollama_client = AsyncClient()

        # ---------------------------------------------------------
        # Deterministic high-value comparison route
        # ---------------------------------------------------------
        if is_compare_request(user_query):
            return await run_compare_flow(
                mcp_client=mcp_client,
                ollama_client=ollama_client,
                user_query=user_query,
                observation_index=observation_index,
            )

        # ---------------------------------------------------------
        # Normal agentic tool-calling flow
        # ---------------------------------------------------------
        messages: list[Any] = [
            {
                "role": "system",
                "content": SYSTEM_PROMPT,
            },
            {
                "role": "user",
                "content": (
                    f"{snapshot_text}\n\n"
                    f"User request:\n{user_query}"
                ),
            },
        ]

        tools_used: list[str] = []

        for _ in range(5):

            response = await ollama_client.chat(
                model=OLLAMA_MODEL,
                messages=messages,
                tools=ollama_tools,
            )

            tool_calls = response.message.tool_calls

            if not tool_calls:
                return {
                    "answer": response.message.content
                    or "The agent returned no response.",
                    "tools_used": tools_used,
                }

            messages.append(response.message)

            for tool_call in tool_calls:

                tool_name = tool_call.function.name
                arguments = dict(tool_call.function.arguments)

                # Always enforce the selected historical snapshot.
                if observation_index is not None:
                    arguments["observation_index"] = observation_index

                if tool_name in {
                    "get_bearing_health",
                    "get_bearing_trend",
                    "get_maintenance_recommendation",
                }:
                    arguments.setdefault("bearing_id", bearing_id)

                if tool_name not in tools_used:
                    tools_used.append(tool_name)

                result = await mcp_client.call_tool(
                    tool_name,
                    arguments,
                )

                tool_output = extract_tool_text(result)

                messages.append(
                    {
                        "role": "tool",
                        "content": tool_output,
                        "tool_name": tool_name,
                    }
                )

        return {
            "answer": (
                "The agent reached the maximum number "
                "of tool-calling steps."
            ),
            "tools_used": tools_used,
        }


async def ask_agent(
    user_query: str,
    bearing_id: int = 1,
    observation_index: int | None = None,
) -> dict[str, Any]:
    return await run_agent(
        user_query=user_query,
        bearing_id=bearing_id,
        observation_index=observation_index,
    )
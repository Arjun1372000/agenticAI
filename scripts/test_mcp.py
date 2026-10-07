import asyncio

from mcp import Client


MCP_URL = "http://127.0.0.1:8001/mcp"


def print_result(title: str, result) -> None:
    print("\n" + "=" * 60)
    print(title)
    print("=" * 60)

    for block in result.content:
        text = getattr(block, "text", None)

        if text:
            print(text)


async def main() -> None:

    async with Client(MCP_URL) as client:

        result = await client.list_tools()

        print("Available MCP tools:")

        for tool in result.tools:
            print(f"  - {tool.name}")

        # ---------------------------------------------------------
        # Bearing Health
        # ---------------------------------------------------------
        health_result = await client.call_tool(
            "get_bearing_health",
            {
                "bearing_id": 1,
                "observation_index": 983,
            },
        )

        print_result(
            "BEARING HEALTH",
            health_result,
        )

        # ---------------------------------------------------------
        # Bearing Trend
        # ---------------------------------------------------------
        trend_result = await client.call_tool(
            "get_bearing_trend",
            {
                "bearing_id": 1,
                "observation_index": 983,
            },
        )

        print_result(
            "BEARING TREND",
            trend_result,
        )

        # ---------------------------------------------------------
        # Maintenance Recommendation
        # ---------------------------------------------------------
        recommendation_result = await client.call_tool(
            "get_maintenance_recommendation",
            {
                "bearing_id": 1,
                "observation_index": 983,
            },
        )

        print_result(
            "MAINTENANCE RECOMMENDATION",
            recommendation_result,
        )

        # ---------------------------------------------------------
        # Compare Bearings
        # ---------------------------------------------------------
        comparison_result = await client.call_tool(
            "compare_bearings",
            {
                "observation_index": 983,
            },
        )

        print_result(
            "COMPARE BEARINGS",
            comparison_result,
        )


if __name__ == "__main__":
    asyncio.run(main())
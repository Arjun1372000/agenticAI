import asyncio

from mcp import Client


async def main() -> None:

    async with Client(
        "http://127.0.0.1:8001/mcp"
    ) as client:

        result = await client.list_tools()

        print("\nAvailable MCP tools:")

        for tool in result.tools:
            print(f"  - {tool.name}")

        print("\n" + "=" * 60)
        print("BEARING HEALTH")
        print("=" * 60)

        response = await client.call_tool(
            "get_bearing_health",
            {
                "bearing_id": 1,
            },
        )

        for content in response.content:
            if hasattr(content, "text"):
                print(content.text)

        print("\n" + "=" * 60)
        print("BEARING TREND")
        print("=" * 60)

        response = await client.call_tool(
            "get_bearing_trend",
            {
                "bearing_id": 1,
                "window": 24,
            },
        )

        for content in response.content:
            if hasattr(content, "text"):
                print(content.text)

        print("\n" + "=" * 60)
        print("MAINTENANCE RECOMMENDATION")
        print("=" * 60)

        response = await client.call_tool(
            "get_maintenance_recommendation",
            {
                "bearing_id": 1,
            },
        )

        for content in response.content:
            if hasattr(content, "text"):
                print(content.text)


if __name__ == "__main__":
    asyncio.run(main())
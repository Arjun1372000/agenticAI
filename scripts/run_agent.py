import asyncio

from predictive_maintenance.agent import run_agent


def main() -> None:

    print(
        "Industrial Predictive Maintenance Agent"
    )
    print(
        "Type 'exit' to quit.\n"
    )

    while True:

        query = input("You: ").strip()

        if query.lower() == "exit":
            break

        if not query:
            continue

        try:
            asyncio.run(
                run_agent(query)
            )
        except KeyboardInterrupt:
            print(
                "\nAgent stopped."
            )
            break
        except Exception as exc:
            print(
                f"\nError: {exc}"
            )


if __name__ == "__main__":
    main()
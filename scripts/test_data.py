from predictive_maintenance.data import (
    get_test_configs,
    list_vibration_files,
    load_vibration_file,
    parse_timestamp,
    validate_test_directory,
)


def main():
    configs = get_test_configs("bearing-dataset")

    for test_id, config in configs.items():
        print(f"\n{test_id.upper()}")
        print("-" * 30)
        print("Path:", config.path)
        print("Expected channels:", config.channels)

        validate_test_directory(config)

        files = list_vibration_files(config.path)
        first_file = files[0]

        print("Files:", len(files))
        print("First file:", first_file)
        print("Timestamp:", parse_timestamp(first_file))

        df = load_vibration_file(first_file)

        print("Shape:", df.shape)


if __name__ == "__main__":
    main()
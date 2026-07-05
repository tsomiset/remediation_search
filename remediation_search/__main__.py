import sys

from remediation_search.processing import process_input, get_usage_text


def main():
    """Main entry point: parse arguments and route to input processor."""
    raw_input = " ".join(sys.argv[1:]).strip()

    if not raw_input:
        print(get_usage_text())
        sys.exit(0)

    process_input(raw_input)


if __name__ == "__main__":
    main()


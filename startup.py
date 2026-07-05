"""Root startup entrypoint for launching the API server."""

from remediation_search.api.app import run


def main() -> None:
    """Start the remediation API server."""
    run()


if __name__ == "__main__":
    main()

#python -m remediation_search .\PodsInCrashloopbackoff.docx //to insert new document into the database
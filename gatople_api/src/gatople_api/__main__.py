"""`python -m gatople_api` — runs the service without needing the
`uvicorn '...:app_factory' --factory` invocation memorized. Reads the same
API_PORT the Makefile uses, defaulting to 8002."""

import os

import uvicorn


def main() -> None:
    port = int(os.environ.get("API_PORT", "8002"))
    uvicorn.run(
        "gatople_api.bootstrap:app_factory",
        factory=True,
        host="127.0.0.1",
        port=port,
        reload=True,
    )


if __name__ == "__main__":
    main()

"""Runtime settings loaded from pyproject.toml."""

from dataclasses import dataclass
from functools import lru_cache
from pathlib import Path
import tomllib


@dataclass(frozen=True)
class RuntimeSettings:
    """Application settings used to start the API server."""

    host: str = "0.0.0.0"
    port: int = 8000
    reload: bool = False


def _project_root() -> Path:
    return Path(__file__).resolve().parents[1]


def _load_pyproject() -> dict:
    pyproject_path = _project_root() / "pyproject.toml"

    if not pyproject_path.exists():
        return {}

    with pyproject_path.open("rb") as file_handle:
        return tomllib.load(file_handle)


@lru_cache(maxsize=1)
def get_runtime_settings() -> RuntimeSettings:
    """Return the API runtime settings from pyproject.toml."""

    tool_config = _load_pyproject().get("tool", {}).get("remediation_search", {})
    api_config = tool_config.get("api", {})

    return RuntimeSettings(
        host=str(api_config.get("host", "0.0.0.0")),
        port=int(api_config.get("port", 8000)),
        reload=bool(api_config.get("reload", False)),
    )
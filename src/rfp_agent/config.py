"""설정 로더.

- 역할: configs/*.yaml 을 읽어 dict 로 돌려주고, .env 를 환경변수로 올린다.
- 계약: load_config(path) -> dict. `paths` 아래 값은 레포 루트 기준 절대 경로(str)로 바꿔서 반환한다.
- 소속: Phase 1 (하드코딩 금지 규칙, CLAUDE.md 3절).
"""

from pathlib import Path
from typing import Any

import yaml
from dotenv import load_dotenv

REPO_ROOT = Path(__file__).resolve().parents[2]


def load_config(path: str | Path = "configs/default.yaml") -> dict[str, Any]:
    """설정 파일을 읽어 dict 로 반환한다. 상대 경로는 레포 루트 기준이다."""
    load_dotenv(REPO_ROOT / ".env")
    cfg_path = Path(path)
    if not cfg_path.is_absolute():
        cfg_path = REPO_ROOT / cfg_path
    with cfg_path.open(encoding="utf-8") as f:
        config: dict[str, Any] = yaml.safe_load(f)
    paths = config.get("paths", {})
    for key, value in paths.items():
        p = Path(value)
        paths[key] = str(p if p.is_absolute() else REPO_ROOT / p)
    return config

"""파일명 → doc_id 규칙.

- 역할: 파서, 메타데이터 로더, 로더가 같은 규칙으로 doc_id 를 만들도록 한 곳에 둔다.
- 계약: normalize_name(name) -> NFC 문자열 / make_doc_id(file_name) -> NFC 파일명의 stem (앞뒤 공백 제거).
- macOS 파일명은 NFD 라서 NFC 정규화 없이는 CSV 의 파일명과 비교가 안 된다 (docs/trials 참고).
"""

import unicodedata
from pathlib import Path


def normalize_name(name: str) -> str:
    """유니코드 NFC 로 정규화한다."""
    return unicodedata.normalize("NFC", name)


def make_doc_id(file_name: str) -> str:
    """파일명(경로 가능)에서 doc_id(NFC 파일명 stem)를 만든다."""
    return Path(normalize_name(file_name)).stem.strip()

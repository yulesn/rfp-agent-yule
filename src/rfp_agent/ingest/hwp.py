"""HWP/HWPX 파서.

- 역할: 한글 문서에서 텍스트를 추출한다. 표는 라이브러리 기본 설정에 따라 문서 위치에 마크다운으로 들어간다.
- 계약: parse_hwp(path) -> RfpDocument (file_type 은 확장자에 따라 "hwp"/"hwpx", pages=None).
  HWP 에는 페이지 정보가 없고, 라이브러리도 제목/섹션 정보를 노출하지 않으므로 섹션 구분은 하지 않는다.
- 소속: Phase 1, ADR 0005 (hwp-hwpx-parser 1.0.0 유지 + 경계 검사 패치).

## 경계 검사 패치
hwp-hwpx-parser 1.0.0 의 `_extract_hyperlink_texts_from_para` 는 문단 끝에 `0x0003`(확장 컨트롤 시작) 만 남고
페이로드가 잘려 있으면(`i + 6 > len`) 읽는 위치 `i` 를 올리지 않아 무한 루프에 빠진다.
(원인 분석: docs/trials/2026-11-11-hwp-파서-무한루프-원인.md)
이 모듈을 import 할 때 한 번 원본 메서드를 감싸서, 꼬리에 잘린 `0x03` 이 있으면 그 앞에서 잘라 넘긴다.
라이브러리 파일은 수정하지 않는다. 업스트림이 고쳐져도 안전하다(원본을 그대로 호출한다).
"""

import struct
from pathlib import Path

from rfp_agent.ingest.naming import make_doc_id, normalize_name
from rfp_agent.ingest.schema import RfpDocument

_PATCH_FLAG = "_rfp_agent_bounds_patched"


def _trim_dangling_control(para_data: bytes) -> bytes:
    """문단 꼬리에 페이로드가 잘린 `0x0003` 컨트롤이 있으면 그 앞까지만 돌려준다.

    확장 컨트롤은 코드 2바이트 + 페이로드 14바이트인데, 남은 길이가 6바이트 미만이면
    파서의 `i + 6 <= len` 검사가 거짓이 되어 루프가 멈추지 않는다. 그 위치는 끝에서 4번째/2번째 코드뿐이다.
    """
    n = len(para_data)
    for pos in (n - 4, n - 2):
        if pos >= 0 and struct.unpack_from("<H", para_data, pos)[0] == 0x03:
            return para_data[:pos]
    return para_data


def apply_bounds_patch() -> bool:
    """hwp-hwpx-parser 의 하이퍼링크 추출 메서드를 감싼다. 이미 적용됐으면 False."""
    from hwp_hwpx_parser.hwp5 import HWP5Reader

    original = HWP5Reader._extract_hyperlink_texts_from_para
    if getattr(original, _PATCH_FLAG, False):
        return False

    def patched(self, para_data):  # type: ignore[no-untyped-def]
        return original(self, _trim_dangling_control(para_data))

    setattr(patched, _PATCH_FLAG, True)
    HWP5Reader._extract_hyperlink_texts_from_para = patched  # type: ignore[method-assign]
    return True


apply_bounds_patch()


def parse_hwp(path: str | Path) -> RfpDocument:
    """HWP/HWPX 를 RfpDocument 로 변환한다."""
    from hwp_hwpx_parser import Reader

    path = Path(path)
    with Reader(path) as reader:
        text = reader.text
    return RfpDocument(
        doc_id=make_doc_id(path.name),
        file_name=normalize_name(path.name),
        file_type=path.suffix.lstrip(".").lower(),
        text=text,
        pages=None,
    )

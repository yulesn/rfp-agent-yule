"""hwp-hwpx-parser 경계 검사 패치 테스트 (합성 바이트만 사용, 실제 문서 없음)."""

import struct
import threading

from hwp_hwpx_parser.hwp5 import CTRL_ID_HYPERLINK, HWP5Reader

import rfp_agent.ingest.hwp as hwp_mod


def _run_with_timeout(para: bytes, seconds: float = 5.0) -> tuple[bool, list[str] | None]:
    """메서드를 스레드에서 돌려 제한 시간 안에 끝나는지 본다. (끝났는지, 결과)"""
    result: list[list[str]] = []
    t = threading.Thread(
        target=lambda: result.append(HWP5Reader._extract_hyperlink_texts_from_para(None, para)),
        daemon=True,
    )
    t.start()
    t.join(seconds)
    return (not t.is_alive()), (result[0] if result else None)


def u16(*codes: int) -> bytes:
    return b"".join(struct.pack("<H", c) for c in codes)


def test_patch_is_applied_once() -> None:
    assert hwp_mod.apply_bounds_patch() is False  # import 시 이미 적용됨


def test_truncated_control_at_end_terminates() -> None:
    # 문단 끝: 0x0003 + 0x000d 만 남은 (페이로드가 잘린) 확장 컨트롤. 패치가 없으면 무한 루프.
    para = u16(0x41, 0x42, 0x43, 0x44, 0x45, 0x46, 0x47, 0x03, 0x0D)
    finished, result = _run_with_timeout(para)
    assert finished
    assert result == []


def test_truncated_control_as_last_code_terminates() -> None:
    para = u16(0x41, 0x42, 0x03)
    finished, result = _run_with_timeout(para)
    assert finished
    assert result == []


def test_plain_paragraph_unchanged() -> None:
    finished, result = _run_with_timeout(u16(0x41, 0x42, 0x0D))
    assert finished
    assert result == []


def test_hyperlink_text_still_extracted() -> None:
    # 0x03 + 컨트롤 ID(하이퍼링크) + 8바이트 + 텍스트 'ab' + 0x04
    para = u16(0x03) + struct.pack("<I", CTRL_ID_HYPERLINK) + b"\x00" * 8 + u16(0x61, 0x62, 0x04, 0x0D)
    finished, result = _run_with_timeout(para)
    assert finished
    assert result == ["ab"]


def test_trim_helper() -> None:
    assert hwp_mod._trim_dangling_control(u16(0x41, 0x03, 0x0D)) == u16(0x41)
    assert hwp_mod._trim_dangling_control(u16(0x41, 0x42, 0x0D)) == u16(0x41, 0x42, 0x0D)
    assert hwp_mod._trim_dangling_control(b"") == b""

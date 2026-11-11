# 시행착오 로그

에러, 실패한 시도, 삽질과 해결 과정을 `YYYY-MM-DD-주제.md` 로 남깁니다. 형식은 `.claude/skills/devlog/SKILL.md` 참고.

| 날짜 | 주제 | Phase | 한 줄 요약 |
| --- | --- | --- | --- |
| 2026-11-11 | 의존성 설치 용량 | 1 | sentence-transformers 가 CUDA torch 를 끌고 와 설치 약 20분, .venv 6GB. CPU 전용 휠 설정 추가, lock 재생성은 pytorch 인덱스 접근 가능한 환경에서 필요 |
| 2026-11-11 | 파일명 NFD / HWP 파서 멈춤 | 1 | macOS NFD 파일명이 한글 리터럴과 불일치해 비교 실패, HWP 1건은 파서가 무한 루프 → NFC 정규화 + 파일별 프로세스 타임아웃 |

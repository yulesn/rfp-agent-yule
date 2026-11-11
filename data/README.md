# 데이터

- `raw/`: 구글 드라이브에서 RFP 문서(hwp/hwpx/pdf)와 메타데이터 CSV를 내려받아 이 폴더에 넣습니다. **절대 커밋하지 않습니다** (`.gitignore`).
  메타데이터 파일명은 `configs/default.yaml` 의 `paths.metadata_file` 과 맞춰야 합니다.
- `processed/`: 파싱 결과(jsonl). `scripts/build_index.py` 가 생성합니다.
- `vectorstore/`: Chroma 인덱스. `scripts/build_index.py` 가 생성합니다.

`processed/`, `vectorstore/` 는 생성물이라 커밋하지 않습니다.

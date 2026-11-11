# RFP 에이전트 (솔로)

B2G 입찰지원 컨설팅 스타트업 '입찰메이트'의 사내 RFP(제안요청서) RAG 에이전트를 혼자 처음부터 끝까지 만드는 프로젝트입니다.
팀 프로젝트([rfp-agent-part3-team1](https://github.com/yulesn/rfp-agent-part3-team1))의 솔로 버전입니다.

- 전체 계획: [docs/PLAN.md](docs/PLAN.md)
- 결정 기록(ADR): [docs/decisions/](docs/decisions/)
- 대화 기록: [docs/conversations/](docs/conversations/)
- 시행착오: [docs/trials/](docs/trials/) · 실험: [docs/experiments/](docs/experiments/)
- Claude Code 작업 규칙: [CLAUDE.md](CLAUDE.md)

## 상태

Phase 0 완료, Phase 1 진행 중. 프로젝트 구조(스캐폴드)만 잡혀 있고, 대부분의 모듈은 계약(docstring)과 시그니처만 있는 스텁입니다.
구현된 것: 설정 로더(`config.py`), LLM 팩토리(`llm.py`), 데이터 모델(`ingest/schema.py`), 에이전트 상태(`agent/state.py`).

## 초기 설정

```bash
# 1. uv 설치 (https://docs.astral.sh/uv/)
curl -LsSf https://astral.sh/uv/install.sh | sh

# 2. 의존성 설치 (Python 3.12 가 없으면 uv 가 받아옵니다)
uv sync

# 3. 환경변수 설정: .env 에 GOOGLE_API_KEY 를 채웁니다
cp .env.example .env

# 4. 데이터 배치: 구글 드라이브의 RFP 문서와 메타데이터 CSV 를 data/raw/ 에 넣습니다 (data/README.md 참고)
```

## 프로젝트 구조

```
configs/default.yaml        # 모델, 청크 크기, top_k 등 모든 설정 (실험은 복사해서 exp_NNN_*.yaml)
src/rfp_agent/
  config.py                 # 설정 로더 (.env 포함)
  llm.py                    # 설정 기반 LLM 팩토리
  ingest/                   # 수집: pdf/hwp 파서, 메타데이터 CSV, 로더, 청킹, 스키마
  retrieval/                # 검색: 임베딩, Chroma, 청크 검색, 메타데이터 필터(pandas)
  agent/                    # LangGraph 에이전트: 상태, 프롬프트, 노드, 그래프, tools/
  evaluation/               # 평가: Hit@k/MRR, LLM-as-judge
scripts/                    # CLI: inspect_data, build_index, ask, evaluate
eval/                       # 평가셋 (questions.v1.jsonl)
data/                       # raw(커밋 금지) / processed / vectorstore
notebooks/                  # 탐색용 노트북
backend/ frontend/ infra/   # Phase 4 자리표시 (아직 시작 안 함)
tests/                      # 스모크 테스트
docs/                       # 계획, ADR, 대화, 시행착오, 실험 기록
```

## 실행 (Phase 1 구현 후 동작)

```bash
uv run python scripts/inspect_data.py                                  # 데이터 탐색
uv run python scripts/build_index.py --config configs/default.yaml     # 인덱스 구축
uv run python scripts/ask.py "질문" --config configs/default.yaml      # 질의응답
uv run python scripts/evaluate.py --config configs/default.yaml        # 평가 (Phase 2)
uv run ruff check . && uv run pytest                                   # 커밋 전 검사
```

## Claude Code 사용법

- 계획/리뷰는 Opus, 구현은 Sonnet. `.claude/settings.json` 의 `opusplan` 설정으로 plan mode(Shift+Tab)에서는 Opus, 실행 시에는 Sonnet이 쓰입니다.
- 서브에이전트: `planner`, `reviewer` (Opus) / `implementer`, `researcher` (Sonnet)
- 스킬: `devlog`, `phase-gate`, `experiment-log` + LangChain 공식 스킬 6종

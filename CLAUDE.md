# CLAUDE.md — RFP 에이전트 (솔로)

B2G 입찰지원 컨설팅 스타트업 '입찰메이트'의 사내 RFP RAG 에이전트를 혼자 만드는 프로젝트입니다.
전체 계획은 `docs/PLAN.md`, 지금까지의 결정은 `docs/decisions/` 에 있습니다. 작업 전에 둘 다 읽으세요.

## 1. 절대 규칙

1. **플랜 확정 전에는 구현하지 않는다.** 새 Phase(또는 큰 기능)를 시작할 때는 계획 → Yule 컨펌 → 구현 순서를 지킨다.
   컨펌 기록이 `docs/decisions/` 또는 `docs/conversations/` 에 남아 있어야 구현을 시작할 수 있다.
2. **기술스택은 Yule과 함께 정한다.** 후보 2~3개 + 추천안 + 근거를 제시하고, 정해지면 ADR(`docs/decisions/`)로 남긴다.
   임의로 새 라이브러리/서비스를 추가하지 않는다 (추가가 필요하면 먼저 묻는다).
3. **모든 대화와 시행착오는 레포에 남긴다.** (아래 4절 참고, `devlog` 스킬 사용)
4. 비밀값(.env, API 키, AWS 자격증명)과 원본 데이터(`data/raw/`)는 절대 커밋하지 않는다.
5. 사용자와는 한국어로 대화하고, 문서도 한국어로 쓴다. 코드 식별자와 커밋 메시지 prefix(feat/fix/docs…)는 영어.

## 2. 모델 역할 분리 (Opus = 계획/리뷰, Sonnet = 구현)

| 역할 | 모델 | 방법 |
| --- | --- | --- |
| 기획, 설계, 기술스택 비교, 플랜 작성 | Opus | 메인 세션 plan mode (`.claude/settings.json` 의 `"model": "opusplan"`) 또는 `planner` 서브에이전트 |
| 코드/PR 리뷰, 플랜 리뷰, 실험 결과 해석 | Opus | `reviewer` 서브에이전트 |
| 실제 구현, 테스트 작성, 리팩터링 | Sonnet | plan mode 밖의 메인 세션(opusplan 이 자동으로 Sonnet 사용) 또는 `implementer` 서브에이전트 |
| 웹 조사(라이브러리, 채용공고 기술스택, 모델 리더보드) | Sonnet | `researcher` 서브에이전트 |

- 기본 흐름: `planner`(Opus)가 계획 → Yule 컨펌 → `implementer`(Sonnet)가 구현 → `reviewer`(Opus)가 리뷰 → 수정.
- `opusplan` 을 쓰지 않는다면 계획 시 `/model opus`, 구현 시 `/model sonnet` 으로 직접 전환한다.

## 3. 작업 방식

- 패키지 관리는 `uv` (`uv add`, `uv run`). `pip install` 금지.
- 하드코딩 금지: 모델명, 청크 크기, top_k 등은 `configs/*.yaml` 로 뺀다. 실험은 설정 파일 단위로 구분한다.
- 에이전트 도구는 1파일 1도구. 도구의 docstring 은 LLM이 읽는 설명이므로 신경 써서 쓴다.
- LangGraph/LangChain 코드를 쓸 때는 `.claude/skills/` 의 langchain 스킬을 먼저 참고한다 (API가 자주 바뀜, 기억에 의존하지 말 것).
- 커밋 전 `uv run ruff check . && uv run pytest` 통과.
- 브랜치: `main` 보호, 작업은 `phase<N>/<짧은-설명>` 브랜치 → PR → 리뷰 후 머지.

## 4. 기록 규칙 (docs/)

| 폴더 | 언제 쓰나 | 파일명 |
| --- | --- | --- |
| `docs/conversations/` | Yule과 의미 있는 논의를 할 때마다 (요청, 제안, 합의 내용을 요약. **대화 원문은 올리지 않음**) | `YYYY-MM-DD-주제.md` |
| `docs/decisions/` | 기술스택·구조 결정이 확정될 때 (ADR) | `NNNN-제목.md` |
| `docs/trials/` | 에러, 삽질, 안 된 시도, 그 원인과 해결 | `YYYY-MM-DD-주제.md` |
| `docs/experiments/` | 설정을 바꿔 성능을 비교할 때 (설정, 결과 표, 해석) | `EXP-NNN-제목.md` |
| `docs/architecture/` | 아키텍처 다이어그램(draw.io), 그래프 구조 그림 | `*.drawio`, `*.png` |
| `docs/research/` | 조사 결과 (라이브러리 비교, 채용공고 분석 등) | 자유 |

- 작업 세션이 끝날 때 위 기록이 빠졌는지 확인하고 채운다. 형식은 `devlog` 스킬을 따른다.
- 실패한 시도도 반드시 남긴다. 발표/보고서에서 "왜 이렇게 결정했나"의 근거가 된다.
- `docs/PLAN.md` 의 Phase 상태(✅/🚧/⏳)는 진행에 맞게 갱신한다.

## 5. 참고

- 팀 레포(구조 참고용, 수정 금지): https://github.com/yulesn/rfp-agent-part3-team1
- 서드파티 스킬: `.claude/skills/langchain-*`, `langgraph-*` 는 langchain-ai/langchain-skills (MIT) 에서 가져옴.

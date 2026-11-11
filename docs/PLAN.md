# 전체 플랜 (v0.2, 2026-11-11 Yule 컨펌)

- 작성: 2026-11-09 (v0.1), 2026-11-11 (v0.2: Yule 답변 반영, 변경 내역은 8절)
- 마감일 없음 (개인 포트폴리오 프로젝트). Phase는 순서만 정하고 기간은 정하지 않음.
- **비용 원칙: 유료 API와 AWS 사용을 최소화.** 기본값은 로컬/무료, 유료는 비교 실험이나 데모 때만 짧게.
- 상태: **컨펌됨 (2026-11-11)**. 기술스택 추천안은 컨펌으로 기본값이 되었고, 각 Phase 시작 때 세부 선택을 다시 확인하고 ADR로 남김.
- 진행 표시: ✅ 완료 / 🚧 진행 중 / ⏳ 대기

## 1. 목표

'입찰메이트' 컨설턴트가 수십 페이지짜리 RFP(hwp, pdf 100건)를 직접 읽지 않고도
핵심 정보(요구조건, 발주기관, 예산, 기간, 제출방식, 마감)를 묻고, 찾고, 비교하고, 고객사에 맞는 공고를 추천받을 수 있는 **RAG 기반 복합 에이전트 웹 서비스**.

| 단계 | 목표 | 완료 기준 |
| --- | --- | --- |
| 1차 (베이스라인) | LangGraph 에이전트가 RAG 도구로 RFP 질의응답 | 평가셋 질문에 출처(문서·페이지) 인용과 함께 답변, 평가 점수 1회 산출 |
| 2차 (최종) | 컨설팅 업무용 도구/노드를 갖춘 복합 에이전트 + 웹 서비스 + AWS 배포 | 아래 Phase 3~9 완료, 공개 URL로 데모 가능 |

멘토 우선순위(LLM 에이전트 > 클라우드 > PDF 청킹 > RAG/평가 > Jev/가드레일)를 Phase 순서에 반영했다.
단, 개선을 측정하려면 평가 체계가 먼저 있어야 하므로 **평가셋은 앞쪽(Phase 2)** 에 둔다.

## 2. Phase 계획

### Phase 0. 하네스 & 결정 ✅
- 레포, CLAUDE.md, 기록 체계(docs/), 모델 분리(opusplan + 서브에이전트), 스킬 세팅 ← 이번에 완료
- 이 플랜 컨펌 + 기술스택 결정(아래 3절) → ADR 작성
- 데이터: Yule이 구글 드라이브에서 받아 `data/raw/` 에 배치 (프로젝트 구조가 잡힌 뒤)
- GitHub Actions CI(ruff + pytest), PR 템플릿

### Phase 1. 데이터 탐색 + 베이스라인 에이전트 (1차 목표) 🚧
"최소한으로 끝까지 한 번 돌리기"가 목적. 품질 고도화는 Phase 5~6에서.
1. 데이터 탐색 노트북(`notebooks/01_데이터탐색.ipynb`, 완료): 파일 형식 비율(hwp/hwpx/pdf), 페이지 수, 표 비중, 메타데이터 컬럼, 스캔 PDF 여부
2. 최소 파서: PDF는 PyMuPDF, HWP는 가장 간단한 후보 1개로 텍스트 추출 → `data/processed/*.jsonl` (doc_id, page/section, text, 메타데이터)
3. 고정 길이 청킹 + 로컬 임베딩 + Chroma 적재 (`scripts/build_index.py`). 메타데이터 CSV는 pandas로 로드해 문서 단위 조건 검색에 사용 (ADR 0003)
4. LangGraph 에이전트: `START → agent ⇄ tools → END`, 도구 2개 (`search_rfp`, `filter_rfps`)
5. CLI(`scripts/ask.py`)로 질의응답, 답변에 출처 인용
- 완료 기준: 샘플 질문 10개에 출처 포함 답변. 그래프 구조 그림 저장.

### Phase 2. 평가셋 & 평가 시스템 ⏳
1. 테스트셋 직접 구축 (목표 80문항, `eval/questions.v1.jsonl`, 버전 고정)
   - 유형: 단일문서 사실(예산, 마감, 기관) / 단일문서 서술(요구사항 요약) / 다중문서 조건검색 / 비교 / **답 없음(거절해야 함)** / 표 안의 정보
   - 생성: LLM으로 후보 질문 생성 → 직접 검수/수정 (생성 비율과 검수 기준도 기록)
2. 지표
   - 검색: Hit@k, MRR (정답 문서/청크 기준)
   - 답변: LLM-as-a-judge (정답성, 근거 충실도, 인용 정확도), 메타데이터 질문은 exact match. judge 모델은 답변 모델과 다른 계열로 (자기 편향 방지)
   - 운영: 지연(p50/p95), 질문당 토큰·비용
3. `scripts/evaluate.py` 한 번 실행으로 결과 표 + 실패 사례 저장, judge 프롬프트는 사람 채점 20건과 일치율 확인
- 완료 기준: baseline 점수표 = `EXP-001`

### Phase 3. 복합 에이전트 (2차 목표 핵심) ⏳
컨설턴트 업무 흐름(찾기 → 파악 → 비교 → 추천 → 준비)에 맞춘 도구/노드:

| 도구/노드 | 하는 일 |
| --- | --- |
| `search_rfp` | 본문 RAG 검색 (인용 포함) |
| `filter_rfps` | 메타데이터 조건 검색 (기관, 예산 범위, 마감일, 분야) |
| `summarize_rfp` | 구조화 요약 카드 (사업명/발주기관/예산/기간/제출방식/마감/자격요건/평가기준, JSON 스키마) |
| `extract_checklist` | 제출서류·자격요건 체크리스트 |
| `compare_rfps` | 2~3개 공고 비교표 |
| `match_client` | 고객사 프로필 ↔ 공고 적합도 점수 + 근거 (핵심 비즈니스 기능) |
| `deadline_board` | 마감 임박 공고 D-day 정리 |

- 그래프: `router → (범위 밖 응답 | 단순 메타 조회 | RAG 에이전트 루프) → 근거 검증 → 응답`
- 대화 메모리(checkpointer, thread_id), 도구 호출 횟수 상한
- 완료 기준: 기능별 시나리오 테스트 + 평가셋 재측정, 그래프 다이어그램

### Phase 4. 웹 백엔드 + 프론트 + AWS 배포 (멘토 2순위) ⏳
1. 채용공고 기술스택 조사 (`researcher`) → 백엔드 스택 확정
2. 백엔드: 채팅 API(SSE 스트리밍), 공고 목록/상세/요약 카드 API, 고객사 프로필 CRUD
3. 프론트: designmd.me/remix, styles.refero.design 참고 → 이미지 모델(gpt-image / nanobanana)로 시안 5개 → Yule 컨펌 → 구현. 이미지 생성은 Claude가 직접 못 하므로 프롬프트를 만들어 드리고 Yule이 생성(또는 API 키 제공)
4. 배포 (비용 최소, 방식은 이 Phase 시작 때 결정)
   - 상시 데모: 무료 호스팅 (프론트 Vercel, API는 Render / Fly.io / HF Spaces 중 하나, Chroma 파일을 이미지에 포함)
   - AWS: draw.io 아키텍처 다이어그램 + Terraform 코드는 반드시 작성. 실제 배포는 프리 티어로 짧게 올려 동작 확인·스크린샷 후 `terraform destroy` (포트폴리오 증빙용)
   - 어느 쪽이든 비용 알람(AWS Budgets) 먼저 설정
- 완료 기준: 공개 URL에서 채팅/요약/추천 동작, 인프라 다이어그램을 설명할 수 있음

### Phase 5. 파싱·청킹 고도화 (멘토 3순위) ⏳
- HWP/PDF 파서 후보를 샘플 10건(표 많은 것 포함)으로 비교 → 선택
- 청킹 실험: 고정 길이 vs 구조 기반(목차/조항) vs parent-child, 표는 마크다운 통째로, 청크 앞에 문서 메타 헤더
- 각 실험은 `EXP-NNN` 으로 기록, 평가셋으로 비교

### Phase 6. 검색(RAG) 고도화 (멘토 4순위) ⏳
- 임베딩 모델 비교, 하이브리드(BM25 + 벡터, 한국어 형태소 토크나이저), 리랭커, 쿼리 재작성
- 속도/비용까지 같이 비교

### Phase 7. 라우터 & 가드레일 (+ "Jev" 조사, 멘토 5순위) ⏳
- 먼저 "Jev"가 무엇인지 조사(`researcher`). Yule 설명("문장을 생성하지 않고 바로 로직을 실행하는 모델")과 가장 가까운 후보는 Meta의 **JEPA 계열(예: VL-JEPA)**: 토큰을 생성하지 않고 임베딩을 예측하는 비생성형 모델. 확인 전까지는 추정이며, 맞다면 "LLM을 부르지 않고 임베딩만으로 라우팅/가드 판단" 실험으로 연결
- 비교 대상: LLM 분류 노드(structured output) vs 임베딩 기반 시맨틱 라우터 vs (조사 결과 맞으면) Jev/JEPA 계열
- 라우터: 이 질문에 RAG가 필요한가 / 메타 조회로 충분한가 / 범위 밖인가
- 입력 가드: 범위 밖 질문, 프롬프트 인젝션 / 출력 가드: 근거 없는 답 차단, 인용 필수
- 라우터 정확도와 가드 오탐률을 평가셋에 추가해 측정

### Phase 8. 분산 처리 & 스트레스 테스트 ⏳
- 인덱싱을 큐 + 워커로 분리(문서 업로드 시 비동기 처리), API 수평 확장
- LLM rate limit 대응(재시도/백오프, 동시성 제한), 응답 캐시
- 부하 테스트: 로컬 docker-compose(API 여러 개 + 로드밸런서)로 먼저, 동시 사용자 늘려가며 RPS, p95, 에러율 측정. AWS에서는 짧게 1회
- 부하 테스트 중에는 LLM을 목(mock) 응답으로 바꿔 API 비용 없이 인프라 한계만 측정하는 모드 제공

### Phase 9. 마무리: 보고서 & 발표 ⏳
- `docs/` 기록(대화, ADR, 시행착오, 실험)을 바탕으로 보고서/발표 자료 작성
- 의사결정 근거 = ADR, 성능 개선 흐름 = EXP 표, 어려웠던 점 = trials

## 3. 기술스택 결정 항목 (함께 정할 것)

각 항목의 추천안은 Claude 의견이며 Yule이 정한다. 최신 모델·가격은 결정 시점에 다시 확인한다.

| # | 항목 | 후보 | 추천 | 이유 |
| --- | --- | --- | --- | --- |
| 1 | 언어/패키지 | Python 3.12 + uv | 그대로 | 팀 레포와 동일, LangGraph 생태계 |
| 2 | 에이전트 프레임워크 | (a) LangGraph StateGraph 직접 (b) LangChain `create_agent` (c) 둘 혼합 | (c) | 바깥은 StateGraph(라우터/가드 노드가 그림으로 보임), 도구 루프는 `create_agent` 를 서브그래프로 써서 구현량 절약 |
| 3 | LLM 호출 | (a) Gemini API 무료 티어 (b) OpenRouter 무료/저가 모델 (c) 로컬(Ollama, GPU 있으면) (d) Bedrock·OpenAI 등 유료 | 기본 (a), 비교용 (b) | 비용 0으로 시작. `init_chat_model` 로 교체 가능하게 짜서 모델 비교는 설정 파일만 바꿈. 무료 티어는 분당 호출 제한이 있어 평가 시 속도 조절·캐시 필요. 모델은 artificialanalysis 기준으로 결정 시점에 확인 |
| 4 | HWP 파싱 | (a) hwp-hwpx-parser (순수 파이썬, 표 추출) (b) pyhwp `hwp5html` (표 HTML 보존) (c) LibreOffice로 PDF 변환 후 PDF 파이프라인 재사용 (d) Upstage Document Parse 등 유료 API (e) olefile 직접 | Phase 1은 (a), Phase 5에서 (a)(b)(c) 비교 | 표 보존 여부가 핵심. (d)는 품질 좋지만 비용, HWP 지원 범위 확인 필요 |
| 5 | PDF 파싱 | (a) PyMuPDF / pymupdf4llm (b) Docling (c) 유료 API | (a) 시작, 표 많은 문서는 (b) 비교 | (a)는 빠르고 마크다운 출력, (b)는 표/레이아웃 강하지만 느림 |
| 6 | 임베딩 | (a) OpenAI text-embedding-3-small (b) BGE-M3 / KURE-v1 (한국어 특화, 로컬) (c) Gemini·Upstage 임베딩 | (b) 베이스라인 (로컬, 무료) → 필요하면 (a) 비교 | 100건 규모라 CPU로도 1회 인덱싱 가능. (a)는 싸고 간단, (b)는 한국어 검색 성능·무료지만 CPU에선 느림. (b)를 채택하면 배포 시 임베딩 서버(컨테이너 메모리/GPU) 비용이 생기므로 Phase 4 인프라와 같이 판단 |
| 7 | 벡터DB | (a) Chroma (로컬 파일) (b) PostgreSQL + pgvector (c) OpenSearch (d) Qdrant | **(a) 확정 제안** (ADR 0003) | 100건 규모엔 서버 DB가 필요 없음. 청크 검색은 Chroma(메타데이터 where 필터 지원), 문서 단위 조건 검색(예산·마감·기관)은 메타데이터 CSV를 pandas로 처리. 파일 하나라 배포도 쉬움. 사용자 데이터(고객사 프로필, 대화)가 늘어나면 그때 SQLite부터 검토 |
| 8 | 하이브리드/리랭크 | BM25(kiwipiepy) + 벡터 RRF, 리랭커 bge-reranker-v2-m3 / Cohere | Phase 6에서 실험 | 공고명·기관명 같은 고유명사는 BM25가 강함 |
| 9 | 평가/트레이싱 | (a) 직접 구현 judge (b) RAGAS (c) LangSmith (d) Langfuse | (a) + (b) 일부 지표, 트레이싱 (c) 무료 티어. judge도 무료 모델로, 평가 실행은 캐시해서 같은 질문 재호출 방지 | 지표를 직접 설계해야 보고서에 설명 가능, LangGraph 디버깅은 LangSmith가 가장 편함 |
| 10 | 백엔드 | (a) FastAPI 단일 (b) Spring Boot BFF + Python AI 서버 | 채용공고 조사 후 결정, 잠정 (a) | 멘토 조언대로 조사 먼저. (a)는 구현 빠름, (b)는 국내 공고 비중 높지만 서버 2개 |
| 11 | 프론트 | (a) Next.js + TS + Tailwind + shadcn/ui (b) Streamlit | (a) | 디자인 시안 반영 가능, 채용 시장 표준. Streamlit은 Phase 1~3 내부 데모용으로만 선택적 |
| 12 | 클라우드 | (a) AWS 풀스택: ECS Fargate(API, Chroma 파일 포함) + S3(원문·인덱스) + SQS/워커(인덱싱) + Amplify 또는 S3+CloudFront(프론트) + Secrets Manager + CloudWatch (b) AWS 경량: App Runner/Lambda (c) Vercel + Supabase + Render | 설계는 (a), 상시 운영은 무료 호스팅 (Phase 4에서 결정) | 비용 최소 원칙. AWS는 다이어그램+Terraform으로 이해도를 보여주고 실제 배포는 짧게. 벡터DB가 Chroma라 RDS 없이 ECS 컨테이너 + S3(Chroma 파일)로 단순화 가능 |
| 13 | IaC | (a) Terraform (b) AWS CDK (Python) (c) 콘솔 수동 | (a) | 다이어그램과 코드가 1:1로 대응, 채용공고 빈도 높음, 다 내리고 다시 올리기 쉬움(비용 관리) |
| 14 | 부하 테스트 | (a) Locust (b) k6 | (a) | Python으로 시나리오 작성 |

## 4. 하네스 (Phase 0 결과)

- `CLAUDE.md`: 규칙(플랜 컨펌 전 구현 금지, 스택은 함께 결정, 기록 의무), 모델 분리, 작업 방식
- `.claude/settings.json`: `"model": "opusplan"` (plan mode에서는 Opus, 실행 시 Sonnet 자동 전환), `.env` 읽기 차단
- 서브에이전트 `.claude/agents/`: `planner`(Opus), `reviewer`(Opus), `implementer`(Sonnet), `researcher`(Sonnet)
- 스킬 `.claude/skills/`
  - 직접 작성: `devlog`(대화/ADR/시행착오 기록), `phase-gate`(계획→컨펌→구현→리뷰 게이트), `experiment-log`(실험 기록)
  - 공식 LangChain 스킬(MIT): `langgraph-fundamentals`, `langgraph-persistence`, `langgraph-human-in-the-loop`, `langchain-fundamentals`, `langchain-middleware`, `langchain-rag`
- 기록 폴더 `docs/`: conversations, decisions, trials, experiments, architecture, research

## 5. 리스크

| 리스크 | 대응 |
| --- | --- |
| HWP 파싱 품질(특히 표) | Phase 1은 텍스트만, Phase 5에서 비교 실험. 최악의 경우 LibreOffice→PDF 변환 |
| 스캔 PDF(이미지) 존재 | Phase 1 탐색에서 비율 확인, 있으면 OCR 옵션 추가 검토 |
| AWS 비용 | 상시 운영은 무료 호스팅, AWS는 Terraform으로 짧게 올리고 destroy, Budgets 알람 |
| LLM 무료 티어 호출 제한 | 평가 결과 캐시, 동시성 제한·백오프, 평가셋 일부만 빠르게 도는 모드 |
| 무료 티어 데이터 정책 | 공개 RFP라 문제 적지만, 고객사 프로필 등은 가상 데이터만 사용 |
| 범위 과다(혼자 9개 Phase) | Phase 1~4를 필수, 5~8은 시간에 맞춰 깊이 조절. 각 Phase는 동작하는 상태로 끝냄 |
| 평가셋 편향(LLM 생성) | 직접 검수, 유형별 비율 고정, 답 없음 문항 포함 |

## 6. Yule에게 확인할 것

(v0.1 질문 중 레포 이름, 일정, 예산 방향, 데이터 위치, Jev, Docker는 답변 받음 → 8절)

1. Gemini API 무료 키를 쓸 수 있는지 (기본 LLM 후보). 다른 걸 원하면 알려주기
2. 3절 기술스택 추천안 중 바꾸고 싶은 것
3. 이 플랜 v0.2로 Phase 1 시작해도 되는지 (컨펌)

## 7. 셀프 리뷰 (reviewer 관점으로 초안 점검 후 반영한 것)

| 지적 | 반영 |
| --- | --- |
| 멘토 우선순위대로면 평가(4순위)가 뒤로 밀려, 파싱/검색 개선 효과를 측정할 수 없음 | 평가셋을 Phase 2로 당김. 이후 모든 개선은 EXP 기록으로 비교 |
| 파싱(3순위)을 먼저 완벽히 하려다 1순위인 에이전트가 늦어질 위험 | Phase 1을 "최소 파싱으로 끝까지 한 번" 으로 제한, 고도화는 Phase 5 |
| 클라우드(2순위)가 마지막에 몰리면 배포 리스크를 늦게 발견 | 웹+AWS 배포를 Phase 4(복합 에이전트 직후)로 배치 |
| (v0.1) pgvector 추천은 로컬 Docker 전제 | v0.2에서 Chroma로 변경되어 해소 |
| 로컬 임베딩(BGE-M3/KURE) 채택 시 배포 비용 누락 | 임베딩 항목에 배포 비용 메모 추가 |
| LLM-as-judge 자기 편향 | judge 모델을 다른 계열로, 사람 채점 20건과 일치율 확인 |
| CI 없음 | Phase 0에 GitHub Actions(ruff+pytest) 추가 |
| 프론트 시안의 이미지 생성은 Claude가 직접 불가 | Yule이 생성하는 흐름으로 명시 |
| 일정 정보가 없어 Phase별 기간을 못 정함 | 마감 없음 확인 → 순서만 유지 |
| "Jev" 의미 불명확 | 해석을 명시하고 질문 5번으로 확인 |

## 8. 변경 내역

### v0.2 (2026-11-11, Yule 답변 반영)
- 레포: `yulesn/rfp-agent-yule` (Yule이 생성)
- 마감일 없음 → Phase 기간 배분 제거
- API/AWS 최소 사용 → LLM 기본값을 무료 티어로, 임베딩을 로컬 모델로, 배포는 무료 호스팅 + AWS는 설계/짧은 검증
- 벡터DB: pgvector 대신 Chroma만 사용 (Yule 제안 수용, ADR 0003)
- 데이터: 구글 드라이브 → 구조 확정 후 Yule이 다운로드
- Jev: Yule도 정확히 모름 → Phase 7에서 조사, 현재 추정은 JEPA 계열

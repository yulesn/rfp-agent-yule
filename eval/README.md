# 평가셋

Phase 2에서 목표 80문항을 `eval/questions.v1.jsonl` 로 만든다. 버전이 정해지면 파일을 고치지 않고 새 버전(`v2`)으로 만든다.

## 형식 (jsonl, 한 줄에 한 문항)

| 필드 | 설명 |
| --- | --- |
| `id` | 문항 ID (예: `q001`) |
| `question` | 질문 |
| `answer` | 정답(기준 답변). 답 없음 유형은 "문서에 근거 없음" 같은 거절 기준 |
| `answer_doc_ids` | 정답 근거 문서의 doc_id 리스트 (답 없음이면 빈 리스트) |
| `type` | 아래 유형 중 하나 |

## 유형 (PLAN Phase 2)

- `single_fact`: 단일문서 사실 (예산, 마감, 기관)
- `single_summary`: 단일문서 서술 (요구사항 요약)
- `multi_filter`: 다중문서 조건검색
- `compare`: 비교
- `no_answer`: 답 없음 (거절해야 함)
- `table`: 표 안의 정보

## 현재 파일

`questions.v1.jsonl` 의 2줄은 형식을 보여주는 **예시(EXAMPLE)** 이며 실제 문항이 아닙니다. 실제 문항을 만들 때 삭제합니다.

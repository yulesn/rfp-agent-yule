---
name: devlog
description: Yule과의 논의, 기술 결정(ADR), 시행착오를 docs/ 에 기록할 때 사용. 의미 있는 대화가 끝났을 때, 결정이 확정됐을 때, 에러를 해결했거나 시도가 실패했을 때 반드시 호출.
---

# devlog — 대화/결정/시행착오 기록

## 1) 대화 로그 → `docs/conversations/YYYY-MM-DD-주제.md`
같은 날 같은 주제면 기존 파일에 이어 쓴다.

```markdown
# YYYY-MM-DD 주제
## 배경
## 논의 (Yule의 질문/요청 → Claude 제안 → Yule 피드백 순으로 요약. 대화 원문은 인용하지 않는다)
## 합의/결정 (→ 관련 ADR 링크)
## 미결 질문 / 다음 할 일
```

## 2) 결정 기록(ADR) → `docs/decisions/NNNN-제목.md`
번호는 기존 최대값 + 1. 상태: 제안됨 → 확정됨 → (대체됨: NNNN).

```markdown
# NNNN. 제목
- 상태: 제안됨 | 확정됨 | 대체됨
- 날짜: YYYY-MM-DD
- 결정자: Yule (+ Claude 제안)
## 맥락
## 후보 비교 (표: 후보 / 장점 / 단점 / 비용)
## 결정
## 근거
## 영향 / 되돌리는 방법
```

## 3) 시행착오 → `docs/trials/YYYY-MM-DD-주제.md`

```markdown
# 주제
- 날짜 / Phase / 관련 파일
## 증상 (에러 메시지 원문 포함)
## 시도한 것 (실패한 것도 순서대로, 왜 실패했는지)
## 원인
## 해결
## 배운 점 (발표에 쓸 만한 한 줄)
```

작성 후 `docs/PLAN.md` 의 Phase 상태가 바뀌었으면 함께 갱신한다.

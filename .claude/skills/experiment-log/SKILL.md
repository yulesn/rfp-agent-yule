---
name: experiment-log
description: 파싱/청킹/임베딩/검색/프롬프트/모델 설정을 바꿔 성능을 비교하는 실험을 하거나 결과를 기록할 때 사용.
---

# experiment-log

1. 실험마다 설정 파일을 만든다: `configs/exp_NNN_설명.yaml` (기준 설정 복사 후 한 가지씩만 바꾼다).
2. 같은 평가셋(`eval/` 의 버전 고정)으로 기준 설정과 비교한다.
3. `docs/experiments/EXP-NNN-제목.md` 에 기록:

```markdown
# EXP-NNN 제목
- 날짜 / 설정 파일 / 평가셋 버전 / 비교 대상(baseline)
## 가설
## 바꾼 것 (한 가지)
## 결과
| 지표 | baseline | 이번 실험 |
| Hit@5 / MRR / 정답률(judge) / 충실도 / p95 지연 / 질문당 비용 | | |
## 해석 (왜 올랐/떨어졌나, 실패 사례 2~3개)
## 결론 (채택/기각) → 채택 시 ADR 링크
```

4. `docs/experiments/README.md` 의 실험 목록 표에 한 줄 추가한다.

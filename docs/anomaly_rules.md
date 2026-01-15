# Rule 기반 이상 판단 로직

본 프로젝트에서는 AI 모델 이전 단계에서
설비 이상을 빠르게 판단하기 위한
Rule 기반 이상 판단 로직을 적용했다.

## 1. Physical Violation
- 의미: 설비의 물리적 한계 또는 안전 한계 위반
- 예: 음수 회전수, 불가능한 온도 범위
- 목적: 센서 오류 또는 즉시 위험 상황 감지

## 2. Spec Violation (Statistical Approximation)
- 실제 제품 품질 규격이 제공되지 않아
  데이터 분포 기반 가상 Spec Limit 설정
- 기준: mean ± 2σ
- 목적: 품질 이상 가능성 사전 감지

## 3. Rule Anomaly (Operational Limit)
- 기준: mean ± 3σ 또는 IQR 기반
- 목적: 설비 및 공정 운영 이상 감지

Rule 기반 판단은 AI 모델의 대체가 아닌,
AI 결과의 해석과 신뢰도를 높이기 위한
1차 안전 장치로 설계되었다.
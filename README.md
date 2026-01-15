# AI 기반 스마트팩토리 예지보전 대시보드

## 1. 프로젝트 개요
본 프로젝트는 제조 설비에서 발생하는 센서, 설비 로그, 생산 및 품질 데이터를 통합하여  
설비 이상 탐지 및 고장 시점(RUL)을 예측하고,  
그 결과를 **현장 및 관리자의 의사결정을 지원하는 KPI 형태로 제공하는 예지보전 시스템**입니다.

단순히 고장 여부를 예측하는 데 그치지 않고,  
AI 결과를 생산·품질·비용 관점의 KPI로 확장하여  
“언제 멈출 것인가, 언제 정비할 것인가”에 대한 판단 근거를 제공하는 것을 목표로 합니다.

---

## 2. 프로젝트 목표
- 설비 이상 상태의 조기 감지
- 고장 시점 및 잔여 운전 시간(RUL) 예측
- AI 예측 결과를 KPI로 변환하여 대시보드에 시각화
- 현장, 품질, 관리자가 즉시 의사결정할 수 있는 구조 설계

---

## 3. 전체 시스템 아키텍처
본 시스템은 다음 흐름으로 구성됩니다.

Sensor / PLC / Production / Quality Data  
→ 데이터 전처리 및 Feature Engineering  
→ 이상치 탐지 및 RUL 예측 AI  
→ KPI 계산 및 의사결정 로직  
→ 대시보드 시각화

![Architecture](docs/architecture-diagram.png)

---

## 4. 기술 스택
- **Frontend**: React, Chart.js
- **Backend**: Spring Boot, JPA
- **AI / Analytics**: Python, PyTorch, Scikit-learn
- **DB**: MySQL
- **Collaboration**: Git, GitHub

---

## 5. 데이터 소스 구성
본 프로젝트는 실제 제조 현장을 가정하여 데이터 소스를 다음과 같이 구성했습니다.

- **Sensor Data**: 온도, 진동, 전류, RPM 등 실시간 시계열 데이터  
- **PLC / Machine Log**: 설비 on/off, 에러 코드, 재시작, 수동 모드 전환 로그  
- **Production DB (MES/ERP)**: 공정 정보, 생산량, 작업 이력, 설비 ID  
- **Quality Inspection Data**: 불량 여부, 불량 유형, 치수 오차

각 데이터는 단독이 아닌 **상호 보완적으로 활용**되어  
설비 상태를 공정 맥락까지 고려한 예지보전을 가능하게 합니다.

---


## 6. AI 기능 구성

### 6.1 설비 상태 판단 (Anomaly Detection + Classification)
- Rule 기반 임계치(IQR, Threshold) 이상 감지
- Isolation Forest, LOF 기반 비지도 이상치 탐지
- 다중 모델 결과를 통합한 Anomaly Score 산출
- 점수 및 현장 기준 임계치에 따라
  설비 상태를 정상 / 주의 / 위험으로 분류

### 6.2 고장 시점 예측 (Predictive Maintenance)
- 회귀 모델 및 LSTM 기반 RUL 예측
- PyTorch 학습 → ONNX 변환 → Spring Boot 추론 구조
- 잔여 운전 가능 시간 산출

### 6.3 KPI 확장 및 의사결정 로직
AI 예측 결과는 다음과 같이 KPI로 확장됩니다.
- 설비 이상 위험도
- 예상 불량률 증가
- 생산 손실 및 비용 영향

AI는 판단 근거를 제공하며,  
최종 결정은 현장과 관리자가 수행하는 **Decision Support System**으로 설계했습니다.

---


## 7. 대시보드 주요 기능
- 설비 상태 KPI 카드 (위험도, RUL)
- 이상 알람 및 추이 시각화
- 공정/설비별 상태 비교
- 운영 판단을 위한 권장 조치 표시

---

## 8. 협업을 고려한 개발 방식
- 역할 분리를 고려한 모듈 구조 설계
- API 명세 기반 Frontend–Backend 연동
- Git Feature 브랜치 전략 적용

---


## 9. 향후 확장 계획
- 실시간 스트리밍 데이터 연동
- 설비별 맞춤 임계치 자동 학습
- 품질 불량 예측 모델 고도화
- 3D 디지털 트윈 시각화 연계








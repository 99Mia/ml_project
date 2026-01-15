# Sensor Data
Predictive Maintenance Dataset (AI4I 2020)  - 출처 kaggle

    "sensor_prod_udi",          # 제품 식별자
    "sensor_prod_id",           # 제품 ID
    "sensor_prod_type",         # 제품 타입

    "sensor_air_temp_k",        # 공기 온도
    "sensor_process_temp_k",    # 공정 온도
    "sensor_rot_speed_rpm",     # 회전 속도
    "sensor_torque_nm",         # 토크
    "sensor_tool_wear_min",     # 공구 마모

    "sensor_flag_machine_failure",  # 설비 고장 여부
    "sensor_flag_twf",              # tool wear failure
    "sensor_flag_hdf",              # heat dissipation failure
    "sensor_flag_pwf",              # power failure
    "sensor_flag_osf",              # other sensor failure
    "sensor_flag_rnf"               # random failure 

위의 데이터는 실제 특정 산업 설비라기보다는 산업용 장비/머신을 시뮬레이터한 데이터이다
- 제조 공정용 머신/공작기계 시뮬레이션 데이터
- Machine ID, Product ID, Type 컬럼으로 장비와 제품을 구분한다. 
- 각 장비에서 발생할 수 있는 센서 값 (온도, 토크, 회전수, Tool  wear 등)을 기록한다

- 고장 발생 유형(TWF ..) 를 레이블에 포함한다 --> 우리는 쓰면 안됨. 예측모델을 만들거니까
--> Failure 컬럼은 이미 고장 여부를 알려주는 정보라서 쓰면 안됨


# 데이터 특성, 데이터 특징 (모델 선택 이유)
- 다변량 센서 데이터
- 연속형 + 범주형 혼합
- 고장/ 이상 데이터 극소수
- 물리적으로 상관된 변수가 많다
- 노이즈가 존재한다
- 문제의 성격 : (정형 데이터 + 이상치 중심 문제)
"테이블 형태의 센서 데이터이며, 대부분 정상이고 소수의 이상 이벤트를 탐지하는 것이 핵심 과제"

--> 데이터의 핵심 목적이 정상분류가 아니라 드물게 발생하는 이상을 찾아내는 것이 문제
정상 데이터 : 95% 이상
고장/이상 : 5% 이하
모델의 목적은 고장/이상(확률 이벤트)를 놓치지 않는 것 
--> 이상치 중심 문제로 접근하면
- Recall, F1, AUC 중심 평가
- Threshold 기반 판단
- Unsupercised / Semi-supervised 활용




# lr/bact-size
- LR 과 Batch size는 데이터의 노이즈, 구조, 불균형을 보고 정하며, 프로젝트에서는 그 선택 이유를
문서와 실험으로 증명하는 것이 핵심이다

- 스마트팩토리 데이터는 거의 항상 작은 batch + 작은 lr
- 노이즈 많음(센서, 시계열) -> batch-size 작게 (16~32) -> lr 작게 
--> 평균 내면 중요한 이상 신호가 사라짐

실 서비스(최종 성능)
--> SGD(+Momentum), batch 큼, lr scheduler 필수 
프로젝트에서는 하이퍼파라미터 선택 근거를 명시적으로 보여줘야한다

"본 프로젝트의 데이터는 센서 기반 시계열 데이터로 노이즈가 많고, 고장 데이터 비율이
매우 낮다. 따라서 작은 batch size 를 사용해 이상 패턴이 평균화되는 것을 방지했고,
Adam 옵티마이저를 사용해 학습 안정성을 확보했다"
질문 : 왜 batch32, lr 0.001을 썼는지?
답 : "센서 데이터 특성 상 gradient noise 가 크기 때문에 작은 batch가 유리했고,
Adam은 파라미터별 학습률 조절로 안정적인 수렴을 보여 실험 결과 가장 좋은 validation 성능을 보였습니다."

# sensor_tool_wear_min
특정 시간 구간(window)안에서 공구 마모 센서 값의 최소값이다
-> 즉, 가공중 가장 "덜 마모된 순간"의 측정치이다
그 순간의 raw 요약값이지, 추세는 아니다.

어디에 쓰이는가?
1. 공정 상태 확인 (단기 상태 feature)
현재 공정에서
- 센서가 안정적인지
- 기준 수준 (baseline)이 유지 되는지 
빠르게 판단하는 용도이다.
min이 갑자기 변하면: 
- 센서 드리프트
- 장비 세팅 변경
- 측정 오류 가능성

2. 이상 탐지에서 "즉각 반응"용
min_ewma 는 느리게 반응하지만 sensor_tool_wear_min은 즉각 반응합니다.
그래서 
- 공구깨짐
- 센서 접촉 불량
- 급격한 절삭 조건 변화 같은 급성 이벤트 감지에 유리하다.
--> ewma 만 쓰면 이런 이벤트를 놓칠 수 있다

3. ewma 계산의 입력값
min 이 없으면 min_ewma 도 존재 불가하다
ewma 는 원본 신호가 있어야 의미가 있다. 

4. feature 간 관계를 모델이 학습하게 할 때
- sensor_tool_wear_min (현재 상태)
- sensor_tool_wear_min_ewma (장기 추세)
- (sensor_tool_wear_min) - (sensor_tool_wear_min_ewma) = 편차
--> 현재 값이 정상 범위인지, 추세 대비 얼마나 벗어났는지 모델이 상황을 입체적으로 이해



# sensor_tool_wear_min_ewma
***sensor 에 들어있는 tool_wear는 실시간 이상탐지에 사용된다
--> 의미 : 최소값을 EWMA로 스무딩
--> 사용 목적 
: 추세(trend)감지, 노이즈 제거, 갑작스러운 변화보다 지속적 변화에 민감
: 공구 마모 상태를 안정적으로 추적하고, 이상을 조기에 감지하기 위해 쓰인다
- min -> 이상하게 튄 큰 값(순간 피크)를 배제
- ewma -> 그 최소값들의 장기 추세만 부드럽게 반영
** --> 그래서 실제 마모 진행 상태만 남긴다

실제로 어디에 쓰이나? 
1. 공구 교체 시점 예측
sensor_tool_wear_min_ewma  가 특정 임계값(threshold)를 넘으면 "곧 공구 교체 필요" 판단
머신러닝 모델에서는:
- Remaining Useful Life (RUL)
- Tool life prediction (공구 기대 수명)
- Failure prediction (고장 예측)
의 핵심 입력 feature 로 사용된다

2. 이상 탐지 (anomaly detection)
- EWMA 추세 대비 갑자기 값이 급상승/급하락하면
- 공구 파손, 센서 이상, 절삭 조건 급변을 감지

3. 모델 안정성 향상용 feature
원본 tool_wear 센서 값:
- 노이즈 많음, 분산 큼 -> 그대로 쓰면 모델이 흔들림
min_ewma :
- 분산 감소, 장기 추세만 반영 -> 모델 성능 & 일반화 개선

한 문장으로 정리하면, sensor_tool_wear_min_ewma 는 공구 마모의 "기본 진행 상태"를 노이즈 없이 추적해서 고장 예측,교체 타이밍 판단에 쓰이는 핵심 신호이다.


# 용어 EWMA
EWMA는 지수 가중 이동평균이라고 부른다. 쉽게 말하면 최근 값에 더 큰 비중을 주고, 과거 값은 점점 덜 반영하는 평균이다.
특징: 노이즈를 줄이고 추세를 파악하기 좋다
갑작스러운 spike(이상치)보다 지속적인 변화에 민감하다
실시간 센서 데이터 모니터링에 적합하다
현재 EWMA = a x 현재값 + (1-a) x 이전 EWMA
- 여기서 알파 a 가 크면 -> 최근 값에 매우 민감 (빠른 반응)
- 알파 a 가 작으면 -> 더 부드러운 평균 (노이즈 제거에 강함)
즉, 노이즈 감소 & 추세 파악에 좋다.
- 센서 데이터나 실시간 측정값은 흔들림(노이즈)가 많다
- 단순 평균보다 EWMA 는 불필요한 흔들림을 줄여 전체적인 상승, 하락 추세를 더 명확하게 보여준다
그래프에서 보면 들쭉날쭉한 원본 데이터 위에 부드러운 곡선이 하나 그려지는 느낌이다
실시간 데이터 처리에 매우 적합하고, 계산량이 작아서 실시간 스트리밍 데이터에 최적이다.
주로 쓰이는 곳: 
- 온도/습도/압력 센서
- 서버 cpu 사용률
- 네트워크 트래픽
- 금융 가격, 변동성 추적
한 마디로, ewma 는 "최근을 더 믿고, 오래된 과거는 잊어가는 똑똑한 평균이다"



# sensor_tool_wear_min_std
--> 의미 : 최소값의 표준편차 
--> 사용 목적 : 변동성(volatility)측정, 갑작스러운 진동/불규칙 변화 감지
즉, 일정 시간 동안 측정된 '최소 마모값'이 얼마나 흔들렸는지 를 나타내는 feature 이다
값이 작으면 안정적으로 최소 마모가 유지되고 있는 것이고, 값이 크면 최소값조차 불규칙하게 흔들리는 것이라고 볼 수있다.

사용 목적 :
1. 공정 안정성 모니터링
--> 일반적이 Tool Wear 지표는 평균이나 최대값을 보는 경우가 많지만, 최소값 변동도 중요하다.
- 최소값이 불안정하면, 공구가 일정 구간에서 예상보다 빨리 마모되거나 진동이 발생할 수 있다
- 따라서 sensor_tool_wear_min_std는 공정 변동성 지표로 활용된다
2. 조기 경보 
- 표준편차가 크게 증가하면 갑작스러운 진동, 충격, 불균형 부하가 발생했다는 신호이다.
- 공구 손상, 기계 베어링 문제, 냉각 시스템 이상 등을 조기에 알 수 있다
3. 품질 예측 및 유지보수
- Tool Wear 변동성이 높으면 제품 표면 품질이나 치수 정확도가 떨어진다. 
- 변동성 지표를 kpi나 ai 모델 입력으로 넣으면 불량률 예측, 최적 교체 시점 결정에 활용 가능

모델에서 활용 :
sensor_tool_wear_min_std는 보통 예지보전과 이상탐지 ai 모델에서 feature로 사용된다



# sensor_tool_wear_min_mean
window 내 최소 tool wear 평균 
목적: 안정성 기준

# sensor_tool_wear_min_max_diff
min max 차이
목적 : 급격한 진동 감지

# sensor_tool_wear_rate
이전 시간 대비 증가율
목적 : 마모 속도 추적, RUL 예측

# sensor_torque_std
torque 변동성
목적: 진동/부하 이상 감지


# sensor_torque_mean
torque 평균 
목적 : 공정 상태 기준

# sensor_rot_speed_rpm
rpm 변동성 
목적 : 모터/기계 불안정 탐지

# torque_rpm_ratio
torque/rpm 비율
목적 : 효율성, 부하 이상 감지

# sensor_air_temp_k_std
변동성
목적 : 냉각 성능, 공정 안정성 확인

# sensor_process_temp_k_std
변동성
목적 : 냉각 성능 , 공정 안정성 확인

# sensor_delta_temp
process_temp - air_temp
목적 : 내부 과열 신호, heat dissipation failure 판단

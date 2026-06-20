# 공정능력분석, 통계적공정관리 (SPC) 대시보드
- 2026-1 스마트제조 프로젝트 과제2
- **공정능력분석**과 **통계적공정관리(SPC)** 를 수행하는 Streamlit 웹앱.
- 데이터가 바뀌면 자동으로 재계산하며, 대시보드로 공정 상황을 한눈에 판단할 수 있다.

## 주요 기능

- **공정능력분석**
    - 정규성 검정(Shapiro–Wilk, Q-Q plot)
    - Cp / Cpk / Pp / Ppk히스토그램(규격선·지수 주석)
    - 공정능력 0~4등급 판정, 예상 불량률(ppm)
- **통계적공정관리**
    - 계량형 3종(Xbar-R / Xbar-s / I-MR)
    - 계수형 4종(NP / P / C / U)
  UCL·CL·LCL 표시, 관리이탈점(Nelson 규칙 1) 강조
- **관리도 재작성**
    - Nelson 규칙 1 이탈 부분군을 관리상태가 될 때까지 반복 제거하고 한계를 재계산
    - 초기/재작성 관리도와 한계를 전후 비교
- **데이터 변경 대응**: 데이터를 업로드할 수 있으며, 새로운 데이터에 대해서 자동 재계산

## 입력 데이터 형식

분석 유형을 먼저 선택한 뒤, 그에 맞는 형식의 파일을 업로드한다.

- **계량형**: 각 행이 하나의 부분군, 각 열이 반복측정값. 업로드 시 행 순서대로 부분군 ID(1, 2, 3…)를 부여해 내부적으로 변환한다.
- **계수형**: `[부분군, 표본크기, 측정값]` 순서의 3개 열.

## 모듈 구조
```
spc-app/
├── app.py              # Streamlit UI
├── config.py           # 색상 토큰, 신호등·등급 판정, 규격 기본값, 데이터 경로
├── constants.py        # 불편화 상수 (공정능력용·관리도용)
├── data_loader.py      # 업로드 읽기, 계량형 Long 변환, 계수형 정리, 샘플 로더
├── capability.py       # 공정능력분석 계산, 시각화
├── control_chart.py    # 관리도 생성(계량형·계수형), 시각화, Nelson 규칙 1
├── rules.py            # 관리이탈 판정 + 관리도 재작성
├── analytics.py        # 대시보드 KPI 조립
│
├── data/               # 불편화 상수 CSV
├── .streamlit/
│   └── config.toml     # 테마
├── requirements.txt
└── README.md
```

**의존성 흐름**: `config` → `constants` → `capability` / `control_chart` → `rules` / `analytics` → `app`
(`data_loader`는 `config`에만 의존)

## 탭 구성

| 탭 | 계량형 | 계수형 |
|---|---|---|
| 개요 | 요약 띠 + 신호등 + KPI 카드 | 요약 띠 + 상태 + 지표 |
| 공정능력분석 | 히스토그램 · 정규성 · Q–Q plot | — |
| 통계적공정관리 | 관리도 + 재작성(전후 비교) | 관리도 |
| 데이터 | 원본 · 부분군 통계 · 다운로드 | 원본 · 다운로드 |

공정능력분석은 계량형에만 적용된다(계수형은 규격·정규분포 가정이 성립하지 않음).

## 배포


## 데이터

- `data/measurements.csv` — 계량형 샘플 (25 부분군 × 5 측정점, 두께)
- `data/defects.csv` — 계수형 샘플 (25 로트, 불량수)
- `data/unbiased_capability_analysis.csv` — 공정능력 불편화 상수 (d2/d3/d4)
- `data/unbiased_control_chart.csv` — 관리도 불편화 상수 (A2/A3/d2/D3/D4/B3/B4)
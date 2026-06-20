"""
데이터 입출력 및 형식 변환
계량형: 각 행=부분군(A형식) -> 행 순서 ID 부여 후 Long 변환
계수형: [부분군, 표본크기, 측정값] 순서로 사용
"""
import pandas as pd

import config


def read_uploaded(uploaded_file):
    name = uploaded_file.name.lower()
    if name.endswith((".xlsx", ".xls")):
        return pd.read_excel(uploaded_file)
    return pd.read_csv(uploaded_file)


def variable_wide_to_long(df, sg_name="subgroup", var_name="value"):
    df = df.copy()
    df[sg_name] = range(1, len(df) + 1)
    long = df.melt(id_vars=sg_name, value_name=var_name)
    return long[[sg_name, var_name]].sort_values(sg_name).reset_index(drop=True)


def prepare_variable(df):
    """업로드된 계량형 원본(행=부분군) → process_capability/generate_value_chart 입력 형식."""
    return variable_wide_to_long(df)


def prepare_count(df):
    """계수형 원본 → [부분군, 표본크기, 측정값] 3컬럼 (앞 3개 열 순서 사용)."""
    cols = list(df.columns[:3])
    out = df[cols].dropna().copy()
    return out


def load_sample_variable():
    return pd.read_csv(config.SAMPLE_MEASUREMENTS)


def load_sample_count():
    return pd.read_csv(config.SAMPLE_DEFECTS)
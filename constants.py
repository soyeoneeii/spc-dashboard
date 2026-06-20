# 불편화 상수 계산을 위한 모듈

import numpy as np
import pandas as pd
from scipy.special import gamma

import config

_D_CAP = pd.read_csv(config.UNBIASED_CAPABILITY_CSV)   # N, d2, d3, d4
_D_CTRL = pd.read_csv(config.UNBIASED_CONTROL_CSV)     # m, A2, A3, d2, D3, D4, B3, B4


def calc_unbiased_const(const_name, n):
    """공정능력 분석용 불편화 상수 계산"""
    d_table = _D_CAP

    if const_name == "d2":
        if n < 51:
            return d_table["d2"][n - 2]
        return 3.4873 + 0.0250141 * n - 0.00009823 * n ** 2

    elif const_name == "d3":
        if n < 26:
            return d_table["d3"][n - 2]
        return 0.80818 - 0.051871 * n + 0.00005098 * n ** 2 - 0.00000019 * n ** 3

    elif const_name == "d4":
        if n < 26:
            return d_table["d4"][n - 2]
        return 2.88606 + 0.051313 * n - 0.00049243 * n ** 2 + 0.00000188 * n ** 3

    elif const_name == "c2":
        return (np.sqrt(2) / np.sqrt(n)) * (gamma(n / 2) / gamma((n - 1) / 2))

    elif const_name == "c3":
        c2 = (np.sqrt(2) / np.sqrt(n)) * (gamma(n / 2) / gamma((n - 1) / 2))
        return np.sqrt((n - 1) / n - c2 ** 2)

    elif const_name == "c4":
        return (np.sqrt(2) / np.sqrt(n - 1)) * (gamma(n / 2) / gamma((n - 1) / 2))

    return None


def unbiased_coefficient(coef_name, m):
    """관리도용 불편화 상수 계산"""
    d_table = _D_CTRL
    if (coef_name in d_table.columns[1:]) and 2 <= m <= 25:
        return d_table[coef_name][m - 2]
    return d_table[coef_name].iloc[-1]
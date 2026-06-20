# rules.py — 관리이탈 판정 및 관리도 재작성

import pandas as pd

from control_chart import generate_value_chart, nelson_rule_1

MAX_ITER = 20


def ooc_subgroups(chart):
    """Nelson 규칙 1 이탈 부분군의 인덱스 리스트."""
    return nelson_rule_1(chart).index.tolist()


def recreate_value_chart(data, chart_type="Xbar-R", window=3):
    """
    이상치 제거 후 관리도 재작성 (반복).
    각 회차에서 이탈 부분군을 모두 제거하고 한계를 재계산하며,
    이탈점이 없어질 때까지 반복한다.
    반환: 초기/최종 관리도, 회차별 제거 이력, 전후 한계 비교.
    """
    sg_name, var_name = data.columns

    charts_initial = generate_value_chart(data, chart_type=chart_type, window=window)
    init_chart = charts_initial[0]

    history = []          # 회차별 제거된 부분군 리스트
    removed_all = []      # 누적 제거 부분군
    df_work = data.copy()

    for _ in range(MAX_ITER):
        charts = generate_value_chart(df_work, chart_type=chart_type, window=window)
        ooc = ooc_subgroups(charts[0])
        if not ooc:
            break
        history.append(ooc)
        removed_all.extend(ooc)
        df_work = df_work[~df_work[sg_name].isin(ooc)].copy()

    charts_revised = generate_value_chart(df_work, chart_type=chart_type, window=window)
    rev_chart = charts_revised[0]

    changed = len(removed_all) > 0

    return {
        "charts_initial": charts_initial,
        "charts_revised": charts_revised if changed else None,
        "history": history,                    
        "removed_lots": removed_all,           
        "rounds": len(history),               
        "removed": len(data) - len(df_work),  
        "initial_limits": (init_chart["UCL"].iloc[0], init_chart["LCL"].iloc[0]),
        "revised_limits": (rev_chart["UCL"].iloc[0], rev_chart["LCL"].iloc[0]) if changed else None,
    }
# 관리도 생성 및 시각화

import numpy as np
import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots

from constants import unbiased_coefficient
import config


def generate_value_chart(data, chart_type="Xbar-R", window=3):
    """계량형 (Xbar-R, Xbar-s, I-MR)"""
    sg_name, var_name = data.columns

    if chart_type == "Xbar-R":
        sg = pd.DataFrame()
        sg["Xbar"] = data.groupby(sg_name)[var_name].mean()
        sg["R"] = data.groupby(sg_name)[var_name].max() - data.groupby(sg_name)[var_name].min()
        sg["n_i"] = data[sg_name].value_counts()

        Xbar_bar = sg["Xbar"].mean()
        R_bar = sg["R"].mean()
        m = sg["n_i"].mode()

        A2 = unbiased_coefficient("A2", m[0])
        D3 = unbiased_coefficient("D3", m[0])
        D4 = unbiased_coefficient("D4", m[0])

        Xbar_chart = pd.DataFrame()
        Xbar_chart["point"] = sg["Xbar"]
        Xbar_chart["CL"] = Xbar_bar
        Xbar_chart["LCL"] = Xbar_bar - A2 * R_bar
        Xbar_chart["UCL"] = Xbar_bar + A2 * R_bar

        R_chart = pd.DataFrame()
        R_chart["point"] = sg["R"]
        R_chart["CL"] = R_bar
        R_chart["LCL"] = D3 * R_bar
        R_chart["UCL"] = D4 * R_bar

        return Xbar_chart, R_chart

    elif chart_type == "Xbar-s":
        sg = pd.DataFrame()
        sg["Xbar"] = data.groupby(sg_name)[var_name].mean()
        sg["s"] = data.groupby(sg_name)[var_name].std(ddof=1)
        sg["n_i"] = data[sg_name].value_counts()

        Xbar_bar = sg["Xbar"].mean()
        s_bar = sg["s"].mean()
        m = sg["n_i"].mode()

        A3 = unbiased_coefficient("A3", m[0])
        B3 = unbiased_coefficient("B3", m[0])
        B4 = unbiased_coefficient("B4", m[0])

        Xbar_chart = pd.DataFrame()
        Xbar_chart["point"] = sg["Xbar"]
        Xbar_chart["CL"] = Xbar_bar
        Xbar_chart["LCL"] = Xbar_bar - A3 * s_bar
        Xbar_chart["UCL"] = Xbar_bar + A3 * s_bar

        s_chart = pd.DataFrame()
        s_chart["point"] = sg["s"]
        s_chart["CL"] = s_bar
        s_chart["LCL"] = B3 * s_bar
        s_chart["UCL"] = B4 * s_bar

        return Xbar_chart, s_chart

    elif chart_type == "I-MR":
        w = window
        sg = data.set_index(sg_name)

        Xbar = sg[var_name].mean()
        MR_i = sg[var_name].rolling(window=w).apply(lambda x: x.max() - x.min())
        MR_bar = MR_i[w - 1:].mean()

        D3 = unbiased_coefficient("D3", w)
        D4 = unbiased_coefficient("D4", w)
        d2 = unbiased_coefficient("d2", w)

        I_chart = pd.DataFrame()
        I_chart["point"] = sg[var_name]
        I_chart["CL"] = Xbar
        I_chart["LCL"] = Xbar - 3 * MR_bar / d2
        I_chart["UCL"] = Xbar + 3 * MR_bar / d2

        MR_chart = pd.DataFrame()
        MR_chart["point"] = MR_i
        MR_chart["CL"] = MR_bar
        MR_chart["LCL"] = D3 * MR_bar
        MR_chart["UCL"] = D4 * MR_bar

        return I_chart, MR_chart

    return None


def generate_count_chart(df_raw, chart_type="NP"):
    """계수형 (NP, P, C, U)"""
    sg_name, n_i, var_name = df_raw.columns
    data = df_raw.set_index(sg_name)

    if chart_type == "NP":
        np_bar = data[var_name].sum() / len(data[n_i])
        p_bar = data[var_name].sum() / data[n_i].sum()

        NP_chart = pd.DataFrame()
        NP_chart["point"] = data[var_name]
        NP_chart["CL"] = np_bar
        NP_chart["LCL"] = np_bar - 3 * np.sqrt(np_bar * (1 - p_bar))
        NP_chart["UCL"] = np_bar + 3 * np.sqrt(np_bar * (1 - p_bar))
        return (NP_chart,)

    elif chart_type == "P":
        p_bar = data[var_name].sum() / data[n_i].sum()

        P_chart = pd.DataFrame()
        P_chart["point"] = data[var_name] / data[n_i]
        P_chart["CL"] = p_bar
        P_chart["LCL"] = p_bar - 3 * np.sqrt(p_bar * (1 - p_bar) / data[n_i])
        P_chart["UCL"] = p_bar + 3 * np.sqrt(p_bar * (1 - p_bar) / data[n_i])
        return (P_chart,)

    elif chart_type == "C":
        c_bar = data[var_name].mean()

        C_chart = pd.DataFrame()
        C_chart["point"] = data[var_name]
        C_chart["CL"] = c_bar
        C_chart["LCL"] = c_bar - 3 * np.sqrt(c_bar)
        C_chart["UCL"] = c_bar + 3 * np.sqrt(c_bar)
        return (C_chart,)

    elif chart_type == "U":
        u_bar = data[var_name].sum() / data[n_i].sum()

        U_chart = pd.DataFrame()
        U_chart["point"] = data[var_name] / data[n_i]
        U_chart["CL"] = u_bar
        U_chart["LCL"] = u_bar - 3 * np.sqrt(u_bar / data[n_i])
        U_chart["UCL"] = u_bar + 3 * np.sqrt(u_bar / data[n_i])
        return (U_chart,)

    return None


def nelson_rule_1(chart):
    return chart[(chart["point"] > chart["UCL"]) | (chart["point"] < chart["LCL"])]


def plot_variable_control_chart(charts, chart_name, var_name="value"):
    """관리도 시각화 (계량형/계수형 공용)"""
    num_charts = len(charts)
    fig = make_subplots(rows=num_charts, cols=1, shared_yaxes=False)

    labels = chart_name.split("-")

    for i in range(num_charts):
        c = charts[i]
        label = labels[i] if i < len(labels) else chart_name

        fig.add_trace(
            go.Scatter(x=c.index, y=c["point"], mode="lines+markers",
                       marker=dict(size=7, color=config.COLOR_PRIMARY),
                       line=dict(color=config.COLOR_PRIMARY, width=1.5),
                       name=label),
            row=i + 1, col=1,
        )
        fig.add_trace(
            go.Scatter(x=c.index, y=c["CL"], mode="lines",
                       line=dict(color=config.COLOR_CL, dash="dashdot"), name="CL"),
            row=i + 1, col=1,
        )
        fig.add_trace(
            go.Scatter(x=c.index, y=c["LCL"], mode="lines",
                       line=dict(color=config.COLOR_LCL, dash="dot"), name="LCL"),
            row=i + 1, col=1,
        )
        fig.add_trace(
            go.Scatter(x=c.index, y=c["UCL"], mode="lines",
                       line=dict(color=config.COLOR_UCL, dash="dot"), name="UCL"),
            row=i + 1, col=1,
        )

        ooc = nelson_rule_1(c)
        if len(ooc) > 0:
            fig.add_trace(
                go.Scatter(x=ooc.index, y=ooc["point"], mode="markers",
                           marker=dict(size=11, color=config.COLOR_OOC, symbol="x"),
                           name="이탈점"),
                row=i + 1, col=1,
            )

        fig.update_yaxes(title=label, row=i + 1, col=1)

        last_index = c.index[-1]
        CL, LCL, UCL = c.iloc[-1, 1:]
        fig.add_annotation(x=last_index, y=UCL, text=f"UCL={UCL:.4f}",
                           showarrow=False, font=dict(color=config.COLOR_UCL),
                           xanchor="left", row=i + 1, col=1)
        fig.add_annotation(x=last_index, y=CL, text=f"CL={CL:.4f}",
                           showarrow=False, font=dict(color=config.COLOR_CL),
                           xanchor="left", row=i + 1, col=1)
        fig.add_annotation(x=last_index, y=LCL, text=f"LCL={LCL:.4f}",
                           showarrow=False, font=dict(color=config.COLOR_LCL),
                           xanchor="left", row=i + 1, col=1)

    fig.update_xaxes(ticks="outside", title=charts[0].index.name)
    fig.update_layout(
        height=120 + 260 * num_charts,
        showlegend=False,
        margin=dict(l=50, r=80, t=40, b=50),
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
    )
    return fig
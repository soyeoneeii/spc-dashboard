# 공정능력 분석

import numpy as np
import pandas as pd
from scipy.stats import shapiro, norm, zscore, probplot
import plotly.express as px

from constants import calc_unbiased_const
import config


def process_capability(data, LSL, USL):
    """process_capability : Cp/Cpk(within), Pp/Ppk(overall)"""
    sg_name, var_name = data.columns

    sigma_sg = data.groupby(sg_name)[var_name].std()

    x_bar = data[var_name].mean()
    sigma_hat = data[var_name].std(ddof=1)
    sigma_overall = sigma_hat / calc_unbiased_const("c4", len(data))

    sigma_p = np.sqrt(np.sum(sigma_sg ** 2) / len(sigma_sg))
    sigma_within = sigma_p / calc_unbiased_const("c4", len(data) - len(sigma_sg) + 1)

    Cp = (USL - LSL) / (6 * sigma_within)
    Cpk = min((USL - x_bar) / (3 * sigma_within), (x_bar - LSL) / (3 * sigma_within))
    Pp = (USL - LSL) / (6 * sigma_overall)
    Ppk = min((USL - x_bar) / (3 * sigma_overall), (x_bar - LSL) / (3 * sigma_overall))

    return Cp, Cpk, Pp, Ppk


def capability_detail(data, LSL, USL):
    """capability_detail  : 평균·전체표준편차·예상 불량률(ppm)"""
    sg_name, var_name = data.columns

    x_bar = data[var_name].mean()
    sigma_hat = data[var_name].std(ddof=1)
    sigma_overall = sigma_hat / calc_unbiased_const("c4", len(data))

    z_u = (USL - x_bar) / sigma_overall
    z_l = (x_bar - LSL) / sigma_overall
    ppm = (norm.cdf(-z_u) + norm.cdf(-z_l)) * 1_000_000

    return {
        "x_bar": x_bar,
        "sigma_overall": sigma_overall,
        "n": len(data),
        "ppm": ppm,
    }


def normality_test(data):
    """Shapiro-Wilk 정규성 검정"""
    sg_name, var_name = data.columns
    stat, p = shapiro(data[var_name])
    return p >= 0.05, p


def plot_process_capability(data, LSL, USL):
    """Plotly Figure 생성"""
    sg_name, var_name = data.columns

    Cp, Cpk, Pp, Ppk = process_capability(data, LSL, USL)

    fig = px.histogram(
        data,
        x=data[var_name],
        nbins=20,
        color=sg_name,
        marginal="box",
        opacity=0.5,
    )
    fig.add_vline(x=LSL, line_width=1, line_dash="dash",
                  line_color=config.COLOR_SPEC, annotation_text="LSL")
    fig.add_vline(x=USL, line_width=1, line_dash="dash",
                  line_color=config.COLOR_SPEC, annotation_text="USL")
    fig.add_annotation(
        xref="paper", yref="paper",
        x=1.14, y=0.0,
        text=f"Cp ={Cp:.4f}<br>Cpk={Cpk:.4f}<br>Pp ={Pp:.4f}<br>Ppk={Ppk:.4f}",
        align="right", showarrow=False, bordercolor="black",
    )
    fig.update_layout(
        height=460,
        margin=dict(l=10, r=120, t=30, b=20),
        showlegend=False,
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
    )
    return fig


def plot_qq(data):
    """Plotly Figure 생성"""
    sg_name, var_name = data.columns

    z_value = zscore(data[var_name])
    (osm, osr), _ = probplot(z_value, dist="norm")

    fig = px.scatter(
        x=osm, y=osr,
        labels={"x": "Theoretical Quantiles", "y": "Sample Quantiles"},
    )
    fig.add_shape(type="line", x0=-3, y0=-3, x1=3, y1=3,
                  line=dict(color=config.COLOR_SPEC, width=2))
    fig.update_layout(
        height=360,
        margin=dict(l=10, r=10, t=30, b=20),
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
    )
    return fig
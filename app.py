import pandas as pd
import streamlit as st

import config
import data_loader as dl
import analytics
import capability as cap
import control_chart as cc
import rules

st.set_page_config(page_title="공정능력분석 · SPC", layout="wide")


def fmt(x, n=4):
    return f"{x:.{n}f}"


def status_banner(status, title, sub=""):
    sub_html = f"<div style='font-size:13px;color:{config.COLOR_TEXT_MUTED};margin-top:3px'>{sub}</div>" if sub else ""
    st.markdown(
        f"""<div style="background:{status['bg']};border-left:3px solid {status['fg']};
        border-radius:0 10px 10px 0;padding:13px 16px;margin-bottom:18px">
        <span style="font-size:15px;font-weight:500;color:{status['fg']}">{status['icon']} {title}</span>
        {sub_html}</div>""",
        unsafe_allow_html=True,
    )


def summary_strip(items, highlight_last=False):
    cols = st.columns(len(items))
    for idx, (col, (label, value)) in enumerate(zip(cols, items)):
        is_hi = highlight_last and idx == len(items) - 1
        bg = config.COLOR_PRIMARY if is_hi else config.COLOR_BG_CARD
        border = "none" if is_hi else f"0.5px solid {config.COLOR_BORDER}"
        label_color = "#B5D4F4" if is_hi else config.COLOR_TEXT_MUTED
        value_color = "#FFFFFF" if is_hi else config.COLOR_TEXT
        col.markdown(
            f"""<div style="background:{bg};border:{border};border-radius:10px;padding:11px 14px">
            <div style="font-size:11px;color:{label_color}">{label}</div>
            <div style="font-size:13px;font-weight:500;color:{value_color};margin-top:2px">{value}</div>
            </div>""",
            unsafe_allow_html=True,
        )


def kpi_card(col, label, value, value_color=None, note="", note_color=None):
    vc = value_color or config.COLOR_TEXT
    note_html = f"<div style='font-size:10px;color:{note_color or config.COLOR_TEXT_MUTED};margin-top:1px'>{note}</div>" if note else ""
    col.markdown(
        f"""<div style="background:{config.COLOR_BG_PAGE};border-radius:10px;padding:13px 14px">
        <div style="font-size:12px;color:{config.COLOR_TEXT_MUTED}">{label}</div>
        <div style="font-size:25px;font-weight:500;color:{vc};margin-top:2px">{value}</div>
        {note_html}</div>""",
        unsafe_allow_html=True,
    )


def metric_line(col, label, value, accent=None, value_color=None):
    border = accent or config.COLOR_BORDER
    vc = value_color or config.COLOR_TEXT
    col.markdown(
        f"""<div style="padding:10px 14px;border-left:2px solid {border}">
        <div style="font-size:12px;color:{config.COLOR_TEXT_MUTED}">{label}</div>
        <div style="font-size:18px;font-weight:500;color:{vc}">{value}</div>
        </div>""",
        unsafe_allow_html=True,
    )


def index_color(value, good=1.33, warn=1.00):
    if value >= good:
        return "#1E7544"
    elif value >= warn:
        return "#9A6510"
    return "#A32D2D"


# ──────────────────────────────────────────────
# 사이드바 — 입력
# ──────────────────────────────────────────────
st.sidebar.title("분석 설정")

kind = st.sidebar.radio("1. 분석 유형", ["계량형 (측정값)", "계수형 (불량/결함)"])
is_variable = kind.startswith("계량형")

source = st.sidebar.radio("2. 데이터 소스", ["샘플 데이터", "파일 업로드"])

uploaded = None
if source == "파일 업로드":
    ext_hint = "CSV/XLSX — 각 행이 한 부분군(측정값 여러 열)" if is_variable \
        else "CSV/XLSX — [부분군, 표본크기, 측정값] 순서"
    uploaded = st.sidebar.file_uploader(ext_hint, type=["csv", "xlsx", "xls"])


@st.cache_data
def load_variable_sample():
    return dl.load_sample_variable()


@st.cache_data
def load_count_sample():
    return dl.load_sample_count()


# ── 원본 로드 ──
df_raw = None
data_label = ""
if is_variable:
    if source == "샘플 데이터":
        df_raw = load_variable_sample()
        data_label = "measurements.csv (샘플)"
    elif uploaded is not None:
        df_raw = dl.read_uploaded(uploaded)
        data_label = uploaded.name
else:
    if source == "샘플 데이터":
        df_raw = load_count_sample()
        data_label = "defects.csv (샘플)"
    elif uploaded is not None:
        df_raw = dl.read_uploaded(uploaded)
        data_label = uploaded.name

if df_raw is None:
    st.title("공정능력분석 · 통계적공정관리")
    st.write("왼쪽에서 분석 유형과 데이터를 선택하세요.")
    st.stop()


# ══════════════════════════════════════════════
# 계량형
# ══════════════════════════════════════════════
if is_variable:
    st.sidebar.subheader("3. 규격")
    target = st.sidebar.number_input("목표값 (Target)", value=config.DEFAULT_TARGET, format="%.4f")
    tol = st.sidebar.number_input("허용오차 (± Tolerance)", value=config.DEFAULT_TOLERANCE,
                                  min_value=0.0, format="%.4f")
    LSL, USL = target - tol, target + tol

    st.sidebar.subheader("4. 관리도")
    chart_type = st.sidebar.selectbox("관리도 종류", ["Xbar-R", "Xbar-s", "I-MR"])
    window = 3
    if chart_type == "I-MR":
        window = st.sidebar.number_input("Moving Range window", value=3, min_value=2, step=1)

    data = dl.prepare_variable(df_raw)
    sg_col, var_col = data.columns
    k = analytics.capability_kpis(data, LSL, USL)

    st.title("공정능력분석 · 통계적공정관리")
    tab_o, tab_c, tab_s, tab_d = st.tabs(["개요", "공정능력분석", "통계적공정관리", "데이터"])

    # ── 개요 ──
    with tab_o:
        summary_strip([
            ("데이터", data_label),
            ("부분군 / 표본", f"{data[sg_col].nunique()} / {len(data)}"),
            ("목표 ± 허용오차", f"{fmt(target,2)} ± {fmt(tol,2)}"),
            ("규격 (LSL / USL)", f"{fmt(LSL,2)} / {fmt(USL,2)}"),
        ], highlight_last=True)
        st.write("")

        status_banner(k["status"], f"{k['status']['label']} — 공정 {k['grade']}등급: {k['verdict']}", k["action"])

        c1, c2, c3, c4, c5 = st.columns(5)
        kpi_card(c1, "Cp", fmt(k["Cp"], 3), config.COLOR_PRIMARY)
        cpk_color = index_color(k["Cpk"])
        kpi_card(c2, "Cpk", fmt(k["Cpk"], 3), cpk_color,
                 note=("▲ 양호" if k["Cpk"] >= 1.33 else ("▼ 주의" if k["Cpk"] >= 1.0 else "▼ 위험")),
                 note_color=cpk_color)
        kpi_card(c3, "Pp", fmt(k["Pp"], 3), config.COLOR_PRIMARY)
        ppk_color = index_color(k["Ppk"])
        kpi_card(c4, "Ppk", fmt(k["Ppk"], 3), ppk_color,
                 note=("▲ 양호" if k["Ppk"] >= 1.33 else ("▼ 주의" if k["Ppk"] >= 1.0 else "▼ 위험")),
                 note_color=ppk_color)
        kpi_card(c5, "예상 불량률", f"{k['ppm']:.0f} <span style='font-size:12px;color:{config.COLOR_TEXT_MUTED}'>ppm</span>")

        st.write("")
        ooc = rules.ooc_subgroups(cc.generate_value_chart(data, chart_type=chart_type, window=window)[0])
        m1, m2, m3 = st.columns(3)
        metric_line(m1, "공정 평균", fmt(k["x_bar"], 3))
        metric_line(m2, "전체 표준편차", fmt(k["sigma_overall"], 3))
        ooc_accent = "#E24B4A" if len(ooc) > 0 else config.COLOR_BORDER
        ooc_vcolor = "#A32D2D" if len(ooc) > 0 else config.COLOR_TEXT
        metric_line(m3, "관리이탈 부분군", f"{len(ooc)}", accent=ooc_accent, value_color=ooc_vcolor)

    # ── 공정능력분석 ──
    with tab_c:
        st.subheader("공정능력 히스토그램")
        st.plotly_chart(cap.plot_process_capability(data, LSL, USL),
                        use_container_width=True, key="cap_hist")

        is_normal, p = cap.normality_test(data)
        col_a, col_b = st.columns(2)
        with col_a:
            st.subheader("정규성 검정 (Shapiro–Wilk)")
            if is_normal:
                st.success(f"정규성 만족 (p = {fmt(p)} ≥ 0.05) — 공정능력지수 신뢰 가능")
            else:
                st.warning(f"정규성 불만족 (p = {fmt(p)} < 0.05) — Box-Cox / Johnson 변환 후 재계산 권장")
        with col_b:
            st.subheader("Q–Q plot")
            st.plotly_chart(cap.plot_qq(data), use_container_width=True, key="cap_qq")

    # ── 통계적공정관리 ──
    with tab_s:
        st.subheader(f"{chart_type} 관리도")
        charts = cc.generate_value_chart(data, chart_type=chart_type, window=window)
        st.plotly_chart(cc.plot_variable_control_chart(charts, chart_type, var_col),
                        use_container_width=True, key="spc_main")

        st.subheader("관리도 재작성 (이상치 제거 후 한계 재계산)")
        res = rules.recreate_value_chart(data, chart_type=chart_type, window=window)

        if res["charts_revised"] is None:
            st.success("관리한계를 벗어난 부분군이 없습니다. 공정이 관리상태입니다.")
        else:
            rounds_txt = " → ".join(str(r) for r in res["history"])
            st.warning(f"이탈 부분군 제거 ({res['rounds']}회, 표본 {res['removed']}개): {rounds_txt}")

            st.caption("초기 관리도")
            st.plotly_chart(cc.plot_variable_control_chart(res["charts_initial"], chart_type, var_col),
                            use_container_width=True, key="spc_initial")
            st.caption("재작성 관리도")
            st.plotly_chart(cc.plot_variable_control_chart(res["charts_revised"], chart_type, var_col),
                            use_container_width=True, key="spc_revised")

            iu, il = res["initial_limits"]
            ru, rl = res["revised_limits"]
            st.table(pd.DataFrame({
                "구분": ["초기", "재작성"],
                "UCL": [fmt(iu), fmt(ru)],
                "LCL": [fmt(il), fmt(rl)],
            }))

    # ── 데이터 ──
    with tab_d:
        st.subheader("원본 데이터")
        st.dataframe(df_raw, use_container_width=True, height=300)

        st.subheader("부분군별 통계량")
        grp = data.groupby(sg_col)[var_col].agg(["count", "mean", "std", "min", "max"])
        grp["range"] = grp["max"] - grp["min"]
        st.dataframe(grp, use_container_width=True)

        st.download_button("CSV 다운로드", df_raw.to_csv(index=False).encode("utf-8-sig"),
                           "measurements.csv", "text/csv")


# ══════════════════════════════════════════════
# 계수형
# ══════════════════════════════════════════════
else:
    st.sidebar.subheader("3. 관리도")
    chart_type = st.sidebar.selectbox("관리도 종류", ["NP", "P", "C", "U"])

    df_count = dl.prepare_count(df_raw)
    sg_col, size_col, var_col = df_count.columns

    charts = cc.generate_count_chart(df_count, chart_type=chart_type)
    ooc = rules.ooc_subgroups(charts[0])

    st.title("통계적공정관리 (계수형)")
    tab_o, tab_s, tab_d = st.tabs(["개요", "통계적공정관리", "데이터"])

    # ── 개요 ──
    with tab_o:
        summary_strip([
            ("데이터", data_label),
            ("로트 수", f"{df_count[sg_col].nunique()}"),
            ("평균 표본크기", f"{df_count[size_col].mean():.0f}"),
            ("관리도", f"{chart_type}"),
        ], highlight_last=True)
        st.write("")

        if len(ooc) > 0:
            status_banner(config.STATUS_RISK, "관리이탈 발생 — 이상원인 분석 필요")
        else:
            status_banner(config.STATUS_GOOD, "관리상태 — 모든 로트가 관리한계 내")

        m1, m2 = st.columns(2)
        metric_line(m1, "총 로트 수", f"{df_count[sg_col].nunique()}")
        ooc_accent = "#E24B4A" if len(ooc) > 0 else config.COLOR_BORDER
        ooc_vcolor = "#A32D2D" if len(ooc) > 0 else config.COLOR_TEXT
        metric_line(m2, "관리이탈 로트", f"{len(ooc)}", accent=ooc_accent, value_color=ooc_vcolor)

    # ── 통계적공정관리 ──
    with tab_s:
        st.subheader(f"{chart_type} 관리도")
        st.plotly_chart(cc.plot_variable_control_chart(charts, chart_type, var_col),
                        use_container_width=True, key="count_spc")
        if len(ooc) > 0:
            st.warning(f"관리한계 이탈 로트: {ooc}")
        else:
            st.success("모든 로트가 관리상태입니다.")

    # ── 데이터 ──
    with tab_d:
        st.subheader("원본 데이터")
        st.dataframe(df_raw, use_container_width=True, height=300)
        st.download_button("CSV 다운로드", df_raw.to_csv(index=False).encode("utf-8-sig"),
                           "defects.csv", "text/csv")

st.sidebar.markdown("---")
st.sidebar.caption("스마트제조 · 공정능력분석 + SPC")
import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(BASE_DIR, "data")
UNBIASED_CAPABILITY_CSV = os.path.join(DATA_DIR, "unbiased_capability_analysis.csv")
UNBIASED_CONTROL_CSV = os.path.join(DATA_DIR, "unbiased_control_chart.csv")

SAMPLE_MEASUREMENTS = os.path.join(DATA_DIR, "measurements.csv")
SAMPLE_DEFECTS = os.path.join(DATA_DIR, "defects.csv")

# ──────────────────────────────────────────────
# 브랜드 색 토큰
# ──────────────────────────────────────────────
COLOR_PRIMARY = "#15406B"
COLOR_PRIMARY_LIGHT = "#1D5288"
COLOR_PRIMARY_DARK = "#0E2C4A"
COLOR_TEXT = "#2C3E50"
COLOR_TEXT_MUTED = "#6B7A89"
COLOR_BG_PAGE = "#F7F9FB"
COLOR_BG_CARD = "#FFFFFF"
COLOR_BORDER = "#E3E8ED"

# ──────────────────────────────────────────────
# 관리도 선 색
# ──────────────────────────────────────────────
COLOR_CL = "green"
COLOR_LCL = "red"
COLOR_UCL = "magenta"
COLOR_SPEC = "red"
COLOR_OOC = "red"

# ──────────────────────────────────────────────
# 신호등 상태색
# ──────────────────────────────────────────────
STATUS_GOOD = {"bg": "#E8F3EC", "fg": "#1E7544", "icon": "🟢", "label": "양호"}
STATUS_WARN = {"bg": "#FBF1E3", "fg": "#9A6510", "icon": "🟡", "label": "주의"}
STATUS_RISK = {"bg": "#FBEAEA", "fg": "#A32D2D", "icon": "🔴", "label": "위험"}

# ──────────────────────────────────────────────
# 규격 기본값
# ──────────────────────────────────────────────
DEFAULT_TARGET = 100.0
DEFAULT_TOLERANCE = 20.0

# ──────────────────────────────────────────────
# 공정능력 판정표 — Cpk 기준
# ──────────────────────────────────────────────
CAPABILITY_GRADES = [
    (1.67, float("inf"), 0, "매우 충분",
     "들쭉날쭉 걱정 없음. 비용절감·관리 간소화 검토."),
    (1.33, 1.67, 1, "충분",
     "이상적인 공정상황. 현 상태 유지."),
    (1.00, 1.33, 2, "충분하지는 않으나 괜찮음",
     "공정관리를 확실히 하여 관리상태 유지. Cpk가 1에 가까우면 불량 주의."),
    (0.67, 1.00, 3, "모자람",
     "불량품 발생 중. 전체 선별·공정 개선·관리 필요."),
    (float("-inf"), 0.67, 4, "매우 부족",
     "품질 불만족. 긴급 현황조사·원인규명·개선. 규격값 재검토."),
]


def grade_of(cpk: float):
    """Cpk 값 → (등급, 판정, 시정조치)."""
    for lo, hi, grade, verdict, action in CAPABILITY_GRADES:
        if lo <= cpk < hi:
            return grade, verdict, action
    return 4, "매우 부족", CAPABILITY_GRADES[-1][4]


def traffic_light(cpk: float):
    """Cpk 값 → 신호등 상태 dict (STATUS_GOOD/WARN/RISK)."""
    if cpk >= 1.33:
        return STATUS_GOOD
    elif cpk >= 1.00:
        return STATUS_WARN
    else:
        return STATUS_RISK
# 대시보드 KPI 조립을 위한 모듈

import config
from capability import process_capability, capability_detail


def capability_kpis(data, LSL, USL):
    Cp, Cpk, Pp, Ppk = process_capability(data, LSL, USL)
    detail = capability_detail(data, LSL, USL)

    grade, verdict, action = config.grade_of(Cpk)
    status = config.traffic_light(Cpk)

    return {
        "Cp": Cp,
        "Cpk": Cpk,
        "Pp": Pp,
        "Ppk": Ppk,
        "x_bar": detail["x_bar"],
        "sigma_overall": detail["sigma_overall"],
        "n": detail["n"],
        "ppm": detail["ppm"],
        "grade": grade,
        "verdict": verdict,
        "action": action,
        "status": status,
    }
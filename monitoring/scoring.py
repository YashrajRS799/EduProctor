"""
Monitoring app – Violation scoring engine.
Maps violation types to severity scores and computes risk levels.
"""

# Severity score map – how many points each violation type costs
SEVERITY_MAP = {
    'tab_switch':      5,
    'multiple_faces': 10,
    'no_face':         7,
    'window_resize':   3,
    'fullscreen_exit': 5,
    'copy_paste':      4,
    'right_click':     2,
    'head_movement':   3,
    'identity_mismatch': 15,
}

# Risk thresholds
RISK_LOW_MAX    = 20
RISK_MEDIUM_MAX = 50


def get_severity(violation_type: str) -> int:
    """Return the severity score for a given violation type."""
    return SEVERITY_MAP.get(violation_type, 1)


def calculate_risk_level(total_score: int) -> str:
    """
    Convert a cumulative violation score into a risk level string.

    Rules:
        0  – 20  → 'low'
        21 – 50  → 'medium'
        51+      → 'high'
    """
    if total_score <= RISK_LOW_MAX:
        return 'low'
    elif total_score <= RISK_MEDIUM_MAX:
        return 'medium'
    else:
        return 'high'


def calculate_integrity_score(total_violation_score: int) -> float:
    """
    Convert a raw violation score to a 0–100 integrity score.
    Integrity score decreases as violation score increases.
    Score bottoms out at 0.
    """
    integrity = max(0.0, 100.0 - (total_violation_score * 1.5))
    return round(integrity, 1)

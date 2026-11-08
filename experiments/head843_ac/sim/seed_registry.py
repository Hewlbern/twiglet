"""Seed blocks for this study.

Historical blocks listed in the AC handoff README and LOAD_REPORT are burned: they are
reproduction checks only, never a place to choose a new gain or gait parameter.
Fresh blocks below were reserved before any new trial was scored. reserved_unused is
not read by the runner.
"""
BURNED_BLOCKS = [5000, 6000, 7000, 8000, 9000, 11000, 12000, 13000, 14000, 15000, 16000, 17000, 18000, 19000]

# name -> (start, count, role)
FRESH = {
    "heading_tune": (21000, 24, "tune heading gains only; +20 deg profile"),
    "load_tune": (22000, 20, "tune load-screen acceptance only"),
    "stop_test": (23000, 20, "phase-aware stop/start test; no parameter fit"),
    "terrain_test": (24000, 40, "labelled terrain test; no parameter fit"),
    "headarm_test": (25000, 40, "walking head/arm test; no parameter fit"),
    "heading_heldout": (26000, 200, "untouched heading held-out"),
    "load_heldout": (27000, 200, "untouched load / flat held-out"),
    "fresh_flat": (28000, 200, "untouched flat reliability of the unchanged reliable gait"),
    "reserved_unused": (29000, 200, "reserved, not consumed"),
}

def ranges():
    out = []
    for b in BURNED_BLOCKS:
        out.append((b, b + 200, "burned"))
    for name, (s, n, role) in FRESH.items():
        out.append((s, s + n, name))
    return out

def assert_disjoint():
    spans = [(a, b, tag) for a, b, tag in ranges()]
    spans.sort()
    for (a0, b0, t0), (a1, b1, t1) in zip(spans, spans[1:]):
        if b0 > a1:
            raise AssertionError(f"overlap {t0} [{a0},{b0}) vs {t1} [{a1},{b1})")
    return True

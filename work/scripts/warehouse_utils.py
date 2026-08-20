"""Shared helpers for the capstone's warehouse pipeline (ML-07 through ML-11).

Written for the capstone (not part of the original reference `scripts/` pipeline,
which stays untouched per work/README.md). Lives under work/scripts/ so it can be
imported from any of the capstone notebooks without duplicating logic five times.

Every function is pure and dataset-agnostic (no hardcoded column names) so the
same helpers work across w04-w07 and the capstone notebook.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Iterable

import numpy as np
import pandas as pd


ROOT = Path(__file__).resolve().parents[2]
WORK_OUTPUT_DIR = ROOT / "work" / "outputs"
WORK_FIGURE_DIR = ROOT / "work" / "figures"


def ensure_dirs() -> None:
    WORK_OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    WORK_FIGURE_DIR.mkdir(parents=True, exist_ok=True)


def write_json(path: Path, payload: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, sort_keys=True, default=str))


def read_json(path: Path) -> dict:
    return json.loads(path.read_text())


def precision_at_k(y_true: Iterable[int], scores: Iterable[float], k: int) -> float:
    """Fraction of the top-k ranked-by-score rows that are actually positive."""
    frame = pd.DataFrame({"y": list(y_true), "score": list(scores)})
    if frame.empty:
        return 0.0
    top = frame.sort_values("score", ascending=False).head(min(k, len(frame)))
    return float(top["y"].mean()) if len(top) else 0.0


def base_rate(y_true: Iterable[int]) -> float:
    values = pd.Series(list(y_true))
    return float(values.mean()) if len(values) else 0.0


def group_holdout_split(df: pd.DataFrame, group_col: str, test_size: float = 0.2, seed: int = 42):
    """Client-holdout split: every row for a given client lands entirely in train or test.

    A plain random row split lets the model partly memorize a client's baseline
    traffic level instead of learning a transferable pattern - see the
    hunting-leakage-and-validating skill. This is the split used everywhere in
    the capstone unless explicitly compared against a random split for the audit.
    """
    rng = np.random.default_rng(seed)
    groups = np.array(df[group_col].dropna().unique(), dtype=object)
    rng.shuffle(groups)
    n_test_groups = max(1, int(len(groups) * test_size))
    test_groups = set(groups[:n_test_groups])
    is_test = df[group_col].isin(test_groups)
    return df.loc[~is_test].copy(), df.loc[is_test].copy()


def safe_float(value: object, default: float = 0.0) -> float:
    try:
        number = float(value)
        if np.isfinite(number):
            return number
    except Exception:
        pass
    return default


def escape_xml(value: str) -> str:
    return (
        value.replace("&", "&amp;")
        .replace("<", "&lt;")
        .replace(">", "&gt;")
        .replace('"', "&quot;")
        .replace("'", "&apos;")
    )


def simple_svg_bar_chart(
    title: str,
    labels: list[str],
    values: list[float],
    path: Path,
    *,
    width: int = 960,
    height: int = 520,
    color: str = "#6F4E7C",
    caption: str = "",
) -> None:
    """Dependency-free SVG bar chart so charts don't need matplotlib in Colab."""
    path.parent.mkdir(parents=True, exist_ok=True)
    labels = [str(label) for label in labels]
    values = [safe_float(v) for v in values]
    max_value = max(max(values, default=1), 1)
    margin_left, margin_right = 220, 40
    margin_top, margin_bottom = 70, 70 if caption else 40
    plot_width = width - margin_left - margin_right
    plot_height = height - margin_top - margin_bottom
    bar_gap = 10
    bar_height = max(14, (plot_height - bar_gap * max(len(values) - 1, 0)) / max(len(values), 1))

    lines = [
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" viewBox="0 0 {width} {height}">',
        '<rect width="100%" height="100%" fill="#ffffff"/>',
        f'<text x="{width/2}" y="34" text-anchor="middle" font-family="Arial" font-size="22" fill="#16232a">{escape_xml(title)}</text>',
    ]
    for i, (label, value) in enumerate(zip(labels, values)):
        y = margin_top + i * (bar_height + bar_gap)
        bar_width = (value / max_value) * plot_width
        lines.append(f'<text x="{margin_left-12}" y="{y+bar_height*0.65:.1f}" text-anchor="end" font-family="Arial" font-size="13" fill="#27343b">{escape_xml(label[:38])}</text>')
        lines.append(f'<rect x="{margin_left}" y="{y:.1f}" width="{bar_width:.1f}" height="{bar_height:.1f}" fill="{color}" rx="4"/>')
        lines.append(f'<text x="{margin_left+bar_width+8:.1f}" y="{y+bar_height*0.65:.1f}" font-family="Arial" font-size="13" fill="#27343b">{value:,.3g}</text>')
    if caption:
        lines.append(f'<text x="{margin_left}" y="{height-20}" font-family="Arial" font-size="12" fill="#5a6a72">{escape_xml(caption[:160])}</text>')
    lines.append("</svg>")
    path.write_text("\n".join(lines))


# ---------------------------------------------------------------------------
# Warehouse access - shared by every ML-07 through ML-11 notebook so the same
# decision-window / outcome-window contract (locked in ML-04) is defined once,
# not re-typed five times with room for the definition to quietly drift.
# ---------------------------------------------------------------------------

WAREHOUSE_TABLE = "fact_content_daily_performance"
WAREHOUSE_BASE = f"hf://datasets/FlyRank/internship-warehouse/{WAREHOUSE_TABLE}"

# The eight decision-time features used from ML-07 onward. Every one is an
# aggregate over the DECISION month only (never the outcome month), so nothing
# here can see the future it is being scored against.
FEATURE_COLUMNS = [
    "impressions",      # summed gsc_impressions in the decision month - observed visibility
    "clicks",           # summed gsc_clicks in the decision month - observed clicks
    "avg_position",      # mean gsc_avg_position in the decision month - observed rank
    "ctr",               # clicks / impressions, both from the decision month only
    "ga4_sessions",       # summed ga4_sessions - observed engagement volume
    "sessions_ai",        # summed sessions_ai - observed AI-referral visibility
    "scroll_events",       # summed scroll_events - observed on-page engagement depth
    "days_active",          # count of decision-month rows with any GSC/GA4 data - history coverage
]


def connect_to_warehouse(hf_token: str):
    """Open a DuckDB connection configured to read the gated HF warehouse.

    Must be called from Colab (or any environment with real network access to
    huggingface.co) - this will fail in a network-restricted sandbox.
    """
    import duckdb

    con = duckdb.connect()
    con.execute(
        f"""
        INSTALL httpfs;
        LOAD httpfs;
        CREATE OR REPLACE SECRET hf_secret (
            TYPE HUGGINGFACE,
            TOKEN '{hf_token}'
        );
        """
    )
    return con


def _month_glob(month: str) -> str:
    return f"{WAREHOUSE_BASE}/month={month}/*.parquet"


def aggregate_month_features(con, month: str) -> "pd.DataFrame":
    """One row per (client_hash_id, content_hash_id) for the given decision month.

    Only aggregates - no per-day rows leave this function - and only columns
    that are genuinely knowable by the end of that month.
    """
    query = f"""
    SELECT
        client_hash_id,
        content_hash_id,
        SUM(gsc_impressions)                                   AS impressions,
        SUM(gsc_clicks)                                        AS clicks,
        AVG(gsc_avg_position)                                  AS avg_position,
        CASE WHEN SUM(gsc_impressions) > 0
             THEN SUM(gsc_clicks) * 1.0 / SUM(gsc_impressions)
             ELSE NULL END                                     AS ctr,
        SUM(COALESCE(ga4_sessions, 0))                         AS ga4_sessions,
        SUM(COALESCE(sessions_ai, 0))                          AS sessions_ai,
        SUM(COALESCE(scroll_events, 0))                        AS scroll_events,
        COUNT(*) FILTER (
            WHERE gsc_data_available IS TRUE
               OR ga4_data_available IS TRUE
        )                                                       AS days_active
    FROM read_parquet('{_month_glob(month)}')
    WHERE gsc_data_available IS TRUE
    GROUP BY client_hash_id, content_hash_id
    """
    return con.execute(query).df()


def aggregate_month_outcome(con, month: str, metric: str = "gsc_impressions") -> "pd.DataFrame":
    """One row per content item: total of `metric` for the OUTCOME month only.

    Kept separate from aggregate_month_features on purpose - this function's
    output is only ever used to build a label, never joined in as a feature.
    """
    query = f"""
    SELECT
        client_hash_id,
        content_hash_id,
        SUM({metric}) AS outcome_value
    FROM read_parquet('{_month_glob(month)}')
    WHERE gsc_data_available IS TRUE
    GROUP BY client_hash_id, content_hash_id
    """
    return con.execute(query).df()


def build_dev_frame(con, decision_month: str, outcome_month: str, cache_path=None, force: bool = False):
    """Decision-window features joined to a future_decline label from the outcome month.

    future_decline = 1 if outcome-month impressions < decision-month impressions,
    else 0. Same definition ML-04 already used for March-to-April - kept identical
    here on purpose (see work README rule: don't silently redefine the label).
    """
    if cache_path is not None and Path(cache_path).exists() and not force:
        return pd.read_csv(cache_path)

    features = aggregate_month_features(con, decision_month)
    outcome = aggregate_month_outcome(con, outcome_month, metric="gsc_impressions")
    outcome = outcome.rename(columns={"outcome_value": "outcome_impressions"})

    frame = features.merge(outcome, on=["client_hash_id", "content_hash_id"], how="inner")
    frame["future_decline"] = (frame["outcome_impressions"] < frame["impressions"]).astype(int)
    frame = frame.drop(columns=["outcome_impressions"])

    if cache_path is not None:
        ensure_dirs()
        frame.to_csv(cache_path, index=False)
    return frame


def build_live_scoring_frame(con, decision_month: str, cache_path=None, force: bool = False):
    """Decision-window features only, no label - for scoring the current/live queue."""
    if cache_path is not None and Path(cache_path).exists() and not force:
        return pd.read_csv(cache_path)
    frame = aggregate_month_features(con, decision_month)
    if cache_path is not None:
        ensure_dirs()
        frame.to_csv(cache_path, index=False)
    return frame

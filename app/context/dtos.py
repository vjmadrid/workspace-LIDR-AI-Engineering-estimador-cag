from dataclasses import dataclass

@dataclass
class CanonicalExample:
    """A reference estimation expressed both as structured data and as Markdown.

    The structured fields (`breakdown`, totals, team) are the single source of truth
    used by the JSON and narrative formatters. `estimation_markdown` is precomputed
    so the Markdown formatter stays byte-for-byte identical to the legacy output.
    """

    title: str
    meeting_summary: str
    breakdown: list[tuple[str, int, int]]
    total_hours: int
    total_cost: int
    team: list[str]
    duration_weeks: int
    estimation_markdown: str
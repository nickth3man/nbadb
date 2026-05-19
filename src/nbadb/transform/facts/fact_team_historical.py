from __future__ import annotations

from typing import ClassVar

from nbadb.transform.base import SqlTransformer


class FactTeamHistoricalTransformer(SqlTransformer):
    output_table: ClassVar[str] = "fact_team_historical"
    depends_on: ClassVar[list[str]] = [
        "stg_team_historical_leaders",
        "stg_team_year_by_year",
        "stg_team_year_by_year_stats",
    ]

    # DISTINCT eliminates exact-copy rows produced when the same source stg
    # tables are re-loaded across multiple extraction passes.
    _SQL: ClassVar[str] = """
        SELECT DISTINCT *, 'leaders' AS history_type
        FROM stg_team_historical_leaders
        UNION ALL BY NAME
        SELECT DISTINCT *, 'year_by_year' AS history_type
        FROM stg_team_year_by_year
        UNION ALL BY NAME
        SELECT DISTINCT *, 'year_by_year_stats' AS history_type
        FROM stg_team_year_by_year_stats
    """

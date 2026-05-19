from __future__ import annotations

from typing import ClassVar

from nbadb.transform.base import SqlTransformer


class FactPlayoffSeriesTransformer(SqlTransformer):
    output_table: ClassVar[str] = "fact_playoff_series"
    depends_on: ClassVar[list[str]] = ["stg_common_playoff_series"]

    # stg_common_playoff_series returns multiple rows per (game_id, season_id)
    # for historical franchises that have been renamed (e.g. Clippers: SDC →
    # LAC → BUF).  Keep one canonical row per game+series via QUALIFY.
    _SQL: ClassVar[str] = """
        SELECT
            season_id,
            series_id,
            game_id,
            game_number,
            home_team_id,
            away_team_id,
            home_team_abbreviation,
            away_team_abbreviation,
            wins,
            losses
        FROM stg_common_playoff_series
        QUALIFY ROW_NUMBER() OVER (
            PARTITION BY game_id, series_id
            ORDER BY home_team_abbreviation
        ) = 1
    """

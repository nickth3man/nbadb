from __future__ import annotations

from typing import ClassVar

from nbadb.transform.base import SqlTransformer


class BridgePlayPlayerTransformer(SqlTransformer):
    output_table: ClassVar[str] = "bridge_play_player"
    depends_on: ClassVar[list[str]] = ["stg_play_by_play"]

    _SQL: ClassVar[str] = """
        SELECT DISTINCT game_id, event_num, player1_id AS player_id,
               player1_team_id AS team_id, 'primary' AS player_role
        FROM stg_play_by_play WHERE player1_id IS NOT NULL
        UNION ALL
        SELECT DISTINCT game_id, event_num, player2_id AS player_id,
               player2_team_id AS team_id, 'secondary' AS player_role
        FROM stg_play_by_play WHERE player2_id IS NOT NULL
        UNION ALL
        SELECT DISTINCT game_id, event_num, player3_id AS player_id,
               player3_team_id AS team_id, 'tertiary' AS player_role
        FROM stg_play_by_play WHERE player3_id IS NOT NULL
    """

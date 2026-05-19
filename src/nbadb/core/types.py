from __future__ import annotations

import re
from enum import StrEnum

from nbadb.orchestrate.seasons import current_season


class SeasonType(StrEnum):
    REGULAR = "Regular Season"
    PLAYOFFS = "Playoffs"
    PRE_SEASON = "Pre Season"
    ALL_STAR = "All Star"


class LeagueID(StrEnum):
    NBA = "00"
    ABA = "01"
    WNBA = "10"
    G_LEAGUE = "20"


class Format(StrEnum):
    SQLITE = "sqlite"
    DUCKDB = "duckdb"
    CSV = "csv"
    PARQUET = "parquet"


class SeasonPhase(StrEnum):
    PRESEASON = "Preseason"
    REGULAR = "Regular"
    PLAY_IN = "Play-In"
    PLAYOFFS_R1 = "Playoffs R1"
    PLAYOFFS_R2 = "Playoffs R2"
    PLAYOFFS_CF = "Conference Finals"
    FINALS = "Finals"
    ALL_STAR = "All-Star"


type GameId = str
type PlayerId = int
type TeamId = int
type SeasonYear = str
type GameDate = str

NBA_FIRST_SEASON: SeasonYear = "1946-47"


CURRENT_SEASON: SeasonYear = current_season()
NBA_HEADERS: dict[str, str] = {
    "Accept": "application/json, text/plain, */*",
    "Accept-Encoding": "gzip, deflate, br",
    "Accept-Language": "en-US,en;q=0.9",
    "Cache-Control": "no-cache",
    "Connection": "keep-alive",
    "Host": "stats.nba.com",
    "Origin": "https://www.nba.com",
    "Pragma": "no-cache",
    "Referer": "https://www.nba.com/",
    "Sec-Ch-Ua": '"Google Chrome";v="131", "Chromium";v="131", "Not_A Brand";v="24"',
    "Sec-Ch-Ua-Mobile": "?0",
    "Sec-Ch-Ua-Platform": '"Windows"',
    "Sec-Fetch-Dest": "empty",
    "Sec-Fetch-Mode": "cors",
    "Sec-Fetch-Site": "same-site",
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"
        " AppleWebKit/537.36 (KHTML, like Gecko)"
        " Chrome/131.0.0.0 Safari/537.36"
    ),
    "x-nba-stats-origin": "stats",
    "x-nba-stats-token": "true",
}

_IDENTIFIER_RE: re.Pattern[str] = re.compile(r"^[a-zA-Z_][a-zA-Z0-9_]*$")


def validate_sql_identifier(name: str) -> str:
    """Validate a string is a safe SQL identifier (table/column name)."""
    if not _IDENTIFIER_RE.match(name):
        raise ValueError(f"Invalid SQL identifier: {name!r}")
    return name

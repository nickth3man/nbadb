from __future__ import annotations

from typing import Annotated

import typer

from nbadb.cli.app import app
from nbadb.cli.commands._helpers import _build_settings, _run_pipeline
from nbadb.cli.options import DataDirOption, FormatOption, VerboseOption  # noqa: TC001
from nbadb.orchestrate import Orchestrator

SeasonTypesOption = Annotated[
    str | None,
    typer.Option(
        "--season-types",
        help="Comma-separated season types (e.g. 'Regular Season,Playoffs')",
    ),
]


def _parse_csv(raw: str | None) -> list[str] | None:
    if raw is None:
        return None
    return [s.strip() for s in raw.split(",") if s.strip()]


@app.command()
def init(
    data_dir: DataDirOption = None,
    format: FormatOption = None,  # noqa: A002
    season_start: int = typer.Option(
        1946,
        "--season-start",
        "-s",
        help="Start season year",
    ),
    season_end: int | None = typer.Option(
        None,
        "--season-end",
        "-e",
        help="End season year (default: current)",
    ),
    season_types: SeasonTypesOption = None,
    verbose: VerboseOption = False,
    quality_check: bool = typer.Option(
        False, "--quality-check", help="Run quality checks after pipeline"
    ),
) -> None:
    """Initialize database with full NBA history (resume-safe)."""
    settings = _build_settings(data_dir, format)
    parsed_season_types = _parse_csv(season_types)
    _run_pipeline(
        "init",
        lambda orch: orch.run_init(
            start_season=season_start,
            end_season=season_end,
            season_types=parsed_season_types,
        ),
        settings,
        verbose,
        quality_check,
        orchestrator_cls=Orchestrator,
    )

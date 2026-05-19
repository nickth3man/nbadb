from __future__ import annotations

from dataclasses import dataclass
from typing import Literal

type ExtractionExclusionClass = Literal[
    "permanently_unsupported",
    "upstream_bug_blocked",
    "contract_not_modeled_yet",
    "intentionally_deferred",
]


@dataclass(frozen=True, slots=True)
class ExtractionExclusion:
    endpoint_name: str
    classification: ExtractionExclusionClass
    reason: str
    owner: str
    revalidation_path: str
    scope: str = "full_extraction"

    def to_dict(self) -> dict[str, str]:
        return {
            "endpoint_name": self.endpoint_name,
            "classification": self.classification,
            "reason": self.reason,
            "owner": self.owner,
            "revalidation_path": self.revalidation_path,
            "scope": self.scope,
        }


FULL_EXTRACTION_EXCLUSIONS: tuple[ExtractionExclusion, ...] = (
    ExtractionExclusion(
        endpoint_name="defense_hub",
        classification="contract_not_modeled_yet",
        reason=(
            "DefenseHub is not reliable under the current season sweep contract; it "
            "needs a dedicated endpoint contract before full-history extraction can "
            "schedule its multi-result staging outputs."
        ),
        owner="extract",
        revalidation_path=(
            "Revalidate by running a focused DefenseHub contract probe and adding "
            "endpoint-specific params once the valid request shape is documented."
        ),
    ),
    ExtractionExclusion(
        endpoint_name="matchups_rollup",
        classification="contract_not_modeled_yet",
        reason=(
            "MatchupsRollup is not reliable under the current generic season sweep "
            "contract and requires endpoint-specific validation before full extraction."
        ),
        owner="extract",
        revalidation_path=(
            "Revalidate with a focused MatchupsRollup sample across current and "
            "historical seasons, then encode the supported params in STAGING_MAP."
        ),
    ),
    ExtractionExclusion(
        endpoint_name="player_career_by_college",
        classification="permanently_unsupported",
        reason=(
            "The upstream nba_api integration contract marks PlayerCareerByCollege as "
            "unable to construct a valid request, likely deprecated."
        ),
        owner="extract",
        revalidation_path=(
            "Revalidate only if nba_api restores a working contract or NBA Stats "
            "publishes replacement request parameters."
        ),
    ),
    ExtractionExclusion(
        endpoint_name="shot_chart_lineup",
        classification="contract_not_modeled_yet",
        reason=(
            "ShotChartLineup requires a lineup group_id; that ID is not available in "
            "the current season-pattern sweep."
        ),
        owner="extract",
        revalidation_path=(
            "Add a lineup workload discovery step that persists valid group_id values, "
            "then schedule this endpoint from that workload."
        ),
    ),
    ExtractionExclusion(
        endpoint_name="shot_chart_lineup_detail",
        classification="contract_not_modeled_yet",
        reason=(
            "ShotChartLineupDetail requires a lineup group_id; that ID is not "
            "available in the current season-pattern sweep."
        ),
        owner="extract",
        revalidation_path=(
            "Add a lineup workload discovery step that persists valid group_id values, "
            "then schedule this endpoint from that workload."
        ),
    ),
    ExtractionExclusion(
        endpoint_name="team_historical_leaders",
        classification="upstream_bug_blocked",
        reason=(
            "The live TeamHistoricalLeaders endpoint currently returns invalid JSON for "
            "valid franchise IDs, so full historical extraction is blocked upstream."
        ),
        owner="extract",
        revalidation_path=(
            "Revalidate after nba_api or upstream NBA Stats fixes the response shape for "
            "current franchise IDs."
        ),
    ),
    ExtractionExclusion(
        endpoint_name="team_game_streak_finder",
        classification="contract_not_modeled_yet",
        reason=(
            "TeamGameStreakFinder is not reliable under the current generic season "
            "sweep contract and repeatedly times out for valid recent-season probes."
        ),
        owner="extract",
        revalidation_path=(
            "Revalidate with a focused TeamGameStreakFinder contract probe, then "
            "encode the supported params before scheduling it in full extraction."
        ),
    ),
)

FULL_EXTRACTION_EXCLUSIONS_BY_ENDPOINT: dict[str, ExtractionExclusion] = {
    exclusion.endpoint_name: exclusion for exclusion in FULL_EXTRACTION_EXCLUSIONS
}


def is_full_extraction_excluded(endpoint_name: str) -> bool:
    return endpoint_name in FULL_EXTRACTION_EXCLUSIONS_BY_ENDPOINT


def filter_full_extraction_entries[T](entries: list[T]) -> list[T]:
    return [
        entry
        for entry in entries
        if not is_full_extraction_excluded(str(getattr(entry, "endpoint_name", "")))
    ]

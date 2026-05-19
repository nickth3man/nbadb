from __future__ import annotations

import polars as pl

from nbadb.orchestrate.discovery_artifacts import DiscoveryArtifactScope, DiscoveryArtifactStore


def test_discovery_artifact_store_round_trips_scoped_game_logs(tmp_path) -> None:
    store = DiscoveryArtifactStore.from_duckdb_path(tmp_path / "planner.duckdb")
    scope = DiscoveryArtifactScope(
        kind="league_game_log",
        seasons=("2024-25",),
        season_types=("Regular Season",),
    )
    frame = pl.DataFrame({"game_id": ["001"], "game_date": ["2024-10-22"]})

    store.upsert_frame(scope, frame, provenance="test")

    loaded = store.load_frame(scope)
    assert loaded is not None
    assert loaded.to_dicts() == frame.to_dicts()


def test_discovery_artifact_store_round_trips_entity_ids(tmp_path) -> None:
    store = DiscoveryArtifactStore.from_duckdb_path(tmp_path / "planner.duckdb")
    scope = DiscoveryArtifactScope(
        kind="player_ids_all",
        seasons=("2024-25",),
        variant="historical",
    )

    store.upsert_ids(scope, [3, 1, 3, 2], provenance="test")

    assert store.load_ids(scope) == [1, 2, 3]


def test_discovery_artifact_store_loads_frame_when_manifest_is_missing(tmp_path) -> None:
    store = DiscoveryArtifactStore.from_duckdb_path(tmp_path / "planner.duckdb")
    scope = DiscoveryArtifactScope(
        kind="league_game_log",
        seasons=("2024-25",),
        season_types=("Regular Season",),
    )
    frame = store.upsert_frame(
        scope,
        pl.DataFrame({"game_id": ["001"], "game_date": ["2024-10-22"]}),
        provenance="test",
    )

    manifest_path = store._manifest_path(scope)
    manifest_path.unlink()

    loaded = store.load_frame(scope)
    assert loaded is not None
    assert loaded.to_dicts() == frame.to_dicts()


def test_discovery_artifact_store_reuses_combo_scoped_game_logs_for_narrower_scope(
    tmp_path,
) -> None:
    store = DiscoveryArtifactStore.from_duckdb_path(tmp_path / "planner.duckdb")
    store.upsert_game_log_combo_frames(
        {
            ("2024-25", "Regular Season"): pl.DataFrame(
                {"game_id": ["001"], "game_date": ["2024-10-22"]}
            ),
            ("2024-25", "Playoffs"): pl.DataFrame(),
        },
        provenance="partial-discovery",
    )

    loaded = store.load_game_log_frame(
        DiscoveryArtifactScope(
            kind="league_game_log",
            seasons=("2024-25",),
            season_types=("Regular Season",),
        )
    )

    assert loaded is not None
    assert loaded.to_dicts() == [{"game_id": "001", "game_date": "2024-10-22"}]


def test_discovery_artifact_store_returns_none_when_unavailable() -> None:
    store = DiscoveryArtifactStore.from_duckdb_path(None)
    scope = DiscoveryArtifactScope(kind="league_game_log")

    assert store.load_frame(scope) is None


def test_load_game_log_partial_returns_only_cached_combos(tmp_path) -> None:
    store = DiscoveryArtifactStore.from_duckdb_path(tmp_path / "planner.duckdb")
    # Persist only Regular Season; Playoffs is absent.
    store.upsert_game_log_combo_frames(
        {
            ("2024-25", "Regular Season"): pl.DataFrame(
                {"game_id": ["001"], "game_date": ["2024-10-22"]}
            ),
        },
        provenance="partial-discovery",
    )

    scope = DiscoveryArtifactScope(
        kind="league_game_log",
        seasons=("2024-25",),
        season_types=("Regular Season", "Playoffs"),
    )
    result = store.load_game_log_partial(scope)

    assert set(result.keys()) == {("2024-25", "Regular Season")}
    assert result[("2024-25", "Regular Season")].to_dicts() == [
        {"game_id": "001", "game_date": "2024-10-22"}
    ]


def test_load_game_log_partial_returns_empty_dict_when_nothing_cached(tmp_path) -> None:
    store = DiscoveryArtifactStore.from_duckdb_path(tmp_path / "planner.duckdb")
    scope = DiscoveryArtifactScope(
        kind="league_game_log",
        seasons=("2024-25",),
        season_types=("Regular Season", "Playoffs"),
    )

    assert store.load_game_log_partial(scope) == {}


def test_load_game_log_partial_returns_empty_dict_when_store_unavailable() -> None:
    store = DiscoveryArtifactStore.from_duckdb_path(None)
    scope = DiscoveryArtifactScope(
        kind="league_game_log",
        seasons=("2024-25",),
        season_types=("Regular Season",),
    )

    assert store.load_game_log_partial(scope) == {}


def test_load_game_log_partial_returns_all_combos_when_all_cached(tmp_path) -> None:
    store = DiscoveryArtifactStore.from_duckdb_path(tmp_path / "planner.duckdb")
    store.upsert_game_log_combo_frames(
        {
            ("2024-25", "Regular Season"): pl.DataFrame(
                {"game_id": ["001"], "game_date": ["2024-10-22"]}
            ),
            ("2024-25", "Playoffs"): pl.DataFrame(),
        },
        provenance="partial-discovery",
    )

    scope = DiscoveryArtifactScope(
        kind="league_game_log",
        seasons=("2024-25",),
        season_types=("Regular Season", "Playoffs"),
    )
    result = store.load_game_log_partial(scope)

    assert set(result.keys()) == {("2024-25", "Regular Season"), ("2024-25", "Playoffs")}

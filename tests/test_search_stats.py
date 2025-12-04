import ai.games as games
from game.checkers import Checkers


def test_alphabeta_sets_last_search_stats():
    game = Checkers()
    state = game.curr_state

    # Run your instrumented search
    games.alphabeta_search(state, game, d=2)

    # It should attach a stats dict to the game object
    assert hasattr(game, "last_search_stats")

    stats = game.last_search_stats

    # Basic shape of the stats
    assert isinstance(stats, dict)
    assert stats["depth_limit"] == 2
    assert "max_depth_reached" in stats
    assert "nodes_expanded" in stats
    assert "runtime_sec" in stats

    # Values should be reasonable
    assert stats["max_depth_reached"] >= 1
    # In your implementation, depth can go at most d+1
    assert stats["max_depth_reached"] <= 2 + 1

    assert stats["nodes_expanded"] >= stats["max_depth_reached"]
    assert stats["nodes_expanded"] > 0
    assert stats["runtime_sec"] >= 0.0


def test_alphabeta_stats_update_for_different_depths():
    game = Checkers()
    state = game.curr_state

    games.alphabeta_search(state, game, d=1)
    stats_d1 = game.last_search_stats.copy()

    games.alphabeta_search(state, game, d=2)
    stats_d2 = game.last_search_stats

    # Depth limit should reflect the depth you asked for
    assert stats_d1["depth_limit"] == 1
    assert stats_d2["depth_limit"] == 2

    # The overall stats dict should change between calls
    # (at least because depth_limit changes)
    assert stats_d1 != stats_d2

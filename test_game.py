import pytest

from bowling_game import BowlingGame, BowlingScoreError


# ----------------------------------------------------------------------
# 1. Provided example game
# ----------------------------------------------------------------------

def test_example_game_from_spec():
    rolls = ["8", "/", "5", "4", "9", "0", "X", "X", "5", "/",
             "5", "3", "6", "3", "9", "/", "9", "/", "X"]
    game = BowlingGame(rolls)
    assert game.frame_scores() == [15, 24, 33, 58, 78, 93, 101, 110, 129, 149]
    assert game.total_score() == 149


# ----------------------------------------------------------------------
# 2. Perfect game
# ----------------------------------------------------------------------

def test_perfect_game_is_300():
    game = BowlingGame(["X"] * 12)
    assert game.total_score() == 300
    assert game.frame_scores() == [30, 60, 90, 120, 150, 180, 210, 240, 270, 300]

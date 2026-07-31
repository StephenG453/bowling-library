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


# ----------------------------------------------------------------------
# 3. All spares
# ----------------------------------------------------------------------

def test_all_spares_with_five_bonus_is_150():
    rolls = ["5", "/"] * 10 + ["5"]
    game = BowlingGame(rolls)
    assert game.total_score() == 150


# ----------------------------------------------------------------------
# 4. All open frames
# ----------------------------------------------------------------------

def test_all_open_frames():
    rolls = ["3", "4"] * 10  # 7 pins/frame * 10 = 70
    game = BowlingGame(rolls)
    assert game.total_score() == 70
    assert game.frame_scores() == [7, 14, 21, 28, 35, 42, 49, 56, 63, 70]


def test_all_gutter_balls_is_zero():
    rolls = ["0", "0"] * 10
    game = BowlingGame(rolls)
    assert game.total_score() == 0


# ----------------------------------------------------------------------
# 5. Tenth frame behavior
# ----------------------------------------------------------------------

def test_tenth_frame_strike_plus_two_bonus_rolls():
    rolls = ["3", "4"] * 9 + ["X", "5", "4"]
    game = BowlingGame(rolls)
    # 9 open frames of 7 = 63, plus 10th: 10+5+4 = 19 -> 82
    assert game.total_score() == 82


def test_tenth_frame_spare_plus_one_bonus_roll():
    rolls = ["3", "4"] * 9 + ["5", "/", "7"]
    game = BowlingGame(rolls)
    # 63 + (10th: 5+5+7=17) = 80
    assert game.total_score() == 80


def test_tenth_frame_open_frame_ends_game_no_bonus():
    rolls = ["3", "4"] * 9 + ["5", "3"]
    game = BowlingGame(rolls)
    # 63 + 8 = 71
    assert game.total_score() == 71


def test_tenth_frame_three_strikes():
    rolls = ["3", "4"] * 9 + ["X", "X", "X"]
    game = BowlingGame(rolls)
    assert game.total_score() == 63 + 30


# ----------------------------------------------------------------------
# 6. Validation tests
# ----------------------------------------------------------------------

def test_spare_as_first_roll_of_frame_is_invalid():
    with pytest.raises(BowlingScoreError):
        BowlingGame(["/", "5"] + ["3", "4"] * 9)


def test_invalid_character_is_rejected():
    with pytest.raises(BowlingScoreError):
        BowlingGame(["Q", "4"] + ["3", "4"] * 9)


def test_too_many_rolls_in_tenth_frame_is_rejected():
    with pytest.raises(BowlingScoreError):
        BowlingGame(["3", "4"] * 9 + ["X", "5", "4", "2"])


def test_frame_pin_count_exceeding_ten_without_spare_is_rejected():
    with pytest.raises(BowlingScoreError):
        BowlingGame(["6", "5"] + ["3", "4"] * 9)


def test_extra_rolls_after_game_completion_is_rejected():
    with pytest.raises(BowlingScoreError):
        BowlingGame(["3", "4"] * 10 + ["5"])


def test_tenth_frame_spare_cannot_be_followed_by_spare_bonus():
    # bonus roll after a 10th-frame spare has nothing before it to complete
    with pytest.raises(BowlingScoreError):
        BowlingGame(["3", "4"] * 9 + ["5", "/", "/"])


def test_tenth_frame_open_frame_cannot_take_extra_roll():
    with pytest.raises(BowlingScoreError):
        BowlingGame(["3", "4"] * 9 + ["5", "3", "2"])


def test_non_list_input_is_rejected():
    with pytest.raises(BowlingScoreError):
        BowlingGame("X" * 12)  # a string, not a list


# --------------------------------------------------------------
# some parameterized scenarios
# --------------------------------------------------------------------

@pytest.mark.parametrize(
    "rolls, expected_total",
    [
        (["X"] * 12, 300),
        (["5", "/"] * 10 + ["5"], 150),
        (["3", "4"] * 10, 70),
        (["0", "0"] * 10, 0),
        (["3", "4"] * 9 + ["5", "3"], 71),
    ],
)
def test_various_full_games(rolls, expected_total):
    assert BowlingGame(rolls).total_score() == expected_total


@pytest.mark.parametrize(
    "bad_rolls",
    [
        ["/", "5"] + ["3", "4"] * 9,
        ["Q", "4"] + ["3", "4"] * 9,
        ["3", "4"] * 9 + ["X", "5", "4", "2"],
        ["6", "5"] + ["3", "4"] * 9,
        ["3", "4"] * 10 + ["5"],
    ],
)
def test_various_invalid_games_raise(bad_rolls):
    with pytest.raises(BowlingScoreError):
        BowlingGame(bad_rolls)

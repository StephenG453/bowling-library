"""
Bowling game scorer.

Input format (Option B — flat list of rolls), e.g.:

    ["8", "/", "5", "4", "9", "0", "X", "X", "5", "/",
     "5", "3", "6", "3", "9", "/", "9", "/", "X"]

Valid roll symbols:
    "X" or "x"  -> strike
    "/"         -> spare (fills the remaining pins of the current sub-frame)
    "0"..."9"   -> number of pins knocked down on that roll

"""

from typing import List, Optional, Union

Roll = str
Score = Optional[int]

STRIKE_SYMBOLS = {"X", "x"}
SPARE_SYMBOL = "/"
DIGIT_SYMBOLS = set("0123456789")
VALID_SYMBOLS = STRIKE_SYMBOLS | {SPARE_SYMBOL} | DIGIT_SYMBOLS

class BowlingGame:
    """
    Parses and scores a single game of ten-pin bowling from a flat list
    of roll symbols.

    Usage:
        game = BowlingGame(["8", "/", "5", "4", ...])
        game.frame_scores()      # -> [15, 24, 33, ...] (cumulative, len<=10)
        game.total_score()       # -> final score (int), or None if incomplete

    Raises BowlingScoreError (a ValueError subclass) for any invalid input.
    Incomplete-but-otherwise-valid games are allowed: frames that cannot
    yet be scored (because bonus rolls haven't happened) report `None` in
    frame_scores(), rather than raising.
    """

    def __init__(self, rolls: List[Roll]):
        self.rolls: List[Roll] = list(rolls)

        self.frame_roll_start: List[Optional[int]] = [None] * 10
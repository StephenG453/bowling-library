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

class BowlingScoreError(ValueError):
    """Raised when an input roll sequence is not a valid bowling game."""

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

        # ------------------------------------------------------------------
        # Validation / parsing
        # ------------------------------------------------------------------

        @staticmethod
        def _validate_symbols(rolls: List[Roll]) -> None:
            if not isinstance(rolls, list):
                raise BowlingScoreError("Rolls must be provided as a list of strings.")
            for idx, r in enumerate(rolls):
                if not isinstance(r, str) or r not in VALID_SYMBOLS:
                    raise BowlingScoreError(
                        f"Invalid roll symbol {r!r} at position {idx}. "
                        f"Expected one of X/x (strike), '/' (spare), or a digit 0-9."
                    )

        def _parse(self, rolls: List[Roll]) -> List[Optional[List[int]]]:
            frames: List[Optional[List[int]]] = []
            pointer = 0
            n = len(rolls)

            for frame_num in range(1, 11):
                if pointer >= n:
                    frames.append(None)
                    continue

                self.frame_roll_start[frame_num - 1] = pointer

                if frame_num < 10:
                    pointer = self._parse_regular_frame(rolls, pointer, frame_num, frames)
                else:
                    pointer = self._parse_tenth_frame(rolls, pointer, frames)

            if pointer < n:
                raise BowlingScoreError(
                    "Extra rolls found after the game was already complete "
                    f"(unused rolls starting at position {pointer}: {rolls[pointer:]})."
                )

            return frames
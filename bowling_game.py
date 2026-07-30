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

def _is_strike(roll: Roll) -> bool:
    return roll in STRIKE_SYMBOLS


def _digit_value(roll: Roll, context: str) -> int:
    if roll not in DIGIT_SYMBOLS:
        raise BowlingScoreError(
            f"Invalid roll symbol {roll!r} {context}. "
            f"Expected one of X/x (strike), '/' (spare), or a digit 0-9."
        )
    return int(roll)

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


    def _parse_regular_frame(self, rolls, pointer, frame_num, frames) -> int:
        n = len(rolls)
        roll_1 = rolls[pointer]

        if roll_1 == SPARE_SYMBOL:
            raise BowlingScoreError(
                f"Frame {frame_num}: a spare ('/') cannot be the first roll of a frame "
                f"(position {pointer})."
            )

        if _is_strike(roll_1):
            frames.append([10])
            return pointer + 1

        pins_1 = _digit_value(roll_1, f"as first roll of frame {frame_num}")
        pointer += 1

        if pointer >= n:
            # Frame started but not finished yet -> partial game.
            frames.append(None)
            return pointer

        roll_2 = rolls[pointer]
        if roll_2 == SPARE_SYMBOL:
            pins_2 = 10 - pins_1
            frames.append([pins_1, pins_2])
        else:
            pins_2 = _digit_value(roll_2, f"as second roll of frame {frame_num}")
            if pins_1 + pins_2 > 10:
                raise BowlingScoreError(
                    f"Frame {frame_num}: pin total {pins_1}+{pins_2} exceeds 10 "
                    f"and the second roll is not marked as a spare ('/')."
                )
            frames.append([pins_1, pins_2])
        return pointer + 1


    def _parse_tenth_frame(self, rolls, pointer, frames) -> int:
        n = len(rolls)

        def take():
            nonlocal pointer
            v = rolls[pointer]
            pointer += 1
            return v

        roll_1 = take()
        if roll_1 == SPARE_SYMBOL:
            raise BowlingScoreError(
                "Frame 10: a spare ('/') cannot be the first roll of the frame."
            )

        if _is_strike(roll_1):
            pins = [10]
            if pointer >= n:
                frames.append(None)
                return pointer
            roll_2 = take()
            if roll_2 == SPARE_SYMBOL:
                raise BowlingScoreError(
                    "Frame 10: a spare ('/') cannot immediately follow a strike "
                    "with no prior roll to complete."
                )
            pins_2 = 10 if _is_strike(roll_2) else _digit_value(roll_2, "as bonus roll 2 of frame 10")
            pins.append(pins_2)

            if pointer >= n:
                frames.append(None)
                return pointer
            roll_3 = take()
            if _is_strike(roll_2):
                # Pins reset after a strike; roll_3 stands alone (can't be a spare).
                if roll_3 == SPARE_SYMBOL:
                    raise BowlingScoreError(
                        "Frame 10: a spare ('/') cannot be the first roll after "
                        "a reset (following back-to-back strikes)."
                    )
                pins_3 = 10 if _is_strike(roll_3) else _digit_value(roll_3, "as bonus roll 3 of frame 10")
            else:
                if roll_3 == SPARE_SYMBOL:
                    pins_3 = 10 - pins_2
                else:
                    pins_3 = 10 if _is_strike(roll_3) else _digit_value(roll_3, "as bonus roll 3 of frame 10")
                    if pins_2 + pins_3 > 10:
                        raise BowlingScoreError(
                            f"Frame 10: bonus pin total {pins_2}+{pins_3} exceeds 10 "
                            f"and the roll is not marked as a spare ('/')."
                        )
            pins.append(pins_3)
            frames.append(pins)
            return pointer

        # roll_1 is a plain digit roll.
        pins_1 = _digit_value(roll_1, "as first roll of frame 10")
        if pointer >= n:
            frames.append(None)
            return pointer
        roll_2 = take()

        if roll_2 == SPARE_SYMBOL:
            pins_2 = 10 - pins_1
            pins = [pins_1, pins_2]
            if pointer >= n:
                frames.append(None)
                return pointer
            roll_3 = take()
            if roll_3 == SPARE_SYMBOL:
                raise BowlingScoreError(
                    "Frame 10: a spare ('/') cannot be the bonus roll with no "
                    "prior roll in that sub-frame to complete."
                )
            pins_3 = 10 if _is_strike(roll_3) else _digit_value(roll_3, "as bonus roll of frame 10")
            pins.append(pins_3)
            frames.append(pins)
            return pointer
        else:
            pins_2 = _digit_value(roll_2, "as second roll of frame 10")
            if pins_1 + pins_2 > 10:
                raise BowlingScoreError(
                    f"Frame 10: pin total {pins_1}+{pins_2} exceeds 10 and the "
                    f"second roll is not marked as a spare ('/')."
                )
            # Open frame -> game ends here, no bonus roll allowed.
            frames.append([pins_1, pins_2])
            return pointer
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
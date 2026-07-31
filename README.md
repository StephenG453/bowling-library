# Bowling Game Scorer

A small, dependency-free Python library that scores a ten-pin bowling game
from a list of roll symbols, with strict input validation and a full pytest
suite.

## Input format

This implementation uses Option B: flat list of rolls. This is a single flat
list of roll symbols in the order they were bowled.

```python
["8", "/", "5", "4", "9", "0", "X", "X", "5", "/",
 "5", "3", "6", "3", "9", "/", "9", "/", "X"]
```

**Valid symbols:**

| Symbol        | Meaning                                   |
|---------------|--------------------------------------------|
| `"X"` / `"x"` | Strike                                   |
| `"/"`         | Spare (completes the frame to 10 pins)   |
| `"0"`-`"9"`   | Number of pins knocked down on that roll |

**Why flat rolls?** It mirrors how a game is actually bowled (one
continuous roll stream), and it makes the parser/validator a single linear
scan with a pointer, which is easier to reason about and to unit test than
juggling nested list shapes.

## Usage

```python
from bowling_game import BowlingGame

rolls = ["8", "/", "5", "4", "9", "0", "X", "X", "5", "/",
         "5", "3", "6", "3", "9", "/", "9", "/", "X"]

game = BowlingGame(rolls)
game.frame_scores()  # [15, 24, 33, 58, 78, 93, 101, 110, 129, 149]
game.total_score()  # 149
game.is_complete()  # True
```

`frame_scores()` always returns exactly 10 values: the cumulative score at
the end of each frame.

## Partial games

A game does not have to be complete. If a frame can't be scored yet because
a required bonus roll hasn't been thrown (or the frame itself hasn't been
fully rolled), that frame, and every frame after it, reports `None`
instead of raising an error:

```python
BowlingGame(["8", "/", "5"]).frame_scores()
# [15, None, None, None, None, None, None, None, None, None]
# Frame 1 (spare) resolves once its bonus roll (5) is thrown.
# Frames 2-10 haven't happened yet.

BowlingGame(["3", "4"]).frame_scores()
# [7, None, None, None, None, None, None, None, None, None]
```

`game.is_complete()` returns `True` once the 10th frame's cumulative score
is known.

## Scoring rules implemented

- **Strike**: 10 + the pins knocked down on the next two rolls.
- **Spare**: 10 + the pins knocked down on the next one roll.
- **Open frame**: the number of pins knocked down in that frame.
- **10th frame**: strike on roll 1 -> two bonus rolls; spare on rolls 1-2 ->
  one bonus roll; open frame -> the game ends there. The 10th frame's score
  is simply the total pins knocked down in it (including bonus rolls).

## Validation

`BowlingGame(...)` raises `bowling_game.BowlingScoreError` (a `ValueError`
subclass) for any structurally invalid game, including:

- An invalid symbol (anything other than `X`/`x`, `/`, or `0`-`9`).
- A spare (`/`) as the first roll of a frame.
- A frame whose pin total exceeds 10 without
  the second roll being marked as a spare.
- Extra rolls beyond what a complete game allows (e.g. a 4th roll in the
  10th frame, or any roll after an open 10th frame).
- 10th-frame bonus rolls that weren't earned (i.e., taking a 3rd roll after
  an open non-strike, non-spare 10th frame).

Non-list input is also rejected.

## Assumptions

- Pin counts per roll are single characters (`"0"`-`"9"`); the "10" value
  is always expressed as `"X"` for a strike, never as the literal string
  `"10"`.
- Consecutive `"/"` symbols are never valid, since a spare must always
  immediately follow the single digit roll it completes.
- Games may be partial (fewer than 21 rolls); they may not have gaps,
  duplicate frames, or extra trailing rolls once the frame structure they
  imply is already complete.

## Project layout

```
bowling-library/
├── src/
│   └── bowling_game.py   # parsing, validation, and scoring logic (BowlingGame, BowlingScoreError)
├── tests/
│   └── test_game.py      # pytest suite
├── pytest.ini             # tells pytest to add src/ to the import path
├── README.md
└── requirements.txt
```

`src/bowling_game.py` is importable in tests as `bowling_game` (not
`src.bowling_game`) because `pytest.ini` adds `src/` directly to the
import path.

## Running the tests

```bash
pip install -r requirements.txt
pytest -v
```

This works because `pytest.ini` at the project root contains:

```ini
[pytest]
pythonpath = src
```

which tells pytest to add `src/` to `sys.path` before collecting tests, so
`tests/test_game.py`'s `from bowling_game import BowlingGame,
BowlingScoreError` resolves without needing the package installed or any
`sys.path` hacks in the test file itself.

Test coverage includes:

- The example game from the email spec (`[15, 24, 33, 58, 78, 93, 101, 110, 129, 149]`)
- A perfect game (300)
- All spares with a 5-pin bonus (150)
- All open frames, including all gutter balls
- All 10th-frame variants (strike+2 bonus, spare+1 bonus, open/no-bonus,
  three strikes)
- 8 validation tests (invalid symbol, spare-as-first-roll, over-10 frame
  total, too many/unearned 10th-frame rolls, extra rolls after game
  completion, non-list input)
- Parameterized full-game and invalid-game scenarios
- Partial-game / `None`-scoring behavior, including the tricky case where a
  strike's or spare's bonus lookahead must reach into a frame that itself
  isn't complete yet

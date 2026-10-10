"""ops 模块的单元测试。运行：uv run pytest"""

from __future__ import annotations

import pytest

from src.calc.ops import add, divide, subtract


def test_add() -> None:
    assert add(2, 3) == 5
    assert add(-1, 1) == 0


def test_subtract() -> None:
    assert subtract(10, 4) == 6
    assert subtract(2, 5) == -3


def test_divide() -> None:
    assert divide(9, 3) == pytest.approx(3.0)


def test_divide_by_zero_raises() -> None:
    with pytest.raises(ZeroDivisionError):
        divide(1, 0)


# ---------------------------------------------------------------------------
# TODO(10-10 ③做)：给 power 和 average 各补 1 个测试
#   test_power         -> assert power(2, 3) == 8
#   test_average       -> assert average([1, 2, 3]) == 2.0
#   test_average_empty -> with pytest.raises(ValueError): average([])
# ---------------------------------------------------------------------------

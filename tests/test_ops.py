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


# --- 上面是旧 TODO，下面是今天的验收标准（导师写的）：把 ops.py 里这两个函数补上 ---
# 参考黑马 Python 进阶里的函数定义章节，重点是多返回值/异常这两个约定。

try:
    from src.calc.ops import average, power
except ImportError:
    power = average = None  # type: ignore[assignment]

_needs_impl = pytest.mark.skipif(power is None, reason="先实现 ops.power / ops.average")


@_needs_impl
def test_power() -> None:
    assert power(2, 3) == 8
    assert power(4, 0.5) == 2.0
    assert power(2, -1) == 0.5


@_needs_impl
def test_average() -> None:
    assert average([1, 2, 3]) == 2.0
    assert average([10]) == 10.0
    assert average([-1, 1]) == 0.0


@_needs_impl
def test_average_empty_raises() -> None:
    with pytest.raises(ValueError):
        average([])

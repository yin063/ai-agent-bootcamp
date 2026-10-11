"""decorators 的验收标准（导师写的，别改）。

现在全是红的，等你把 src/utils/decorators.py 里的 timer 填完就该全绿。
"""

from __future__ import annotations

import logging
import time

import pytest

from src.utils.decorators import timer


def test_timer_returns_original_value() -> None:
    @timer
    def add(a: float, b: float) -> float:
        return a + b

    assert add(2, 3) == 5


def test_timer_keeps_function_metadata() -> None:
    @timer
    def heavy_job() -> str:
        """这是原始 docstring。"""
        return "done"

    assert heavy_job() == "done"
    assert heavy_job.__name__ == "heavy_job"
    assert heavy_job.__doc__ == "这是原始 docstring。"


def test_timer_works_with_args_and_kwargs() -> None:
    @timer
    def mul(a: float, scale: float = 2.0) -> float:
        return a * scale

    assert mul(5) == 10
    assert mul(5, scale=3) == 15


def test_timer_actually_costs_time() -> None:
    @timer
    def slow() -> int:
        time.sleep(0.05)
        return 1

    start = time.perf_counter()
    assert slow() == 1
    assert time.perf_counter() - start >= 0.05


def test_timer_logs_cost(caplog: pytest.LogCaptureFixture) -> None:
    @timer
    def work(x: int) -> int:
        return x * 2

    with caplog.at_level(logging.INFO):
        work(4)

    text = caplog.text
    assert "work" in text, f"日志里要能看到函数名，实际：{text!r}"
    assert any(ch.isdigit() for ch in text), f"日志里要能看到耗时数字，实际：{text!r}"

"""itertools_tools 的验收标准（导师写的，别改）。

重点是 test_chunked_is_lazy：那条能过，说明你写的是真生成器，不是 list。
"""

from __future__ import annotations

import itertools

import pytest

from src.utils.itertools_tools import chunked


def test_chunked_basic() -> None:
    assert list(chunked([1, 2, 3, 4, 5], 2)) == [[1, 2], [3, 4], [5]]


def test_chunked_size_equals_length() -> None:
    assert list(chunked([1, 2, 3], 3)) == [[1, 2, 3]]


def test_chunked_size_bigger_than_length() -> None:
    assert list(chunked([1, 2], 10)) == [[1, 2]]


def test_chunked_empty_input() -> None:
    assert list(chunked([], 3)) == []


def test_chunked_rejects_bad_size() -> None:
    for bad in (0, -1):
        with pytest.raises(ValueError):
            list(chunked([1, 2, 3], bad))


def test_chunked_is_lazy() -> None:
    """喂一个无限序列，只要它能吐出第一批，就证明没被一次性读完。"""
    infinite = itertools.count()
    first_batch = next(iter(chunked(infinite, 3)))
    assert first_batch == [0, 1, 2]

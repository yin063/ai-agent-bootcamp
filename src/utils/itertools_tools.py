"""惰性工具：生成器版本。

凡是"数据量大 / 来源可能是流式"的场景一律用生成器，
Agent 里读日志、读设备采样、分页拉接口都是这类。

先钩 stub 再填实现：pytest 现在是红的，把注释里的要求读完填上就会变绿。
"""

from __future__ import annotations

from collections.abc import Iterable, Iterator
from typing import TypeVar

T = TypeVar("T")


def chunked(seq: Iterable[T], size: int) -> Iterator[list[T]]:
    """把序列按 size 切成一批一批，惰性产出，最后一批可以不足 size。

    size <= 0 抛 ValueError。
    必须是惰性的：传入无限序列时也能取出第一批。
    """
    # TODO(10-11 ③做)：删掉下面这行，换成你自己的实现
    #   1. 先校验 size：if size <= 0: raise ValueError(...)
    #   2. batch = [] ；for item in seq:  append → 满 size 就 yield batch 并清空
    #   3. 循环结束 batch 里还有剩 → yield batch
    #   看不懂先看：BV1U2WmzfEqp P98（迭代器 22min）→ P100（yield 5min）
    raise NotImplementedError("TODO: 实现 chunked")


def take(seq: Iterable[T], n: int) -> Iterator[T]:
    """只取前 n 个元素就停，不读完整个序列（弹性题）。"""
    # TODO(10-11 弹性)：for i, item in enumerate(seq): 到 n 就 break
    raise NotImplementedError("TODO: 实现 take")

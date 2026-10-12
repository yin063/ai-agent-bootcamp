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
    # ① 先挡掉非法 size：写了 yield 的函数，函数体要等第一次 next() 才跑，
    #    但 list(chunked(...)) 会触发迭代，所以这里照样能抛出去。
    if size <= 0:
        raise ValueError(f"size must be positive, got {size}")

    batch: list[T] = []
    for item in seq:
        batch.append(item)
        # ② 攒满一批就 yield：函数在这里"暂停"，外面拿到这批数据
        if len(batch) == size:
            yield batch
            # ③ 必须新建列表，不能 batch.clear()。
            #    yield 交出去的是同一个对象的引用，clear 会把外面那份也清空。
            batch = []
    # ④ 收尾：最后一批不足 size 的别丢
    if batch:
        yield batch


def take(seq: Iterable[T], n: int) -> Iterator[T]:
    """只取前 n 个元素就停，不读完整个序列（弹性题）。"""
    # 数到第 n 个就 break —— 不去读后面，所以无限序列也不会卡死
    for i, item in enumerate(seq):
        if i >= n:
            break
        yield item

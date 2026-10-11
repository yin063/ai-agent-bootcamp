"""上下文管理器的验收标准（导师写的，别改）。

核心就一件事：**出了 with 块，资源必须被关掉，哪怕中间抛了异常**。
Agent 里连数据库、连设备、开文件都是这个模式——漏关一次就是线上泄漏。
"""

from __future__ import annotations

import pytest

context = pytest.importorskip("src.utils.context")

device_session = getattr(context, "device_session", None)
FakeDeviceSession = getattr(context, "FakeDeviceSession", None)

pytestmark = pytest.mark.skipif(
    device_session is None,
    reason="先在 src/utils/context.py 里实现 FakeDeviceSession 和 device_session",
)


def test_closes_on_normal_exit() -> None:
    """正常退出 with 块 → closed 必须是 True。"""
    with device_session("dev-001") as session:
        assert session.device_id == "dev-001"
        assert session.closed is False
    assert session.closed is True


def test_closes_even_when_exception() -> None:
    """抛异常也要关 —— 这是上下文管理器存在的唯一理由。"""
    session = None
    with pytest.raises(RuntimeError):
        with device_session("dev-002") as s:
            session = s
            raise RuntimeError("设备读数失败")
    assert session is not None
    assert session.closed is True, "异常路径没关资源，这是最典型的 bug"


def test_yields_a_usable_session() -> None:
    """with ... as x 拿到的对象必须能干活（这里模拟读一次数）。"""
    with device_session("dev-003") as session:
        assert session.read() == {"device_id": "dev-003", "connected": True}


def test_double_close_is_safe() -> None:
    """重复关一次不能炸（真实驱动经常这么调）。"""
    with device_session("dev-004") as session:
        pass
    session.close()
    assert session.closed is True

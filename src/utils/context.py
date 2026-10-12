"""上下文管理器：设备会话。

为什么需要它：连设备 = 借资源，用完必须还。手写 try/finally 容易漏，
with 语句把"还"这件事绑定到代码块结束上，异常也跑不掉。

约定：进入 with 建立会话，退出时**无论是否异常**都调用 close()。

先钩 stub 再填实现：tests/test_context.py 现在整组 skip，把函数补上就会跑起来。
"""

from __future__ import annotations

from collections.abc import Iterator
from contextlib import contextmanager

from src.utils.logger import get_logger

logger = get_logger(__name__)


class FakeDeviceSession:
    """假的设备连接，用来验证"退出必关"这件事（不碰真实硬件）。"""

    def __init__(self, device_id: str) -> None:
        self.device_id = device_id
        self.closed = False
        logger.info("session opened: %s", device_id)

    def read(self) -> dict[str, object]:
        """模拟读一次数。已关闭的会话应该报错（真实驱动也这样）。"""
        if self.closed:
            raise RuntimeError("session already closed")
        return {"device_id": self.device_id, "connected": True}

    def close(self) -> None:
        """关连接。重复调用要安全（幂等），不能抛异常。"""
        # 幂等：关一次和关十次结果一样，重复调用不报错
        self.closed = True
        logger.info("session closed: %s", self.device_id)


@contextmanager
def device_session(device_id: str) -> Iterator[FakeDeviceSession]:
    """用法：with device_session("PUMP-001") as s: s.read()

    关键：close() 必须放在 finally 里，否则抛异常时不执行。
    """
    session = FakeDeviceSession(device_id)
    try:
        yield session  # 停在 with 块内部
    finally:
        # 这一行是整个练习的答案：finally 里的代码，抛异常也一定会执行
        session.close()

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
        # TODO(10-12 ③做)：
        #   1. if self.closed: raise RuntimeError("session already closed")
        #   2. return {"device_id": self.device_id, "connected": True}
        raise NotImplementedError("TODO: 实现 read")

    def close(self) -> None:
        """关连接。重复调用要安全（幂等），不能抛异常。"""
        # TODO(10-12 ③做)：
        #   self.closed = True
        #   可选：logger.info("session closed: %s", self.device_id)
        raise NotImplementedError("TODO: 实现 close")


@contextmanager
def device_session(device_id: str) -> Iterator[FakeDeviceSession]:
    """用法：with device_session("PUMP-001") as s: s.read()

    关键：close() 必须放在 finally 里，否则抛异常时不执行。
    """
    # TODO(10-12 ③做)：删掉下面这行，按骨架填
    #   session = FakeDeviceSession(device_id)
    #   try:
    #       yield session
    #   finally:
    #       session.close()          # ← 这一行是整个练习的答案
    #
    # 看不懂先看：BV1h4411Q7QP P23「with、上下文管理器」19 min
    #   https://www.bilibili.com/video/BV1h4411Q7QP
    # 文档：https://docs.python.org/zh-cn/3/library/contextlib.html
    raise NotImplementedError("TODO: 实现 device_session")

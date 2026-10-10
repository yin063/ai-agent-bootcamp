"""全项目统一的日志出口。

为什么这么写：
1. 用 %s 占位符而不是 f-string —— 日志级别关掉时不会产生字符串拼接开销。
2. 不加重复 handler —— 否则每调用一次就多打一行。
3. 所有模块都通过 get_logger(__name__) 拿，以后要接文件/JSON 只改这一个地方。
"""

from __future__ import annotations

import logging
import sys

_LOG_FORMAT = "%(asctime)s | %(levelname)-7s | %(name)s | %(message)s"
_DATE_FORMAT = "%H:%M:%S"

_configured = False


def get_logger(name: str = "app") -> logging.Logger:
    global _configured
    if not _configured:
        handler = logging.StreamHandler(sys.stdout)
        handler.setFormatter(logging.Formatter(_LOG_FORMAT, datefmt=_DATE_FORMAT))
        root = logging.getLogger()
        root.setLevel(logging.INFO)
        root.addHandler(handler)
        _configured = True
    return logging.getLogger(name)

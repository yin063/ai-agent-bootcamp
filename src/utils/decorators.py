"""装饰器工具。

约定：装饰器必须保留原函数的返回值和元信息（__name__ / __doc__），
否则被装饰的工具函数在 Agent 里会因为签名丢失而调用失败。

先钩 stub 再填实现：pytest 现在是红的，把注释里的要求读完填上就会变绿。
"""


import functools
import time

from src.utils.logger import get_logger

logger = get_logger(__name__)


def timer(func):
    """给任意函数加计时日志，返回 wrapper。"""

    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        start = time.perf_counter()
        result = func(*args, **kwargs)
        cost = time.perf_counter() - start
        logger.info("%s cost %.4fs", func.__name__, cost)
        return result

    return wrapper

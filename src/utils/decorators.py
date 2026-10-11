"""装饰器工具。

约定：装饰器必须保留原函数的返回值和元信息（__name__ / __doc__），
否则被装饰的工具函数在 Agent 里会因为签名丢失而调用失败。

先钩 stub 再填实现：pytest 现在是红的，把注释里的要求读完填上就会变绿。
"""

# TODO(10-11 ③做)：实现前先把这几个 import 加回来
#   import functools
#   import time
#   from src.utils.logger import get_logger


def timer(func):
    """给任意函数加计时日志，返回 wrapper。

    要求：
    1. 被装饰的函数照常返回原返回值
    2. 执行完打一行 INFO 日志，包含函数名和耗时（秒）
    3. 用 functools.wraps 保住 __name__ 和 __doc__
    """
    # TODO(10-11 ③做)：删掉下面这行，换成你自己的实现
    #   日志对象这样拿：from src.utils.logger import get_logger → get_logger(__name__)
    #   骨架：
    #       @functools.wraps(func)
    #       def wrapper(*args, **kwargs):
    #           start = time.perf_counter()
    #           result = func(*args, **kwargs)      # 别忘 return
    #           cost = time.perf_counter() - start
    #           logger.info("%s cost %.4fs", func.__name__, cost)
    #           return result
    #       return wrapper
    #   看不懂先看：BV1U2WmzfEqp P55（传统写法 28min）→ P56（语法糖 5min）
    raise NotImplementedError("TODO: 实现 timer")

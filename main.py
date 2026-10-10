"""项目入口：从根目录运行 `python main.py`。

注意：不要写 `python src/calc/ops.py`，会报
"attempted relative import with no known parent package"。
src 布局下必须从项目根启动。
"""

from __future__ import annotations

from src.calc.ops import add, divide, subtract
from src.utils.logger import get_logger

logger = get_logger("main")


def main() -> None:
    logger.info("=== ai-agent-bootcamp 启动 ===")
    print("add(2, 3)      =", add(2, 3))
    print("subtract(10, 4)=", subtract(10, 4))
    print("divide(9, 3)   =", divide(9, 3))
    try:
        divide(1, 0)
    except ZeroDivisionError as exc:
        logger.warning("捕获到预期异常：%s", exc)
    logger.info("=== 运行结束 ===")


if __name__ == "__main__":
    main()

"""W1 Day1 验收脚本：类型注解 + logging + main 守卫。"""
import logging

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
)
logger = logging.getLogger(__name__)


def add(a: int, b: int) -> int:
    """返回两数之和。"""
    result = a + b
    logger.info("add(%d, %d) = %d", a, b, result)
    return result


if __name__ == "__main__":
    add(2, 3)

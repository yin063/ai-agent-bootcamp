"""异步并发小工具（D9 · 10-16 ③做）

为什么需要这个模块 —— 直接对应阶段 4 的债：
10-13 那个 Streamlit 聊天机器人的流式输出是**同步**写的。到阶段 4 做 FastAPI + SSE 时，
同一个流式必须用**异步生成器**重写。现在先在这里把 async 的肌肉练出来。

场景：设备巡检 —— 并发拉取 N 台特种设备的状态。
同步写法要等 N × 单台耗时；并发写法只等 最慢的那台。
"""

from __future__ import annotations

import asyncio  # noqa: F401 —— 填完 probe_all 后这行就会被真正用到
from dataclasses import dataclass


@dataclass
class DeviceStatus:
    """一台设备的巡检结果。"""

    device_id: str
    status: str  # "ok" | "timeout"
    latency: float


async def probe_device(device_id: str, delay: float = 0.1) -> DeviceStatus:
    """模拟探测一台设备（真实情况下这里是 HTTP 请求）。

    TODO(10-16 ③做)：
    1. 记下开始时间 `start = asyncio.get_running_loop().time()`
    2. `await asyncio.sleep(delay)` —— 这一句是"让出控制权"的关键，
       换成 `time.sleep(delay)` 就不会有并发了，想想为什么
    3. 返回 `DeviceStatus(device_id, "ok", latency)`，
       latency 用 `round(now - start, 3)`（保留 3 位小数，否则断言浮点会不稳）

    为什么用 `asyncio.get_running_loop().time()` 而不是 `time.time()`：
    前者是单调时钟，系统时间被改也不会倒流。
    """
    raise NotImplementedError("TODO(10-16 ③做)：实现 probe_device")


async def probe_all(
    device_ids: list[str],
    *,
    delay: float = 0.1,
    limit: int = 3,
    timeout: float | None = None,
) -> list[DeviceStatus]:
    """并发探测多台设备，结果**按入参顺序**返回（不是按完成顺序）。

    TODO(10-16 ③做)：
    1. 建一个 `sem = asyncio.Semaphore(limit)`，把并发数压住
       —— 不加限流，100 台设备会瞬间打出 100 个连接，真实场景会被对方封 IP
    2. 内部定义一个协程 `async def _one(device_id)`：
       ```
       async with sem:
           return await probe_device(device_id, delay)
       ```
       注意 `async with` 包住的是 **await 之前**的那一刻，限的是"同时在跑的数量"
    3. `results = await asyncio.gather(*[_one(d) for d in device_ids])`
       —— 空列表要能直接返回 `[]`，别让它炸
    4. 超时：`timeout` 不为 None 时，用 `asyncio.timeout(timeout)` 包住 gather，
       抛 `TimeoutError` 就整体返回 `[DeviceStatus(d, "timeout", 0.0) for d in device_ids]`

    坑位提醒：
    - `asyncio.gather` 返回的**顺序**和传入顺序一致，这一点是它比 `as_completed` 好用的地方
    - `asyncio.timeout` 是 3.11+ 的写法，别写成老的 `asyncio.wait_for`（已被标记遗留）
    """
    raise NotImplementedError("TODO(10-16 ③做)：实现 probe_all")


async def aiter_probe_results(
    device_ids: list[str],
    *,
    delay: float = 0.1,
    limit: int = 3,
):
    """异步生成器：谁先探测完就先吐谁（**完成顺序**，不是入参顺序）。

    这就是阶段 4 要的 SSE 骨架 —— FastAPI 里 `for chunk in aiter_probe_results(...)`，
    每 yield 一个就推给前端一条，前端不用等全部跑完。

    TODO(10-16 ③做)：
    1. `sem = asyncio.Semaphore(limit)`
    2. 用 `asyncio.as_completed(...)` 遍历任务，**每完成一个就 `yield await task`**
       写法：
       ```
       tasks = [asyncio.create_task(_one(d)) for d in device_ids]
       for coro in asyncio.as_completed(tasks):
           yield await coro
       ```
    3. 内部 `_one` 同样要过 `sem`

    为什么必须 `create_task` 先建任务再 `as_completed`：
    直接把协程对象丢给 `as_completed` 在 3.11+ 已废弃，且无法控制并发起点。
    """
    raise NotImplementedError("TODO(10-16 ③做)：实现 aiter_probe_results")
    yield  # pragma: no cover —— 让 Python 认定这是个生成器函数

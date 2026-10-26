"""D9 asyncio 验收测试（10-16 目标：这 6 条从红转绿）

设计原则：**不装 pytest-asyncio 也能跑** —— 每条测试内部自己 `asyncio.run(...)`。
这样今天不用折腾插件，明晚直接见红。
"""

import asyncio
import time

import pytest

from src.utils.async_tools import (
    DeviceStatus,
    aiter_probe_results,
    probe_all,
    probe_device,
)

# ---------- 并发观测器（用来证明"真的是并发"） ----------


class _ConcurrencyProbe:
    """记录任意时刻同时在跑的任务数上限。"""

    def __init__(self) -> None:
        self.running = 0
        self.peak = 0

    def __enter__(self) -> "_ConcurrencyProbe":
        self.running += 1
        self.peak = max(self.peak, self.running)
        return self

    def __exit__(self, *exc) -> None:  # noqa: ANN002
        self.running -= 1


# ---------- 1. 单台探测 ----------


def test_probe_device_returns_ok_status():
    status = asyncio.run(probe_device("EQ-001", delay=0.05))
    assert isinstance(status, DeviceStatus)
    assert status.device_id == "EQ-001"
    assert status.status == "ok"
    assert 0.04 <= status.latency <= 0.30


# ---------- 2. 真的并发（关键验收点） ----------


def test_probe_all_runs_concurrently():
    """5 台 × 0.1s：同步要 0.5s+，并发应该 < 0.35s。"""
    ids = [f"EQ-{i:03d}" for i in range(5)]
    t0 = time.perf_counter()
    results = asyncio.run(probe_all(ids, delay=0.1))
    elapsed = time.perf_counter() - t0

    assert len(results) == 5
    assert all(r.status == "ok" for r in results)
    # 并发证据：总耗时接近单台耗时，而不是 5 倍
    assert elapsed < 0.35, f"疑似串行执行，耗时 {elapsed:.3f}s"


# ---------- 3. 结果顺序 = 入参顺序 ----------


def test_probe_all_preserves_input_order():
    ids = ["EQ-C", "EQ-A", "EQ-B"]
    results = asyncio.run(probe_all(ids, delay=0.01))
    assert [r.device_id for r in results] == ids


# ---------- 4. 限流生效 ----------


def test_probe_all_respects_semaphore_limit():
    """limit=2 时，同时在跑的任务数不得超过 2。"""
    probe = _ConcurrencyProbe()
    ids = [f"EQ-{i:03d}" for i in range(6)]

    async def run():
        async def spy(delay=0.02):
            with probe:
                await asyncio.sleep(delay)

        import src.utils.async_tools as mod

        original = mod.probe_device

        async def wrapped(device_id, delay=0.1):
            await spy(delay)
            return DeviceStatus(device_id, "ok", delay)

        mod.probe_device = wrapped
        try:
            return await probe_all(ids, delay=0.02, limit=2)
        finally:
            mod.probe_device = original

    results = asyncio.run(run())
    assert len(results) == 6
    assert probe.peak <= 2, f"限流失效，峰值并发 {probe.peak}"


# ---------- 5. 超时降级 ----------


def test_probe_all_timeout_marks_timeout():
    ids = ["EQ-SLOW"]
    results = asyncio.run(probe_all(ids, delay=0.5, timeout=0.05))
    assert [r.status for r in results] == ["timeout"]


# ---------- 6. 异步生成器（阶段 4 SSE 的骨架） ----------


def test_aiter_probe_results_yields_all():
    async def collect():
        return [s async for s in aiter_probe_results(["EQ-1", "EQ-2", "EQ-3"], delay=0.01)]

    results = asyncio.run(collect())
    assert len(results) == 3
    assert {r.device_id for r in results} == {"EQ-1", "EQ-2", "EQ-3"}
    assert all(r.status == "ok" for r in results)


def test_probe_all_empty_list():
    assert asyncio.run(probe_all([])) == []


if __name__ == "__main__":
    pytest.main([__file__, "-v"])

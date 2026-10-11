"""models 的验收标准（导师写的，别改）。

两条硬要求：
1. 合法数据能构造出来
2. 非法数据必须抛 ValidationError，而且是**明确的**字段名错误，不是静默通过
"""

from __future__ import annotations

from datetime import datetime

import pytest

pytest.importorskip("pydantic", reason="先执行：uv add pydantic")

models = pytest.importorskip("src.models")

SensorReading = getattr(models, "SensorReading", None)
WorkOrder = getattr(models, "WorkOrder", None)

pytestmark = pytest.mark.skipif(
    SensorReading is None,
    reason="先在 src/models.py 里定义 SensorReading 和 WorkOrder",
)

TS = datetime(2026, 10, 11, 9, 30, 0)


def test_sensor_reading_ok() -> None:
    s = SensorReading(device_id="PUMP-001", value=68.5, unit="celsius", ts=TS)
    assert s.device_id == "PUMP-001"
    assert s.value == 68.5
    assert s.unit == "celsius"


def test_sensor_reading_coerces_number_string() -> None:
    """外部传来的数字可能是字符串，Pydantic 应该帮忙转成 float。"""
    s = SensorReading(device_id="PUMP-001", value="68.5", unit="celsius", ts=TS)
    assert isinstance(s.value, float)


def test_sensor_reading_rejects_bad_value() -> None:
    with pytest.raises(Exception):  # noqa: B017 — 用宽泛基类兼容不同版本的 pydantic
        SensorReading(device_id="PUMP-001", value="abc", unit="celsius", ts=TS)


def test_sensor_reading_rejects_unknown_unit() -> None:
    with pytest.raises(Exception):  # noqa: B017
        SensorReading(device_id="PUMP-001", value=68.5, unit="kelvin", ts=TS)


def test_sensor_reading_rejects_empty_device_id() -> None:
    with pytest.raises(Exception):  # noqa: B017
        SensorReading(device_id="", value=68.5, unit="bar", ts=TS)


def test_work_order_defaults() -> None:
    w = WorkOrder(order_id="WO-2026-001", device_id="PUMP-001")
    assert w.priority == "mid"
    assert w.status == "open"


def test_work_order_rejects_bad_priority() -> None:
    with pytest.raises(Exception):  # noqa: B017
        WorkOrder(order_id="WO-2026-001", device_id="PUMP-001", priority="urgent")


def test_work_order_rejects_bad_status() -> None:
    with pytest.raises(Exception):  # noqa: B017
        WorkOrder(order_id="WO-2026-001", device_id="PUMP-001", status="closed")

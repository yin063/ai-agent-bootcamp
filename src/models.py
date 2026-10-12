"""设备与工单的数据模型（Pydantic 版）。

为什么要这一层：Agent 拿到的外部输入（设备上报、工单表单、HTTP 请求）
一律不可信，必须在进业务逻辑之前校验掉格式错误。
"""

from __future__ import annotations

from datetime import datetime
from typing import Literal

from pydantic import BaseModel, Field


class SensorReading(BaseModel):
    """一次传感器读数。外部上报的数据一律不可信，进业务逻辑前先校验。"""

    device_id: str = Field(min_length=1)  # 空字符串直接拒
    value: float  # 传 "68.5" 会被自动转成 68.5
    unit: Literal["celsius", "bar", "rpm"]  # 只认这三种单位
    ts: datetime


class WorkOrder(BaseModel):
    """一张设备巡检工单。"""

    order_id: str
    device_id: str
    priority: Literal["low", "mid", "high"] = "mid"  # 不传默认 mid
    status: Literal["open", "doing", "done"] = "open"

"""设备与工单的数据模型（Pydantic 版）。

为什么要这一层：Agent 拿到的外部输入（设备上报、工单表单、HTTP 请求）
一律不可信，必须在进业务逻辑之前校验掉格式错误。
"""

from __future__ import annotations


# TODO(10-11 ③做)：装依赖
#   uv add pydantic          （本 shell 找不到 uv 就用 ~/.local/bin/uv.exe add pydantic）
#
# 装完把 import 加回来：
#   from datetime import datetime
#   from typing import Literal
#   from pydantic import BaseModel, Field
#
# 然后在这里写两个模型：
#
# class SensorReading(BaseModel):
#     device_id: str                       # 设备编号，不能为空，min_length=1
#     value: float                         # 传感器读数
#     unit: Literal["celsius", "bar", "rpm"]   # 只允许这三种单位
#     ts: datetime                         # 采集时间
#
# class WorkOrder(BaseModel):
#     order_id: str
#     device_id: str
#     priority: Literal["low", "mid", "high"] = "mid"   # 缺省值
#     status: Literal["open", "doing", "done"] = "open"
#
# 看不懂先看：https://www.bilibili.com/video/BV1xUzRYTEBG （30min）
# 再对着文档写：https://docs.pydantic.dev/latest/concepts/models/

"""对话消息层：与具体模型、具体界面都无关。

这一层的意义：把"多轮会话到底怎么组织"从 Streamlit 脚本里剥出来，
使得同一份逻辑将来换 FastAPI / 换云端厂商都不用重写。
"""

from typing import Literal

from pydantic import BaseModel

Role = Literal["system", "user", "assistant"]


class Message(BaseModel):
    """一条对话消息。用 Pydantic 而不是裸 dict，好处是拼错字段名会立刻报错。"""

    role: Role
    content: str

    def to_api(self) -> dict[str, str]:
        """转成各家大模型 API 通用的 dict 格式。"""
        return {"role": self.role, "content": self.content}


def build_messages(
    history: list[Message],
    system: str | None = None,
) -> list[dict[str, str]]:
    """组装要发给模型的 messages 列表。

    规则：system 消息只允许出现一次，且永远排在最前面。
    如果调用方把 system 也塞进了 history，这里要去掉重复的那条，
    否则有些模型会因为"两条 system"而行为异常，还会白白多花 token。
    """
    out: list[dict[str, str]] = []

    if system:
        out.append({"role": "system", "content": system})

    for m in history:
        if system and m.role == "system":
            continue
        out.append(m.to_api())

    return out


def truncate_history(
    history: list[Message],
    max_turns: int = 10,
    keep_system: bool = True,
) -> list[Message]:
    """把对话历史裁剪到最近 max_turns 轮。

    TODO(10-14 ③做)
    要求：
      1. 一轮 = 一条 user + 一条 assistant（按出现的先后顺序成对计算）
      2. 从最新的往回保留，最老的先丢
      3. keep_system 为 True 时，保留结果里第一条 system（如果有），不占用 max_turns 额度
      4. 返回新的列表，不要原地修改入参

    为什么必须做这件事：模型有上下文长度上限，聊到第 50 轮就会报错，
    而每轮都把全部历史发出去还会让 token 费用线性增长。
    """
    raise NotImplementedError("TODO(10-14 ③做)：实现 truncate_history")

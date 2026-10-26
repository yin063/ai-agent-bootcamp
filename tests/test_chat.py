"""chat 模块的验收测试：先把"多轮会话"这件事做对。

设计原则：**测试不联网、不依赖 openai 包**。
所以这里用自己造的假 chunk 对象（鸭子类型）来验证解析逻辑。
"""

from types import SimpleNamespace

import pytest

from src.chat.client import OpenAICompatClient, extract_delta
from src.chat.messages import Message, build_messages, truncate_history


def _history(n_turns: int) -> list[Message]:
    """造 n 轮对话：user / assistant 交替出现。"""
    out: list[Message] = []
    for i in range(1, n_turns + 1):
        out.append(Message(role="user", content=f"问题{i}"))
        out.append(Message(role="assistant", content=f"回答{i}"))
    return out


# ---------------------------------------------------------------- build_messages


def test_build_messages_without_system() -> None:
    msgs = build_messages(_history(2))
    assert [m["role"] for m in msgs] == ["user", "assistant", "user", "assistant"]


def test_build_messages_puts_system_first() -> None:
    msgs = build_messages(_history(1), system="你是一个助手")
    assert msgs[0] == {"role": "system", "content": "你是一个助手"}
    assert len(msgs) == 3


def test_build_messages_dedup_system() -> None:
    """history 里已经混进 system 时，结果里只能有一条 system。"""
    h = [Message(role="system", content="旧的"), *_history(1)]
    msgs = build_messages(h, system="新的")
    systems = [m for m in msgs if m["role"] == "system"]
    assert len(systems) == 1
    assert systems[0]["content"] == "新的"


# -------------------------------------------------------------- truncate_history


def test_truncate_keeps_recent_turns() -> None:
    out = truncate_history(_history(20), max_turns=3)
    assert len(out) == 6
    assert out[0].content == "问题18"
    assert out[-1].content == "回答20"


def test_truncate_keeps_system_and_does_not_mutate() -> None:
    h = [Message(role="system", content="SYS"), *_history(12)]
    out = truncate_history(h, max_turns=2, keep_system=True)
    assert out[0].role == "system"
    assert len(out) == 5  # 1 条 system + 2 轮
    assert len(h) == 25  # 入参没被改动


# ----------------------------------------------------------------- extract_delta


def _chunk(content: str | None) -> SimpleNamespace:
    return SimpleNamespace(choices=[SimpleNamespace(delta=SimpleNamespace(content=content))])


def test_extract_delta_normal() -> None:
    assert extract_delta(_chunk("你好")) == "你好"


def test_extract_delta_none_content() -> None:
    """流式最后一个 chunk 的 content 是 None——这是最常见的线上崩溃点。"""
    assert extract_delta(_chunk(None)) == ""


def test_extract_delta_no_choices() -> None:
    assert extract_delta(SimpleNamespace(choices=[])) == ""


# ------------------------------------------------------------------------- 客户端


def test_default_client_points_to_local_ollama() -> None:
    c = OpenAICompatClient()
    assert c.base_url == "http://localhost:11434/v1"
    assert "qwen" in c.model


def test_stream_chat_is_not_implemented_yet() -> None:
    """占位：实现完成后这条会自然失败，届时直接删掉本用例即可。"""
    with pytest.raises(NotImplementedError):
        list(OpenAICompatClient().stream_chat([{"role": "user", "content": "hi"}]))

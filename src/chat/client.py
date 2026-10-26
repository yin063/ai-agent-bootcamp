"""统一的模型调用客户端。

关键设计：走 **OpenAI 兼容协议**，而不是某个厂商的私有 SDK。

    本地 Ollama  : base_url = "http://localhost:11434/v1"   api_key 填任意字符串
    云端某厂商   : base_url 换成厂商地址                      api_key 换成真 key

好处是"改一行就能换模型"。如果用厂商私有 SDK（比如 ollama 官方包），
将来要把本地模型换成云端服务时，调用代码得整段重写。

注意：openai 包在这里是**懒加载**的（只在真正发请求时才 import），
这样即使环境里没装 openai，也能 import 本模块并跑单元测试。
"""

from collections.abc import Iterator
from typing import Any

DEFAULT_BASE_URL = "http://localhost:11434/v1"
DEFAULT_MODEL = "qwen2.5:7b-instruct-q4_K_M"


def extract_delta(chunk: Any) -> str:
    """从流式响应的一个 chunk 里安全地取出增量文本。

    TODO(10-14 ③做)
    为什么需要一个函数：OpenAI 协议的流式返回里，
    **最后一个 chunk 的 choices[0].delta.content 是 None**，
    直接 `+=` 会抛 TypeError。而且有的 chunk 压根没有 choices（携带用量统计的那种）。

    要求（用 getattr 做防御式取值，不要用 [] 下标，否则缺字段会 KeyError）：
      1. chunk 没有 choices 或 choices 为空 -> 返回 ""
      2. delta 为 None 或 delta.content 为 None -> 返回 ""
      3. 其余情况返回 content 字符串
    """
    raise NotImplementedError("TODO(10-14 ③做)：实现 extract_delta")


class OpenAICompatClient:
    """对所有 OpenAI 兼容服务的统一封装。"""

    def __init__(
        self,
        base_url: str = DEFAULT_BASE_URL,
        api_key: str = "ollama",
        model: str = DEFAULT_MODEL,
        timeout: float = 60.0,
    ) -> None:
        self.base_url = base_url
        self.api_key = api_key
        self.model = model
        self.timeout = timeout
        self._client: Any = None

    def _ensure_client(self) -> Any:
        """创建并缓存底层 SDK 客户端。

        TODO(10-14 ③做)
        要求：
          1. 如果 self._client 已经有值，直接返回（不要每次请求都新建连接）
          2. 否则 `from openai import OpenAI`，构造 OpenAI(base_url=..., api_key=..., timeout=...)
          3. 存进 self._client 再返回
        提示：把 import 写在函数内部，这是"延迟导入"的常用手法。
        """
        raise NotImplementedError("TODO(10-14 ③做)：实现 _ensure_client")

    def stream_chat(self, messages: list[dict[str, str]]) -> Iterator[str]:
        """流式调用，逐个 yield 文本片段。

        TODO(10-14 ③做)
        要求：
          1. client = self._ensure_client()
          2. resp = client.chat.completions.create(
                 model=self.model, messages=messages, stream=True)
          3. for chunk in resp: 用上面写好的 extract_delta(chunk) 取文本，
             取到的**非空**片段才 yield（空串不要往外吐，否则界面会多刷一次）
        """
        raise NotImplementedError("TODO(10-14 ③做)：实现 stream_chat")

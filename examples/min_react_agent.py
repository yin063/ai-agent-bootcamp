"""
最小可用 Agent 完整样例（教学版）
================================

一个 Agent = 三样东西：
    1. 大脑：LLM（本例用本机 Ollama 的 qwen2.5:7b-instruct-q4_K_M）
    2. 手脚：工具（普通 Python 函数，用 @tool 装饰器登记）
    3. 心跳：循环（LLM -> 工具 -> 结果回传 -> 再问 LLM，直到不需要工具）

本文件手搓业界最经典的 ReAct（Reason + Act）循环，约 180 行。
看懂了它，后面所有 Agent 框架（LangChain / LangGraph ...）都只是它的包装。

运行前提：Ollama 已启动，且已拉取模型 qwen2.5:7b-instruct-q4_K_M
运行方法（Git Bash，venv 已激活）：
    uv add requests
    python examples/min_react_agent.py
"""

import json
import sys

import requests

# ============================================================
# 第 1 步：配置
# ============================================================

OLLAMA_URL = "http://localhost:11434/api/chat"  # Ollama 本地对话接口
MODEL = "qwen2.5:7b-instruct-q4_K_M"  # 本机已拉取的 7B 模型
MAX_STEPS = 5  # 最多思考几轮，防止 Agent 停不下来

# ============================================================
# 第 2 步：定义工具（用到了刚学的装饰器）
# ============================================================
# "注册表"模式：@tool 不改变函数行为，只把函数登记进 TOOLS 字典。
# 好处：以后加工具 = 再写一个 @tool 函数，主循环一行都不用改。

TOOLS = {}  # 注册表：工具名 -> 函数


def tool(func):
    """把被装饰的函数登记进 TOOLS，原样返回（不改变它）。"""
    TOOLS[func.__name__] = func
    return func


@tool
def get_weather(city: str) -> str:
    """查询任意城市的实时天气。参数 city：城市名，如 "洛阳"、"北京"。"""
    # 真实工具 = 外部 API + 超时 + 异常兜底。
    # Agent 的能力边界 = 工具的能力边界：模型再聪明，
    # 也回答不了工具给不出的数据（换成写死的假工具，查洛阳只会"查无此地"）。
    try:
        # wttr.in：免费、无需 API key 的天气服务；format=3 拿一行摘要
        response = requests.get(
            f"https://wttr.in/{city}",
            params={"format": "3", "lang": "zh"},
            timeout=15,
        )
        response.raise_for_status()
        return response.text.strip()
    except requests.RequestException as exc:
        # 工具失败也是"观察"：返回人能看懂的原因，
        # 让 LLM 转告用户，而不是让整个程序崩掉
        return f"天气查询失败：{exc}"


@tool
def calc(expression: str) -> str:
    """计算数学表达式。参数 expression：算式，如 "128*46"。（教学代码，真实项目禁用 eval）"""
    try:
        # 空 __builtins__ = 不给它用内置函数，挡住绝大多数注入攻击
        return str(eval(expression, {"__builtins__": {}}, {}))
    except Exception as exc:
        return f"算不出来：{exc}"


# ============================================================
# 第 3 步：把工具清单写进系统提示词（提示词就是接口契约）
# ============================================================


def build_system_prompt() -> str:
    lines = ["你是一个会使用工具的智能体。可用工具："]
    for name, func in TOOLS.items():
        # 直接复用 docstring 当说明书：写一次，两边生效
        lines.append(f"- {name}: {func.__doc__.strip()}")
    lines.append(
        "\n规则：\n"
        "1. 需要工具时，只输出 JSON："
        '{"tool": "工具名", "args": {"参数名": "参数值"}}\n'
        "2. 一个问题需要多个工具时，分多轮调用，每轮只输出一个 JSON。\n"
        "3. 不需要工具时，直接说人话，不要输出 JSON。"
    )
    return "\n".join(lines)


# ============================================================
# 第 4 步：调用 LLM（就是一次 HTTP POST，没有魔法）
# ============================================================


def ask_llm(messages: list[dict]) -> str:
    """把整个消息列表发给 Ollama，拿回这次的回复文本。"""
    payload = {
        "model": MODEL,
        "messages": messages,
        "stream": False,  # 教学版：一次性拿完整回答，不分片
    }
    response = requests.post(OLLAMA_URL, json=payload, timeout=120)
    response.raise_for_status()  # HTTP 出错立刻炸出来，不静默吞错
    return response.json()["message"]["content"]


# ============================================================
# 第 5 步：从回复中解析出"工具调用"（可能没有，也可能有多个）
# ============================================================
# 关键认知：LLM 只会生成文本，不会真的执行任何东西。
# "调用工具"是我们和 LLM 约定的暗号（JSON），解析和执行都由 Python 完成。
#
# 实战教训（本文件因此升级过一次）：
# 7B 小模型不守规矩是常态——可能一次吐出两个 JSON，可能套 ``` 马甲，
# 可能在 JSON 前后夹带人话。所以这里用两层防御：
#   第一层（引导）：系统提示词约定"每轮一个 JSON"——管大多数情况；
#   第二层（兜底）：解析器用 raw_decode 逐个扫描，来几个接几个——管意外情况。
# LLM 输出永远不可全信：先怀疑，再信任。


def parse_tool_calls(text: str) -> list[tuple[str, dict]]:
    """解析出全部工具调用 -> [(工具名, 参数字典), ...]；一个都没有则返回空列表。"""
    calls = []
    decoder = json.JSONDecoder()  # 低级解码器：能从字符串任意位置解析出一个完整 JSON
    idx = 0
    while True:
        # 找下一个 { 作为起点：```json 前缀和人话都会被自动跳过
        start = text.find("{", idx)
        if start == -1:
            break
        try:
            # raw_decode 解析一个 JSON 并返回 (对象, 结束位置)，
            # 所以模型一次吐几个 JSON，这里就能接几个
            data, idx = decoder.raw_decode(text, start)
        except json.JSONDecodeError:
            break  # 从这里往后没有完整 JSON 了
        if isinstance(data, dict) and "tool" in data:
            calls.append((data["tool"], data.get("args", {})))
    return calls


# ============================================================
# 第 6 步：Agent 主循环（全文的心脏，只有 20 行）
# ============================================================


def run_agent(question: str, system_prompt: str | None = None) -> str:
    """跑一个完整 Agent：进去一个问题，出来一个答案。

    system_prompt 可传自定义人设/规则；不传则用本文件默认的通用提示词。
    同一个循环，换一段提示词就换一个 Agent——这叫"依赖注入"。
    """
    # messages 是 Agent 的唯一记忆：每轮全量重发给 LLM（LLM 自己不记对话）
    messages = [
        {"role": "system", "content": system_prompt or build_system_prompt()},
        {"role": "user", "content": question},
    ]

    for step in range(1, MAX_STEPS + 1):
        print(f"\n========== 第 {step} 轮思考 ==========")

        # (1) 思考：基于全部历史，LLM 决定下一步干什么
        reply = ask_llm(messages)
        print(f"[LLM 说] {reply}")

        # (2) 它说过的话也要进记忆，否则下一轮它"失忆"
        messages.append({"role": "assistant", "content": reply})

        # (3) 判断：这轮有没有工具调用？（可能 0 个，也可能一次多个）
        calls = parse_tool_calls(reply)
        if not calls:
            return reply  # 一个暗号都没有 -> 这就是最终答案，结束循环

        # (4) 行动：逐个执行（**args 是字典解包，你学过的那种）
        observations = []
        for tool_name, args in calls:
            print(f"[调用工具] {tool_name}  参数: {args}")
            func = TOOLS.get(tool_name)
            if func is None:
                result = f"错误：工具 {tool_name} 不存在，可用工具: {list(TOOLS)}"
            else:
                try:
                    result = func(**args)
                except TypeError as exc:
                    # LLM 会瞎编参数名，这行就是给它的纠错通道
                    result = f"参数不对：{exc}"
            print(f"[工具结果] {result}")
            observations.append(f"工具 {tool_name} 的结果：{result}")

        # (5) 观察：所有结果一起写回记忆，回到 (1) 让 LLM 接着想
        messages.append({"role": "user", "content": "\n".join(observations)})

    return "（超过最大轮数，Agent 主动放弃）"


if __name__ == "__main__":
    # sys.argv[0] 是脚本名，argv[1] 起才是用户敲的参数——你的第一个命令行程序。
    # 不给参数时用默认问题（同时演示两个工具）；给了就直接问你想问的。
    question = (
        sys.argv[1] if len(sys.argv) > 1 else "北京今天天气如何？再帮我算一下 128*46 等于多少"
    )
    print("[系统提示词]")
    print(build_system_prompt())
    answer = run_agent(question)
    print(f"\n[最终答案] {answer}")

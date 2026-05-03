"""
模型路由层
统一管理所有模型配置，提供 gear-aware 调用
"""

import os
import requests
from typing import Dict, Any

# 模型注册表
MODEL_REGISTRY = {
    "deepseek": {
        "name": "DeepSeek Chat",
        "url": "https://api.deepseek.com/v1/chat/completions",
        "model": "deepseek-chat",
        "key_env": "DEEPSEEK_API_KEY",
    },
    "qwen": {
        "name": "百炼 Qwen-Turbo",
        "url": "https://dashscope.aliyuncs.com/compatible-mode/v1/chat/completions",
        "model": "qwen-turbo",
        "key_env": "BAILIAN_API_KEY",
    },
    "kimi": {
        "name": "Kimi",
        "url": "https://api.moonshot.cn/v1/chat/completions",
        "model": "moonshot-v1-8k",
        "key_env": "KIMI_API_KEY",
    },
    "local": {
        "name": "Local Ollama",
        "url": "http://localhost:11434/v1/chat/completions",
        "model": "qwen2.5:7b",
        "key_env": None,
    },
}

GEAR_PROMPTS = {
    1: "你处于完全约束模式（EMBRACE）。只回答用户直接提问的问题，用最简洁的方式回复，不做任何额外建议。回复不超过 50 字。",
    2: "你处于有限建议模式（EXPLORE）。可以提出选项和建议，但每项执行需要用户确认。保持回复在 200 字以内。",
    3: "你处于自主调整模式（ADAPT）。可以在预设边界内自主回答，但需记录决策理由。回复可以详细。",
    4: "你处于全自主模式（LET_GO）。可以自由回答和执行，仅在异常情况下暂停等待用户介入。",
}

GEAR_MAP = {
    1: {"name": "EMBRACE", "desc": "完全约束态"},
    2: {"name": "EXPLORE", "desc": "有限建议态"},
    3: {"name": "ADAPT", "desc": "自主调整须报告"},
    4: {"name": "LET_GO", "desc": "全自主异常介入"},
}


def gear_aware_call(model_id: str, message: str, gear: int = 2) -> Dict[str, Any]:
    """
    通用档位感知模型调用函数。
    
    Args:
        model_id: 模型 ID (deepseek/qwen/kimi/local)
        message: 用户消息
        gear: 档位 1-4
    
    Returns:
        {"success": bool, "reply": str, "model": str, "gear": int, "gear_name": str}
    """
    if model_id not in MODEL_REGISTRY:
        return {"success": False, "error": f"不支持的模型：{model_id}"}
    
    model_info = MODEL_REGISTRY[model_id]
    api_key = os.environ.get(model_info["key_env"], "") if model_info["key_env"] else ""
    
    # 检查 API Key（本地模型不需要）
    if model_info["key_env"] and not api_key:
        return {"success": False, "error": f"{model_info['name']} API Key 未配置（环境变量：{model_info['key_env']}）"}
    
    gear_name = GEAR_MAP.get(gear, {}).get("name", "UNKNOWN")
    system_prompt = GEAR_PROMPTS.get(gear, GEAR_PROMPTS[1])
    system_prompt += f"\n\n当前系统状态：档位 {gear} ({gear_name})。"
    
    # 构建请求头（本地模型不需要 Authorization）
    headers = {"Content-Type": "application/json"}
    if api_key:
        headers["Authorization"] = f"Bearer {api_key}"
    
    try:
        resp = requests.post(
            model_info["url"],
            headers=headers,
            json={
                "model": model_info["model"],
                "messages": [
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": message}
                ],
                "temperature": 0.7,
                "max_tokens": 1024,
            },
            timeout=30
        )
        result = resp.json()
        reply = result["choices"][0]["message"]["content"]
        return {
            "success": True,
            "reply": reply,
            "model": model_info["name"],
            "gear": gear,
            "gear_name": gear_name,
        }
    except Exception as e:
        return {"success": False, "error": str(e)}

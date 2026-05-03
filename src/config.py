"""
配置管理
"""

import os
from typing import Dict, Optional

DEFAULT_CONFIG = {
    "log_file": "cost_log.jsonl",
    "department": "default",
    "api_keys": {},
}


def load_config(config_file: Optional[str] = None) -> Dict:
    """
    加载配置
    
    优先级：
    1. 配置文件（如果提供）
    2. 环境变量
    3. 默认值
    """
    config = DEFAULT_CONFIG.copy()
    
    # 从环境变量加载 API Keys
    for key in ["DEEPSEEK_API_KEY", "BAILIAN_API_KEY", "KIMI_API_KEY"]:
        value = os.environ.get(key, "")
        if value:
            model_key = key.replace("_API_KEY", "").lower()
            if model_key == "bailian":
                model_key = "qwen"
            config["api_keys"][model_key] = value
    
    return config

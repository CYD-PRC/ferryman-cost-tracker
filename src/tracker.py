"""
成本追踪核心模块
记录每次调用的熵值、token、成本
"""

import json
import os
import time
from datetime import datetime
from typing import Optional, Dict, Any, List

try:
    from .router import gear_aware_call, MODEL_REGISTRY
except ImportError:
    from router import gear_aware_call, MODEL_REGISTRY

# 各模型价格（每 1K tokens，美元）
PRICING = {
    "deepseek": {"input": 0.00027, "output": 0.0011},
    "qwen": {"input": 0.00057, "output": 0.0017},
    "kimi": {"input": 0.002, "output": 0.002},
    "local": {"input": 0, "output": 0},
}

GEAR_ENTROPY_MAP = {
    1: 0.0,    # EMBRACE
    2: 0.25,   # EXPLORE
    3: 0.75,   # ADAPT
    4: 1.5,    # LET_GO
}


class FerrymanTracker:
    """
    成本追踪器
    
    用法:
        tracker = FerrymanTracker(api_keys={"deepseek": "xxx", "qwen": "xxx"})
        response = tracker.chat("你好", model_id="deepseek", gear=2)
        report = tracker.get_report()
    """
    
    def __init__(
        self,
        api_keys: Optional[Dict[str, str]] = None,
        log_file: str = "cost_log.jsonl",
        department: str = "default"
    ):
        self.api_keys = api_keys or {}
        self.log_file = log_file
        self.department = department
        self._event_log = []
    
    def _calculate_cost(self, model_id: str, input_tokens: int, output_tokens: int) -> float:
        """计算单次调用成本"""
        pricing = PRICING.get(model_id, {"input": 0, "output": 0})
        return (input_tokens * pricing["input"] + output_tokens * pricing["output"]) / 1000
    
    def _estimate_tokens(self, text: str) -> int:
        """粗略估算 token 数（中文约 1.5 字/token）"""
        return max(1, int(len(text) / 1.5))
    
    def chat(
        self,
        message: str,
        model_id: str = "deepseek",
        gear: int = 2,
        user_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        调用模型并追踪成本
        
        Args:
            message: 用户输入
            model_id: 模型 ID (deepseek/qwen/kimi/local)
            gear: 档位 1-4
            user_id: 可选的用户 ID
        
        Returns:
            {"success": bool, "reply": str, "cost": float, "tokens": {...}}
        """
        start_time = time.time()
        
        # 调用模型
        result = gear_aware_call(model_id, message, gear)
        
        # 估算 token（实际应该从 API 响应中获取，这里简化处理）
        input_tokens = self._estimate_tokens(message)
        output_tokens = self._estimate_tokens(result.get("reply", "")) if result.get("success") else 0
        
        # 计算成本
        cost = self._calculate_cost(model_id, input_tokens, output_tokens)
        
        # 记录日志
        log_entry = {
            "timestamp": datetime.utcnow().isoformat() + "Z",
            "model": model_id,
            "gear": gear,
            "gear_name": result.get("gear_name", "UNKNOWN"),
            "entropy": GEAR_ENTROPY_MAP.get(gear, 0),
            "input_tokens": input_tokens,
            "output_tokens": output_tokens,
            "cost_usd": round(cost, 6),
            "department": self.department,
            "user_id": user_id or "anonymous",
            "latency_ms": round((time.time() - start_time) * 1000, 0),
            "success": result.get("success", False),
        }
        
        self._event_log.append(log_entry)
        self._append_to_file(log_entry)
        
        # 返回结果（附加成本信息）
        result["cost_usd"] = round(cost, 6)
        result["tokens"] = {"input": input_tokens, "output": output_tokens}
        result["latency_ms"] = log_entry["latency_ms"]
        
        return result
    
    def _append_to_file(self, entry: Dict[str, Any]):
        """追加日志到文件"""
        try:
            with open(self.log_file, "a", encoding="utf-8") as f:
                f.write(json.dumps(entry, ensure_ascii=False) + "\n")
        except Exception as e:
            print(f"日志写入失败：{e}")
    
    def get_report(
        self,
        department: Optional[str] = None,
        period: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        获取成本报告
        
        Args:
            department: 部门过滤
            period: 月份过滤 (格式：2026-05)
        
        Returns:
            成本统计报告
        """
        logs = self._load_logs()
        
        # 过滤
        if department:
            logs = [l for l in logs if l.get("department") == department]
        if period:
            logs = [l for l in logs if l.get("timestamp", "").startswith(period)]
        
        # 统计
        total_cost = sum(l.get("cost_usd", 0) for l in logs)
        total_input = sum(l.get("input_tokens", 0) for l in logs)
        total_output = sum(l.get("output_tokens", 0) for l in logs)
        
        # 按档位统计
        by_gear = {}
        for l in logs:
            gear = l.get("gear", 0)
            if gear not in by_gear:
                by_gear[gear] = {"count": 0, "cost": 0, "entropy": l.get("entropy", 0)}
            by_gear[gear]["count"] += 1
            by_gear[gear]["cost"] += l.get("cost_usd", 0)
        
        # 按模型统计
        by_model = {}
        for l in logs:
            model = l.get("model", "unknown")
            if model not in by_model:
                by_model[model] = {"count": 0, "cost": 0}
            by_model[model]["count"] += 1
            by_model[model]["cost"] += l.get("cost_usd", 0)
        
        return {
            "total_calls": len(logs),
            "total_cost_usd": round(total_cost, 4),
            "total_input_tokens": total_input,
            "total_output_tokens": total_output,
            "avg_entropy": sum(l.get("entropy", 0) for l in logs) / max(1, len(logs)),
            "by_gear": {k: {"count": v["count"], "cost_usd": round(v["cost"], 4)} for k, v in by_gear.items()},
            "by_model": {k: {"count": v["count"], "cost_usd": round(v["cost"], 4)} for k, v in by_model.items()},
            "period": period or "all",
            "department": department or "all",
        }
    
    def _load_logs(self) -> List[Dict[str, Any]]:
        """从文件加载日志"""
        logs = []
        if os.path.exists(self.log_file):
            try:
                with open(self.log_file, "r", encoding="utf-8") as f:
                    for line in f:
                        if line.strip():
                            logs.append(json.loads(line))
            except Exception as e:
                print(f"日志读取失败：{e}")
        return logs
    
    def get_recent_logs(self, limit: int = 10) -> List[Dict[str, Any]]:
        """获取最近的日志"""
        logs = self._load_logs()
        return logs[-limit:]

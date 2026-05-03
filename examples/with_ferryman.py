#!/usr/bin/env python3
"""
与 Ferryman 数字孪生集成示例

展示如何将成本追踪集成到现有的 Ferryman 系统中
"""

import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

from tracker import FerrymanTracker, GEAR_ENTROPY_MAP


def main():
    print("=" * 50)
    print("Ferryman + Cost Tracker 集成演示")
    print("=" * 50)
    
    # 初始化追踪器
    tracker = FerrymanTracker(
        department="digital_twin",
        log_file="ferryman_cost_log.jsonl"
    )
    
    # 模拟 Ferryman 的档位切换场景
    print("\n场景：用户在数字孪生界面切换档位，每次切换后与 AI 交互")
    print("-" * 50)
    
    scenarios = [
        {"gear": 1, "message": "当前系统状态如何？"},
        {"gear": 2, "message": "有什么优化建议？"},
        {"gear": 3, "message": "详细分析一下潜在风险"},
        {"gear": 4, "message": "自主决策，我信任你"},
    ]
    
    total_cost = 0
    total_entropy = 0
    
    for scenario in scenarios:
        gear = scenario["gear"]
        message = scenario["message"]
        entropy = GEAR_ENTROPY_MAP.get(gear, 0)
        
        print(f"\n[档位 {gear} · 熵={entropy}] {message}")
        
        result = tracker.chat(
            message=message,
            model_id="deepseek",
            gear=gear,
            user_id="user_demo"
        )
        
        if result.get("success"):
            cost = result.get("cost_usd", 0)
            total_cost += cost
            total_entropy += entropy
            print(f"  → 成本：${cost:.6f} | 累计：${total_cost:.6f}")
        else:
            print(f"  → 错误：{result.get('error')}")
    
    # 输出总结
    print("\n" + "=" * 50)
    print("会话总结")
    print("=" * 50)
    print(f"总成本：${total_cost:.6f}")
    print(f"平均熵值：{total_entropy / len(scenarios):.3f}")
    print(f"\n日志已保存到：ferryman_cost_log.jsonl")
    
    # 生成报告
    report = tracker.get_report(department="digital_twin")
    print(f"\n详细报告：{report}")


if __name__ == "__main__":
    main()

# Ferryman Cost Tracker

AI 权限控制的成本追踪中间层，PRE-GHR 框架的工程参考实现。

## 核心功能

- **四档位熵感知路由**（EMBRACE/EXPLORE/ADAPT/LET_GO）
- **Token 成本追踪与审计日志**
- **支持 DeepSeek / Qwen / Kimi 模型**

## 快速开始

```bash
# 安装依赖
pip install -r requirements.txt

# 设置 API Key
export DEEPSEEK_API_KEY=your_key_here
export BAILIAN_API_KEY=your_key_here
export KIMI_API_KEY=your_key_here

# 运行示例
python examples/basic_usage.py
```

## 用法

```python
from src.tracker import FerrymanTracker

tracker = FerrymanTracker(department="engineering")

# 调用并自动追踪成本
result = tracker.chat(
    message="你好",
    model_id="deepseek",
    gear=2  # EXPLORE 档
)

print(f"回复：{result['reply']}")
print(f"成本：${result['cost_usd']:.6f}")

# 获取成本报告
report = tracker.get_report(period="2026-05")
print(f"本月花费：${report['total_cost_usd']:.4f}")
```

## 档位说明

| 档位 | 名称 | 熵值 | 适用场景 |
|------|------|------|----------|
| 1 | EMBRACE | 0.0 | 完全约束，只回答直接问题 |
| 2 | EXPLORE | 0.25 | 有限建议，需用户确认 |
| 3 | ADAPT | 0.75 | 自主调整，可详细回答 |
| 4 | LET_GO | 1.5 | 全自主，自由发挥 |

## 日志格式

每条调用记录保存为 JSONL 格式：

```json
{
  "timestamp": "2026-05-03T19:00:00Z",
  "model": "deepseek",
  "gear": 2,
  "gear_name": "EXPLORE",
  "entropy": 0.25,
  "input_tokens": 50,
  "output_tokens": 120,
  "cost_usd": 0.00034,
  "department": "engineering",
  "user_id": "user_123",
  "latency_ms": 850
}
```

## 项目结构

```
ferryman-cost-tracker/
├── src/
│   ├── tracker.py      # 成本追踪核心
│   ├── router.py       # 模型路由
│   └── config.py       # 配置管理
├── examples/           # 使用示例
├── tests/              # 测试
├── requirements.txt
├── LICENSE
└── README.md
```

---

想跑就跑，想改就改，想问就问。

**License:** MIT

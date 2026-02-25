# 保险智能体评测系统 - 后端

基于 LiveBench 模式的保险大模型智能体评估系统后端。

## 核心功能

### 1. Agent 适配层 (sandbox/)
- **统一接口**: 支持 OpenAI API、Azure OpenAI、vLLM、本地模型
- **自动适配**: 通过配置即可接入任意大模型
- **健康检查**: 支持连接测试和性能监控

### 2. 评分引擎 (evaluators/)
- **关键词检查**: 验证必须包含/禁止出现的关键词
- **数值比对**: 计算题精确验证，支持容忍区间
- **Schema验证**: JSON格式和字段类型检查
- **结论验证**: 案例分析的正确结论判断
- **合规检查**: 保险销售禁用词检测
- **工具调用验证**: API调用序列和参数检查

### 3. 题库系统
**五大维度，共50道题:**
- **保险业务知识** (10题): 条款解析、免责判定、权益说明
- **客户需求理解** (10题): 意图识别、情感分析、需求挖掘
- **专业推理能力** (10题): 理赔判断、核保评估、精算计算
- **合规安全** (10题): 销售合规、隐私保护、风险控制
- **工具调用** (10题): API调用、数据查询、流程处理

### 4. 评测流水线
- 并发执行评测
- 超时控制和重试机制
- 结构化输出解析
- 详细的评分报告

## 快速开始

### 1. 安装依赖

```bash
cd backend
pip install -r requirements.txt
```

### 2. 运行测试

```bash
# 测试题库和评分引擎
python test_system.py

# 测试完整评测（需要设置API Key）
export OPENAI_API_KEY=your_key
python test_system.py
```

### 3. 启动API服务

```bash
python run.py
```

服务启动后访问:
- API文档: http://localhost:8000/docs
- 健康检查: http://localhost:8000/health

## API 接口

### Agent 管理

```bash
# 注册Agent
curl -X POST http://localhost:8000/api/v1/agents/ \
  -H "Content-Type: application/json" \
  -d '{
    "id": "my-agent",
    "name": "My Insurance Agent",
    "vendor": "My Company",
    "agent_type": "openai_api",
    "base_url": "https://api.openai.com/v1",
    "api_key": "sk-...",
    "model": "gpt-4"
  }'

# 测试Agent连接
curl http://localhost:8000/api/v1/agents/my-agent/test
```

### 题库查询

```bash
# 获取题库统计
curl http://localhost:8000/api/v1/questions/stats

# 获取题目列表
curl http://localhost:8000/api/v1/questions/

# 按维度获取题目
curl http://localhost:8000/api/v1/questions/?dimension=knowledge

# 获取题目详情
curl http://localhost:8000/api/v1/questions/INS-KNOW-001
```

### 执行评测

```bash
# 执行完整评测
curl -X POST http://localhost:8000/api/v1/evaluation/run \
  -H "Content-Type: application/json" \
  -d '{
    "agent_config": {
      "id": "test-agent",
      "name": "Test Agent",
      "vendor": "Test",
      "agent_type": "openai_api",
      "base_url": "https://api.openai.com/v1",
      "api_key": "sk-...",
      "model": "gpt-4"
    },
    "question_set_id": "benchmark_v1",
    "concurrency": 3
  }'
```

## 项目结构

```
backend/
├── src/
│   ├── models/           # Pydantic数据模型
│   │   ├── agent.py     # Agent配置和响应
│   │   ├── question.py  # 题目模型
│   │   └── evaluation.py # 评测结果
│   ├── sandbox/         # Agent适配层
│   │   ├── adapter.py   # 基类
│   │   ├── openai_adapter.py
│   │   ├── local_adapter.py
│   │   └── factory.py   # 工厂
│   ├── evaluators/      # 评分引擎
│   │   ├── base.py
│   │   ├── keyword_checker.py
│   │   ├── numeric_checker.py
│   │   ├── schema_validator.py
│   │   ├── logic_engine.py
│   │   ├── compliance_checker.py
│   │   ├── tool_call_checker.py
│   │   └── factory.py
│   ├── db/             # 数据层
│   │   └── question_repo.py
│   ├── pipeline/       # 评测流水线
│   │   └── evaluator.py
│   └── api/            # FastAPI服务
│       ├── main.py
│       └── routes/
│           ├── leaderboard.py
│           ├── agent.py
│           ├── evaluation.py
│           └── questions.py
├── data/
│   └── questions/      # 题库文件
│       ├── benchmark_knowledge_10.json
│       ├── benchmark_understanding_10.json
│       ├── benchmark_reasoning_10.json
│       ├── benchmark_compliance_10.json
│       └── benchmark_tools_10.json
├── tests/              # 测试文件
├── requirements.txt
├── run.py             # 启动脚本
└── test_system.py     # 测试脚本
```

## 自定义Agent配置

```python
from src.models.agent import AgentConfig, AgentType

config = AgentConfig(
    id="my-agent",
    name="My Insurance Agent",
    vendor="My Company",
    agent_type=AgentType.OPENAI_API,
    base_url="https://api.openai.com/v1",
    api_key="sk-...",
    model="gpt-4",
    temperature=0.3,
    system_prompt="你是一位专业的保险顾问..."
)
```

## 添加新题目

```python
from src.models.question import Question, ValidationRule
from src.db.question_repo import get_repository

question = Question(
    question_id="INS-CUSTOM-001",
    dimension="knowledge",
    question_type="case_analysis",
    title="自定义题目",
    content="题目内容...",
    validation_rules=ValidationRule(
        must_contain_keywords=["关键词1", "关键词2"],
        prohibited_keywords=["禁用词"]
    ),
    score=100
)

repo = get_repository()
repo.save_question(question, "custom_questions.json")
```

## 评分规则说明

| 评分器 | 用途 | 配置方式 |
|--------|------|----------|
| KeywordChecker | 关键词验证 | must_contain_keywords, prohibited_keywords |
| NumericChecker | 数值计算验证 | numeric_path, numeric_tolerance |
| SchemaValidator | JSON格式验证 | expected_schema |
| ConclusionChecker | 结论判断 | conclusion_must_be_one_of |
| ComplianceChecker | 合规检查 | 内置禁用词库 |
| ToolCallChecker | 工具调用验证 | required_tools |

## 后续开发计划

1. **数据爬虫**: 自动抓取最新保险条款和案例
2. **题目变异引擎**: 自动生成题目变体防污染
3. **竞技场引擎**: 虚拟客户实时对战系统
4. **排行榜服务**: 完整的排名和历史追踪
5. **前端对接**: WebSocket实时数据推送

## License

MIT

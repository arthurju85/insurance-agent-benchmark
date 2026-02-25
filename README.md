# 保险智能体评测系统

一个专业的保险Agent评测平台，支持多维度能力测试、排行榜管理和数据持久化。

## 系统架构

```
┌─────────────────────────────────────────────────────────────────┐
│                        前端界面 (Web)                             │
├─────────────────────────────────────────────────────────────────┤
│                     FastAPI 后端服务                              │
│  ┌─────────────┐ ┌─────────────┐ ┌─────────────┐ ┌────────────┐ │
│  │ 排行榜API   │ │ Agent管理   │ │ 评测API     │ │ 题库API    │ │
│  └─────────────┘ └─────────────┘ └─────────────┘ └────────────┘ │
│  ┌─────────────┐ ┌─────────────┐ ┌─────────────────────────────┐│
│  │ 题目变异    │ │ 竞技场API   │ │ 数据持久化(SQLite)          ││
│  └─────────────┘ └─────────────┘ └─────────────────────────────┘│
├─────────────────────────────────────────────────────────────────┤
│                      核心评测引擎                                 │
│  ┌─────────────┐ ┌─────────────┐ ┌─────────────┐ ┌────────────┐ │
│  │ 知识评测    │ │ 理解评测    │ │ 推理评测    │ │ 合规评测   │ │
│  └─────────────┘ └─────────────┘ └─────────────┘ └────────────┘ │
│  ┌─────────────┐ ┌─────────────┐ ┌─────────────────────────────┐│
│  │ 工具评测    │ │ 沙箱执行    │ │ 题目变异引擎                ││
│  └─────────────┘ └─────────────┘ └─────────────────────────────┘│
└─────────────────────────────────────────────────────────────────┘
```

## 功能模块

### P1 优先级（已完成）

#### 1. 核心评测流水线 ✅
- 五维度评测（知识/理解/推理/合规/工具）
- 多线程并行执行
- 自动评分和报告生成

**文件位置：**
- `backend/src/pipeline/evaluator.py` - 评测器核心
- `backend/src/pipeline/runner.py` - 流水线运行器

#### 2. 沙箱系统 ✅
- 隔离执行环境
- OpenAI API 适配器
- 工具调用支持

**文件位置：**
- `backend/src/sandbox/` - 沙箱模块

#### 3. 数据持久化 ✅
- SQLite 数据库存储
- 评测结果自动保存
- 历史趋势分析

**文件位置：**
- `backend/src/db/database.py` - 数据库管理
- `backend/data/insurance_benchmark.db` - 数据库文件

**数据库表结构：**
| 表名 | 用途 |
|------|------|
| `evaluations` | 评测结果主表 |
| `evaluation_details` | 每道题的详细评分 |
| `leaderboard_history` | 排行榜历史记录 |
| `arena_sessions` | 竞技场会话 |
| `arena_events` | 竞技场事件日志 |
| `registered_agents` | 注册的Agent |

#### 4. 题目变异引擎 ✅
自动生成题目变体，防止数据污染和过拟合。

**支持的变异类型：**
- **数值变异**：日期、金额、年龄等参数调整
- **实体替换**：人名、公司名、地名的同义词替换
- **句式重组**：保持语义不变的前提下调整表达方式
- **选项重排**：选择题选项顺序调整

**文件位置：**
- `backend/src/db/variation_engine.py` - 变异引擎核心

**使用示例：**
```python
from backend.src.db.variation_engine import VariationEngine

# 创建变异引擎
engine = VariationEngine(seed=42)

# 为单道题生成3个变体
variations = engine.generate_variations(question, count=3)

# 批量生成题集变体
all_questions = engine.generate_question_set_variations(
    questions,
    variations_per_question=3
)
```

**API接口：**
- `POST /api/v1/variations/generate` - 为指定题目生成变体
- `POST /api/v1/variations/generate-set` - 批量生成题集变体
- `GET /api/v1/variations/{question_id}/variants` - 列出变体
- `POST /api/v1/variations/preview` - 预览变体效果

### P2 优先级（已完成）

#### 5. 数据爬虫系统 ✅
自动抓取保险条款、监管政策、法律案例，并解析为结构化数据。

**支持的爬虫：**
- 银保监会（国家金融监督管理总局）政策
- 保险公司官网产品条款
- 裁判文书网保险案例

**文件位置：**
- `backend/src/crawler/crawler.py` - 爬虫核心
- `backend/src/crawler/parser.py` - 条款解析器

**API接口：**
- `POST /api/v1/crawler/run` - 执行数据爬取
- `GET /api/v1/crawler/data` - 查询已爬取数据
- `POST /api/v1/crawler/parse` - 解析条款文本

**条款解析功能：**
- 自动识别条款类型（重疾险/医疗险/意外险等）
- 提取关键日期（等待期、犹豫期、宽限期）
- 提取保额信息
- 识别责任免除条款
- 生成评测题目建议

#### 6. 管理员后台 ✅
提供题库管理、评测监控、系统配置等管理功能。

**文件位置：**
- `backend/src/api/admin.py` - 管理模块
- `backend/src/api/routes/admin.py` - 管理API路由

**功能模块：**

| 模块 | 功能 |
|------|------|
| 仪表盘 | 数据统计、趋势分析 |
| 题目管理 | CRUD、变体生成、批量导入 |
| 评测监控 | 实时监控、历史查询、性能分析 |
| 系统管理 | 配置管理、数据备份 |

**API接口：**
- `GET /api/v1/admin/dashboard` - 仪表盘数据
- `GET/PUT/DELETE /api/v1/admin/questions/{id}` - 题目管理
- `GET /api/v1/admin/evaluations/*` - 评测监控
- `GET/POST /api/v1/admin/system/*` - 系统管理

## 快速开始

### 安装依赖

```bash
# 创建虚拟环境
python3 -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# 安装依赖
pip install -r requirements.txt
```

### 运行测试

```bash
# 测试数据库模块
python test_database.py

# 测试题目变异引擎
python test_variation_engine.py

# 测试数据爬虫系统
python test_crawler.py

# 测试管理员后台
python test_admin.py

# 运行完整评测
python run_benchmark.py --agent-id test-agent-1 --question-set benchmark_v1
```

### 启动API服务

```bash
cd backend/src
uvicorn api.main:app --reload --host 0.0.0.0 --port 8000
```

### API文档

启动服务后访问：http://localhost:8000/docs

## 项目结构

```
insurance-agent-benchmark/
├── backend/
│   ├── src/
│   │   ├── api/              # FastAPI 接口
│   │   │   ├── main.py       # 应用入口
│   │   │   ├── admin.py      # 管理员模块
│   │   │   └── routes/       # 路由模块
│   │   ├── crawler/          # 数据爬虫
│   │   │   ├── crawler.py    # 爬虫核心
│   │   │   └── parser.py     # 条款解析器
│   │   ├── db/               # 数据层
│   │   │   ├── database.py   # 数据库管理
│   │   │   ├── question_repo.py  # 题库管理
│   │   │   └── variation_engine.py  # 题目变异引擎
│   │   ├── models/           # 数据模型
│   │   ├── pipeline/         # 评测流水线
│   │   └── sandbox/          # 沙箱执行环境
│   └── data/                 # 数据文件
│       ├── questions/        # 题库文件
│       └── insurance_benchmark.db  # SQLite数据库
├── frontend/                 # 前端界面
├── test_database.py          # 数据库测试
├── test_variation_engine.py  # 变异引擎测试
├── test_crawler.py           # 爬虫系统测试
├── test_admin.py             # 管理员后台测试
└── run_benchmark.py          # 评测运行脚本
```

## 评测维度

| 维度 | 说明 | 示例题目 |
|------|------|----------|
| 知识 | 保险业务知识掌握 | 等待期条款解析 |
| 理解 | 客户需求理解能力 | 从对话中提取关键信息 |
| 推理 | 专业推理能力 | 理赔案例计算分析 |
| 合规 | 合规安全 | 识别不当销售话术 |
| 工具 | 工具调用能力 | 调用计算器进行保费计算 |

## 贡献指南

1. Fork 本项目
2. 创建特性分支：`git checkout -b feature/xxx`
3. 提交更改：`git commit -am 'Add some feature'`
4. 推送分支：`git push origin feature/xxx`
5. 创建 Pull Request

## 许可证

MIT License

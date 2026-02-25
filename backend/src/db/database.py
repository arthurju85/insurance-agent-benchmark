"""
数据库管理模块
使用SQLite进行数据持久化
"""

import sqlite3
import json
from pathlib import Path
from typing import Optional, List, Dict, Any
from datetime import datetime
from contextlib import contextmanager


class Database:
    """
    SQLite数据库管理类
    """

    def __init__(self, db_path: str = None):
        if db_path is None:
            # 默认存储在项目data目录
            current_file = Path(__file__).resolve()
            data_dir = current_file.parent.parent.parent / "data"
            data_dir.mkdir(exist_ok=True)
            db_path = data_dir / "insurance_benchmark.db"

        self.db_path = str(db_path)
        self._init_database()

    @contextmanager
    def get_connection(self):
        """获取数据库连接上下文管理器"""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        try:
            yield conn
            conn.commit()
        except Exception as e:
            conn.rollback()
            raise e
        finally:
            conn.close()

    def _init_database(self):
        """初始化数据库表结构"""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()

        try:
            # 评测结果表
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS evaluations (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    evaluation_id TEXT UNIQUE NOT NULL,
                    agent_id TEXT NOT NULL,
                    agent_name TEXT NOT NULL,
                    agent_vendor TEXT,
                    agent_version TEXT,
                    question_set_id TEXT NOT NULL,
                    status TEXT NOT NULL,
                    total_score REAL DEFAULT 0,
                    max_total_score REAL DEFAULT 0,
                    overall_percentage REAL DEFAULT 0,
                    total_questions INTEGER DEFAULT 0,
                    completed_questions INTEGER DEFAULT 0,
                    failed_questions INTEGER DEFAULT 0,
                    timeout_questions INTEGER DEFAULT 0,
                    total_latency_ms REAL DEFAULT 0,
                    avg_latency_ms REAL DEFAULT 0,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    started_at TIMESTAMP,
                    completed_at TIMESTAMP,
                    tags TEXT,
                    notes TEXT,
                    raw_result TEXT
                )
            """)

            # 评测详情表
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS evaluation_details (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    evaluation_id TEXT NOT NULL,
                    question_id TEXT NOT NULL,
                    dimension TEXT NOT NULL,
                    agent_output TEXT,
                    parsed_output TEXT,
                    latency_ms REAL,
                    score REAL DEFAULT 0,
                    max_score REAL DEFAULT 0,
                    status TEXT NOT NULL,
                    error_message TEXT,
                    validation_results TEXT,
                    tool_calls TEXT,
                    executed_at TIMESTAMP,
                    FOREIGN KEY (evaluation_id) REFERENCES evaluations(evaluation_id)
                )
            """)

            # 排行榜历史表
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS leaderboard_history (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    leaderboard_id TEXT NOT NULL,
                    name TEXT NOT NULL,
                    evaluation_date TEXT NOT NULL,
                    question_set_id TEXT NOT NULL,
                    agent_id TEXT NOT NULL,
                    agent_name TEXT NOT NULL,
                    vendor TEXT,
                    version TEXT,
                    agent_type TEXT,
                    rank INTEGER NOT NULL,
                    overall_score REAL NOT NULL,
                    overall_percentage REAL NOT NULL,
                    knowledge_score REAL DEFAULT 0,
                    understanding_score REAL DEFAULT 0,
                    reasoning_score REAL DEFAULT 0,
                    compliance_score REAL DEFAULT 0,
                    tools_score REAL DEFAULT 0,
                    change_from_last REAL DEFAULT 0,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)

            # 竞技场会话表
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS arena_sessions (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    session_id TEXT UNIQUE NOT NULL,
                    name TEXT,
                    status TEXT NOT NULL,
                    started_at TIMESTAMP,
                    ended_at TIMESTAMP,
                    duration_minutes INTEGER,
                    config TEXT,
                    final_leaderboard TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)

            # 竞技场事件表
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS arena_events (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    session_id TEXT NOT NULL,
                    event_type TEXT NOT NULL,
                    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    data TEXT,
                    FOREIGN KEY (session_id) REFERENCES arena_sessions(session_id)
                )
            """)

            # Agent注册表
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS registered_agents (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    agent_id TEXT UNIQUE NOT NULL,
                    name TEXT NOT NULL,
                    vendor TEXT NOT NULL,
                    version TEXT DEFAULT '1.0',
                    agent_type TEXT NOT NULL,
                    base_url TEXT,
                    model TEXT NOT NULL,
                    system_prompt TEXT,
                    config TEXT,
                    is_active BOOLEAN DEFAULT 1,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    last_tested_at TIMESTAMP,
                    test_result TEXT
                )
            """)

            # 创建索引
            cursor.execute("""
                CREATE INDEX IF NOT EXISTS idx_evaluations_agent
                ON evaluations(agent_id)
            """)
            cursor.execute("""
                CREATE INDEX IF NOT EXISTS idx_evaluations_date
                ON evaluations(created_at)
            """)
            cursor.execute("""
                CREATE INDEX IF NOT EXISTS idx_leaderboard_date
                ON leaderboard_history(evaluation_date)
            """)
            cursor.execute("""
                CREATE INDEX IF NOT EXISTS idx_arena_events_session
                ON arena_events(session_id)
            """)

            conn.commit()
        except Exception as e:
            conn.rollback()
            raise e
        finally:
            conn.close()

    # ========== 评测结果操作 ==========

    def save_evaluation(self, evaluation: Dict[str, Any]) -> str:
        """保存评测结果"""
        with self.get_connection() as conn:
            cursor = conn.cursor()

            cursor.execute("""
                INSERT OR REPLACE INTO evaluations (
                    evaluation_id, agent_id, agent_name, agent_vendor, agent_version,
                    question_set_id, status, total_score, max_total_score, overall_percentage,
                    total_questions, completed_questions, failed_questions, timeout_questions,
                    total_latency_ms, avg_latency_ms, started_at, completed_at, tags, notes, raw_result
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                evaluation['evaluation_id'],
                evaluation['agent_id'],
                evaluation['agent_name'],
                evaluation.get('agent_vendor', ''),
                evaluation.get('agent_version', '1.0'),
                evaluation['question_set_id'],
                evaluation['status'],
                evaluation.get('total_score', 0),
                evaluation.get('max_total_score', 0),
                evaluation.get('overall_percentage', 0),
                evaluation.get('total_questions', 0),
                evaluation.get('completed_questions', 0),
                evaluation.get('failed_questions', 0),
                evaluation.get('timeout_questions', 0),
                evaluation.get('total_latency_ms', 0),
                evaluation.get('avg_latency_ms', 0),
                evaluation.get('started_at'),
                evaluation.get('completed_at'),
                json.dumps(evaluation.get('tags', [])),
                evaluation.get('notes', ''),
                json.dumps(evaluation)
            ))

            # 保存详细结果
            for detail in evaluation.get('question_results', []):
                cursor.execute("""
                    INSERT INTO evaluation_details (
                        evaluation_id, question_id, dimension, agent_output,
                        parsed_output, latency_ms, score, max_score, status,
                        error_message, validation_results, tool_calls, executed_at
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    evaluation['evaluation_id'],
                    detail['question_id'],
                    detail['dimension'],
                    detail.get('agent_output', ''),
                    json.dumps(detail.get('parsed_output')),
                    detail.get('latency_ms', 0),
                    detail.get('score', 0),
                    detail.get('max_score', 0),
                    detail['status'],
                    detail.get('error_message', ''),
                    json.dumps(detail.get('validation_results', [])),
                    json.dumps(detail.get('tool_calls', [])),
                    detail.get('executed_at')
                ))

            return evaluation['evaluation_id']

    def get_evaluation(self, evaluation_id: str) -> Optional[Dict[str, Any]]:
        """获取评测结果"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM evaluations WHERE evaluation_id = ?", (evaluation_id,))
            row = cursor.fetchone()
            return dict(row) if row else None

    def get_agent_evaluations(self, agent_id: str, limit: int = 10) -> List[Dict[str, Any]]:
        """获取Agent的历史评测"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT * FROM evaluations
                WHERE agent_id = ? AND status = 'completed'
                ORDER BY created_at DESC
                LIMIT ?
            """, (agent_id, limit))
            return [dict(row) for row in cursor.fetchall()]

    def get_evaluation_trend(self, agent_id: str, months: int = 6) -> List[Dict[str, Any]]:
        """获取Agent的评测趋势"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(f"""
                SELECT
                    strftime('%Y-%m', created_at) as month,
                    AVG(overall_percentage) as avg_score,
                    COUNT(*) as evaluation_count
                FROM evaluations
                WHERE agent_id = ?
                    AND status = 'completed'
                    AND created_at >= date('now', '-{months} months')
                GROUP BY strftime('%Y-%m', created_at)
                ORDER BY month
            """, (agent_id,))
            return [dict(row) for row in cursor.fetchall()]

    # ========== 排行榜操作 ==========

    def save_leaderboard(self, leaderboard: Dict[str, Any]):
        """保存排行榜"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            for entry in leaderboard.get('entries', []):
                cursor.execute("""
                    INSERT INTO leaderboard_history (
                        leaderboard_id, name, evaluation_date, question_set_id,
                        agent_id, agent_name, vendor, version, agent_type,
                        rank, overall_score, overall_percentage,
                        knowledge_score, understanding_score, reasoning_score,
                        compliance_score, tools_score, change_from_last
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    leaderboard['leaderboard_id'],
                    leaderboard['name'],
                    leaderboard['evaluation_date'],
                    leaderboard['question_set_id'],
                    entry['agent_id'],
                    entry['agent_name'],
                    entry.get('vendor', ''),
                    entry.get('version', '1.0'),
                    entry.get('agent_type', 'unknown'),
                    entry['rank'],
                    entry['overall_score'],
                    entry['overall_percentage'],
                    entry.get('knowledge_score', 0),
                    entry.get('understanding_score', 0),
                    entry.get('reasoning_score', 0),
                    entry.get('compliance_score', 0),
                    entry.get('tools_score', 0),
                    entry.get('change', 0)
                ))

    def get_leaderboard(self, date: str) -> Optional[Dict[str, Any]]:
        """获取指定日期的排行榜"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT * FROM leaderboard_history
                WHERE evaluation_date = ?
                ORDER BY rank
            """, (date,))
            rows = cursor.fetchall()
            if not rows:
                return None
            first_row = dict(rows[0])
            return {
                'leaderboard_id': first_row['leaderboard_id'],
                'name': first_row['name'],
                'evaluation_date': first_row['evaluation_date'],
                'question_set_id': first_row['question_set_id'],
                'entries': [dict(row) for row in rows]
            }

    def get_latest_leaderboard(self) -> Optional[Dict[str, Any]]:
        """获取最新的排行榜"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT evaluation_date FROM leaderboard_history
                ORDER BY evaluation_date DESC
                LIMIT 1
            """)
            row = cursor.fetchone()
            if not row:
                return None
            return self.get_leaderboard(row['evaluation_date'])

    # ========== 竞技场操作 ==========

    def create_arena_session(self, session_id: str, name: str, config: Dict[str, Any]) -> str:
        """创建竞技场会话"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO arena_sessions (session_id, name, status, config)
                VALUES (?, ?, 'running', ?)
            """, (session_id, name, json.dumps(config)))
            return session_id

    def save_arena_event(self, session_id: str, event_type: str, data: Dict[str, Any]):
        """保存竞技场事件"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO arena_events (session_id, event_type, data)
                VALUES (?, ?, ?)
            """, (session_id, event_type, json.dumps(data)))

    def finish_arena_session(self, session_id: str, final_leaderboard: Dict[str, Any]):
        """结束竞技场会话"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                UPDATE arena_sessions
                SET status = 'finished',
                    ended_at = CURRENT_TIMESTAMP,
                    final_leaderboard = ?
                WHERE session_id = ?
            """, (json.dumps(final_leaderboard), session_id))

    def get_arena_session(self, session_id: str) -> Optional[Dict[str, Any]]:
        """获取竞技场会话"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM arena_sessions WHERE session_id = ?", (session_id,))
            row = cursor.fetchone()
            if not row:
                return None
            result = dict(row)
            result['config'] = json.loads(result.get('config', '{}'))
            result['final_leaderboard'] = json.loads(result.get('final_leaderboard', '{}'))
            return result

    def get_arena_events(self, session_id: str, limit: int = 100) -> List[Dict[str, Any]]:
        """获取竞技场事件"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT * FROM arena_events
                WHERE session_id = ?
                ORDER BY timestamp DESC
                LIMIT ?
            """, (session_id, limit))
            events = []
            for row in cursor.fetchall():
                event = dict(row)
                event['data'] = json.loads(event.get('data', '{}'))
                events.append(event)
            return events

    # ========== Agent注册操作 ==========

    def register_agent(self, agent_config: Dict[str, Any]) -> str:
        """注册Agent"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT OR REPLACE INTO registered_agents (
                    agent_id, name, vendor, version, agent_type,
                    base_url, model, system_prompt, config
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                agent_config['id'],
                agent_config['name'],
                agent_config['vendor'],
                agent_config.get('version', '1.0'),
                agent_config['agent_type'],
                agent_config.get('base_url', ''),
                agent_config['model'],
                agent_config.get('system_prompt', ''),
                json.dumps(agent_config)
            ))
            return agent_config['id']

    def get_registered_agents(self, active_only: bool = True) -> List[Dict[str, Any]]:
        """获取已注册的Agent"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            if active_only:
                cursor.execute("SELECT * FROM registered_agents WHERE is_active = 1")
            else:
                cursor.execute("SELECT * FROM registered_agents")
            return [dict(row) for row in cursor.fetchall()]

    def update_agent_test_result(self, agent_id: str, test_result: Dict[str, Any]):
        """更新Agent测试结果"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                UPDATE registered_agents
                SET last_tested_at = CURRENT_TIMESTAMP,
                    test_result = ?
                WHERE agent_id = ?
            """, (json.dumps(test_result), agent_id))

    # ========== 统计操作 ==========

    def get_statistics(self) -> Dict[str, Any]:
        """获取系统统计信息"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            stats = {}

            cursor.execute("SELECT COUNT(*) as count FROM evaluations")
            stats['total_evaluations'] = cursor.fetchone()['count']

            cursor.execute("SELECT COUNT(*) as count FROM registered_agents WHERE is_active = 1")
            stats['total_agents'] = cursor.fetchone()['count']

            cursor.execute("SELECT COUNT(DISTINCT evaluation_date) as count FROM leaderboard_history")
            stats['total_leaderboards'] = cursor.fetchone()['count']

            cursor.execute("""
                SELECT COUNT(*) as count FROM evaluations
                WHERE created_at >= date('now', '-7 days')
            """)
            stats['recent_evaluations'] = cursor.fetchone()['count']

            return stats


# 全局数据库实例
_db_instance: Optional[Database] = None


def get_database(db_path: str = None) -> Database:
    """获取数据库单例"""
    global _db_instance
    if _db_instance is None:
        _db_instance = Database(db_path)
    return _db_instance

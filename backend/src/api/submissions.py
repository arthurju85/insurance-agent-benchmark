"""
Agent 提交服务
处理用户/企业提交 Agent 参与排行榜或竞技场的申请
"""

import sqlite3
import json
from pathlib import Path
from typing import Optional, List, Dict, Any
from datetime import datetime
from contextlib import contextmanager
from pydantic import BaseModel, EmailStr, Field
from enum import Enum


class SubmissionStatus(str, Enum):
    """提交状态"""
    PENDING = "pending"  # 待审核
    REVIEWING = "reviewing"  # 审核中
    APPROVED = "approved"  # 已批准
    REJECTED = "rejected"  # 已拒绝
    CANCELLED = "cancelled"  # 已取消


class AgentType(str, Enum):
    """Agent 类型"""
    INSURER = "insurer"  # 保险公司自研
    TECH = "tech"  # 科技公司
    OPENSOURCE = "opensource"  # 开源


class ModelPlatform(str, Enum):
    """模型平台"""
    OPENAI = "openai"
    AZURE_OPENAI = "azure_openai"
    VLLM = "vllm"
    CLAUDE = "claude"
    GEMINI = "gemini"
    OTHER = "other"


class AgentSubmission(BaseModel):
    """Agent 提交申请"""
    applicant_name: str = Field(..., min_length=1, max_length=100, description="申请人姓名")
    company_name: Optional[str] = Field(None, max_length=200, description="公司名称")
    email: str = Field(..., description="联系邮箱")
    phone: str = Field(..., pattern=r'^\+?1?\d{9,15}$', description="手机号")
    agent_name: str = Field(..., min_length=1, max_length=100, description="Agent 名称")
    agent_type: AgentType = Field(..., description="Agent 类型")
    model_platform: ModelPlatform = Field(..., description="模型平台")
    api_endpoint: Optional[str] = Field(None, max_length=500, description="API 端点")
    notes: Optional[str] = Field(None, max_length=1000, description="备注说明")


class AgentSubmissionRecord(AgentSubmission):
    """Agent 提交记录（包含审核信息）"""
    id: str
    status: SubmissionStatus
    submitted_at: str
    reviewed_at: Optional[str] = None
    reviewed_by: Optional[str] = None
    review_notes: Optional[str] = None
    ip_address: Optional[str] = None


class SubmissionCreateRequest(AgentSubmission):
    """创建提交请求"""
    captcha_token: Optional[str] = Field(None, description="验证码 token")


class SubmissionUpdateRequest(BaseModel):
    """更新提交请求（管理员用）"""
    status: Optional[SubmissionStatus] = None
    review_notes: Optional[str] = None


class SubmissionListResponse(BaseModel):
    """提交列表响应"""
    total: int
    submissions: List[AgentSubmissionRecord]


class RateLimitConfig(BaseModel):
    """限流配置"""
    max_requests: int = 3  # 24 小时内最大请求数
    window_seconds: int = 86400  # 时间窗口（秒）


class SubmissionsDatabase:
    """
    Agent 提交数据库管理类
    """

    def __init__(self, db_path: str = None):
        if db_path is None:
            current_file = Path(__file__).resolve()
            data_dir = current_file.parent.parent.parent / "data"
            data_dir.mkdir(exist_ok=True)
            db_path = data_dir / "insurance_benchmark.db"

        self.db_path = str(db_path)
        self._init_tables()

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

    def _init_tables(self):
        """初始化 Agent 提交表"""
        with self.get_connection() as conn:
            cursor = conn.cursor()

            cursor.execute("""
                CREATE TABLE IF NOT EXISTS agent_submissions (
                    id TEXT PRIMARY KEY,
                    applicant_name TEXT NOT NULL,
                    company_name TEXT,
                    email TEXT NOT NULL,
                    phone TEXT NOT NULL,
                    agent_name TEXT NOT NULL,
                    agent_type TEXT NOT NULL,
                    model_platform TEXT NOT NULL,
                    api_endpoint TEXT,
                    notes TEXT,
                    status TEXT NOT NULL DEFAULT 'pending',
                    submitted_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    reviewed_at TIMESTAMP,
                    reviewed_by TEXT,
                    review_notes TEXT,
                    ip_address TEXT,
                    UNIQUE(email, agent_name)
                )
            """)

            # 创建索引
            cursor.execute("""
                CREATE INDEX IF NOT EXISTS idx_submissions_status
                ON agent_submissions(status)
            """)
            cursor.execute("""
                CREATE INDEX IF NOT EXISTS idx_submissions_date
                ON agent_submissions(submitted_at)
            """)

            # 限流记录表
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS submission_rate_limits (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    ip_address TEXT NOT NULL,
                    email TEXT NOT NULL,
                    submitted_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)

            cursor.execute("""
                CREATE INDEX IF NOT EXISTS idx_rate_limits_ip
                ON submission_rate_limits(ip_address)
            """)

    def create_submission(self, submission: AgentSubmission, ip_address: str = None) -> str:
        """创建 Agent 提交申请"""
        import uuid
        submission_id = str(uuid.uuid4())[:8].upper()

        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO agent_submissions (
                    id, applicant_name, company_name, email, phone,
                    agent_name, agent_type, model_platform, api_endpoint, notes,
                    status, ip_address
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                submission_id,
                submission.applicant_name,
                submission.company_name,
                submission.email,
                submission.phone,
                submission.agent_name,
                submission.agent_type.value,
                submission.model_platform.value,
                submission.api_endpoint,
                submission.notes,
                SubmissionStatus.PENDING.value,
                ip_address
            ))

            return submission_id

    def get_submission(self, submission_id: str) -> Optional[AgentSubmissionRecord]:
        """获取提交详情"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM agent_submissions WHERE id = ?", (submission_id,))
            row = cursor.fetchone()

            if not row:
                return None

            return self._row_to_record(row)

    def get_submissions(self, status: Optional[SubmissionStatus] = None, limit: int = 100) -> List[AgentSubmissionRecord]:
        """获取提交列表"""
        with self.get_connection() as conn:
            cursor = conn.cursor()

            if status:
                cursor.execute("""
                    SELECT * FROM agent_submissions
                    WHERE status = ?
                    ORDER BY submitted_at DESC
                    LIMIT ?
                """, (status.value, limit))
            else:
                cursor.execute("""
                    SELECT * FROM agent_submissions
                    ORDER BY submitted_at DESC
                    LIMIT ?
                """, (limit,))

            return [self._row_to_record(row) for row in cursor.fetchall()]

    def update_submission(self, submission_id: str, status: Optional[SubmissionStatus] = None,
                         review_notes: Optional[str] = None, reviewed_by: Optional[str] = None) -> bool:
        """更新提交状态"""
        with self.get_connection() as conn:
            cursor = conn.cursor()

            updates = []
            values = []

            if status:
                updates.append("status = ?")
                values.append(status.value)
                if status in [SubmissionStatus.APPROVED, SubmissionStatus.REJECTED]:
                    updates.append("reviewed_at = CURRENT_TIMESTAMP")

            if review_notes is not None:
                updates.append("review_notes = ?")
                values.append(review_notes)

            if reviewed_by:
                updates.append("reviewed_by = ?")
                values.append(reviewed_by)

            if not updates:
                return False

            values.append(submission_id)
            cursor.execute(f"""
                UPDATE agent_submissions
                SET {', '.join(updates)}
                WHERE id = ?
            """, values)

            return cursor.rowcount > 0

    def delete_submission(self, submission_id: str) -> bool:
        """删除提交记录"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("DELETE FROM agent_submissions WHERE id = ?", (submission_id,))
            return cursor.rowcount > 0

    def check_rate_limit(self, ip_address: str, email: str, config: RateLimitConfig = None) -> bool:
        """检查限流（返回 True 表示允许请求）"""
        if config is None:
            config = RateLimitConfig()

        with self.get_connection() as conn:
            cursor = conn.cursor()

            # 检查 IP 限制
            cursor.execute("""
                SELECT COUNT(*) as count FROM submission_rate_limits
                WHERE ip_address = ? AND submitted_at >= datetime('now', ?)
            """, (ip_address, f'-{config.window_seconds} seconds'))

            ip_count = cursor.fetchone()['count']
            if ip_count >= config.max_requests:
                return False

            # 检查邮箱限制
            cursor.execute("""
                SELECT COUNT(*) as count FROM submission_rate_limits
                WHERE email = ? AND submitted_at >= datetime('now', ?)
            """, (email, f'-{config.window_seconds} seconds'))

            email_count = cursor.fetchone()['count']
            if email_count >= config.max_requests:
                return False

            return True

    def record_rate_limit(self, ip_address: str, email: str):
        """记录限流请求"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO submission_rate_limits (ip_address, email)
                VALUES (?, ?)
            """, (ip_address, email))

    def get_rate_limit_remaining(self, ip_address: str, email: str, config: RateLimitConfig = None) -> Dict[str, int]:
        """获取剩余请求次数"""
        if config is None:
            config = RateLimitConfig()

        with self.get_connection() as conn:
            cursor = conn.cursor()

            cursor.execute("""
                SELECT COUNT(*) as count FROM submission_rate_limits
                WHERE ip_address = ? AND submitted_at >= datetime('now', ?)
            """, (ip_address, f'-{config.window_seconds} seconds'))
            ip_remaining = config.max_requests - cursor.fetchone()['count']

            cursor.execute("""
                SELECT COUNT(*) as count FROM submission_rate_limits
                WHERE email = ? AND submitted_at >= datetime('now', ?)
            """, (email, f'-{config.window_seconds} seconds'))
            email_remaining = config.max_requests - cursor.fetchone()['count']

            return {
                "ip_remaining": max(0, ip_remaining),
                "email_remaining": max(0, email_remaining),
                "window_seconds": config.window_seconds
            }

    def _row_to_record(self, row: sqlite3.Row) -> AgentSubmissionRecord:
        """将数据库行转换为记录对象"""
        return AgentSubmissionRecord(
            id=row['id'],
            applicant_name=row['applicant_name'],
            company_name=row.get('company_name'),
            email=row['email'],
            phone=row['phone'],
            agent_name=row['agent_name'],
            agent_type=AgentType(row['agent_type']),
            model_platform=ModelPlatform(row['model_platform']),
            api_endpoint=row.get('api_endpoint'),
            notes=row.get('notes'),
            status=SubmissionStatus(row['status']),
            submitted_at=row['submitted_at'],
            reviewed_at=row.get('reviewed_at'),
            reviewed_by=row.get('reviewed_by'),
            review_notes=row.get('review_notes'),
            ip_address=row.get('ip_address')
        )

    def get_statistics(self) -> Dict[str, int]:
        """获取提交统计"""
        with self.get_connection() as conn:
            cursor = conn.cursor()

            stats = {}

            cursor.execute("SELECT COUNT(*) as count FROM agent_submissions")
            stats['total_submissions'] = cursor.fetchone()['count']

            cursor.execute("SELECT COUNT(*) as count FROM agent_submissions WHERE status = 'pending'")
            stats['pending'] = cursor.fetchone()['count']

            cursor.execute("SELECT COUNT(*) as count FROM agent_submissions WHERE status = 'approved'")
            stats['approved'] = cursor.fetchone()['count']

            cursor.execute("SELECT COUNT(*) as count FROM agent_submissions WHERE status = 'rejected'")
            stats['rejected'] = cursor.fetchone()['count']

            return stats


# 全局数据库实例
_submissions_db: Optional[SubmissionsDatabase] = None


def get_submissions_database() -> SubmissionsDatabase:
    """获取数据库单例"""
    global _submissions_db
    if _submissions_db is None:
        _submissions_db = SubmissionsDatabase()
    return _submissions_db

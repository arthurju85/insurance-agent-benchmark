"""
管理员后台模块
提供题库管理、评测监控、系统配置等功能
"""

import json
from typing import List, Dict, Optional, Any
from datetime import datetime, timedelta
from dataclasses import dataclass, field
from pathlib import Path

try:
    from ..db.database import get_database
    from ..db.question_repo import get_repository
    from ..db.variation_engine import VariationEngine
    from .submissions import get_submissions_database, SubmissionStatus
except ImportError:
    import sys
    import os
    sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
    from db.database import get_database
    from db.question_repo import get_repository
    from db.variation_engine import VariationEngine
    from submissions import get_submissions_database, SubmissionStatus


@dataclass
class AdminDashboardStats:
    """管理员仪表盘统计数据"""
    # 题库统计
    total_questions: int = 0
    questions_by_dimension: Dict[str, int] = field(default_factory=dict)
    questions_by_difficulty: Dict[str, int] = field(default_factory=dict)
    variant_questions: int = 0

    # 评测统计
    total_evaluations: int = 0
    evaluations_this_week: int = 0
    evaluations_today: int = 0
    avg_score: float = 0.0

    # Agent统计
    registered_agents: int = 0
    active_agents: int = 0

    # 系统状态
    system_health: str = "healthy"
    last_crawl_time: Optional[datetime] = None
    storage_usage: Dict = field(default_factory=dict)


class QuestionManager:
    """
    题目管理器
    提供题目的增删改查、审核、发布等功能
    """

    def __init__(self):
        self.repo = get_repository()
        self.db = get_database()

    def list_questions(
        self,
        dimension: Optional[str] = None,
        difficulty: Optional[str] = None,
        is_variant: Optional[bool] = None,
        keyword: Optional[str] = None,
        page: int = 1,
        page_size: int = 20
    ) -> Dict:
        """分页查询题目列表"""
        all_questions = self.repo.load_all_questions()

        # 过滤
        filtered = all_questions
        if dimension:
            filtered = [q for q in filtered if q.dimension == dimension]
        if difficulty:
            filtered = [q for q in filtered if q.difficulty == difficulty]
        if is_variant is not None:
            filtered = [q for q in filtered if q.is_variant == is_variant]
        if keyword:
            keyword_lower = keyword.lower()
            filtered = [
                q for q in filtered
                if keyword_lower in q.content.lower() or
                keyword_lower in (q.title or '').lower()
            ]

        # 分页
        total = len(filtered)
        start = (page - 1) * page_size
        end = start + page_size
        page_data = filtered[start:end]

        return {
            "total": total,
            "page": page,
            "page_size": page_size,
            "total_pages": (total + page_size - 1) // page_size,
            "questions": [
                {
                    "id": q.question_id,
                    "title": q.title,
                    "dimension": q.dimension,
                    "difficulty": q.difficulty,
                    "type": q.question_type,
                    "is_variant": q.is_variant,
                    "parent_id": q.parent_id,
                    "score": q.score,
                    "tags": q.tags
                }
                for q in page_data
            ]
        }

    def get_question_detail(self, question_id: str) -> Optional[Dict]:
        """获取题目详情"""
        question = self.repo.get_question(question_id)
        if not question:
            return None

        return {
            "id": question.question_id,
            "title": question.title,
            "content": question.content,
            "context": question.context,
            "dimension": question.dimension,
            "difficulty": question.difficulty,
            "type": question.question_type,
            "score": question.score,
            "ground_truth": question.ground_truth,
            "validation_rules": question.validation_rules.model_dump() if question.validation_rules else None,
            "expected_schema": question.expected_schema.model_dump() if question.expected_schema else None,
            "is_variant": question.is_variant,
            "parent_id": question.parent_id,
            "variant_seed": question.variant_seed,
            "tags": question.tags,
            "source": question.source,
            "version": question.version,
            "created_at": question.created_at
        }

    def update_question(self, question_id: str, updates: Dict) -> bool:
        """更新题目"""
        question = self.repo.get_question(question_id)
        if not question:
            return False

        # 应用更新
        for key, value in updates.items():
            if hasattr(question, key):
                setattr(question, key, value)

        question.updated_at = datetime.now().isoformat()

        # 保存
        self.repo.save_question(question)
        return True

    def delete_question(self, question_id: str) -> bool:
        """删除题目（软删除）"""
        question = self.repo.get_question(question_id)
        if not question:
            return False

        # 标记为已删除
        question.tags.append("deleted")
        question.updated_at = datetime.now().isoformat()
        self.repo.save_question(question)
        return True

    def create_variants(self, question_id: str, count: int = 3, seed: Optional[int] = None) -> List[str]:
        """为题⽬生成变体"""
        question = self.repo.get_question(question_id)
        if not question:
            return []

        engine = VariationEngine(seed=seed)
        variations = engine.generate_variations(question, count)

        # 保存变体
        variant_ids = []
        for var in variations:
            self.repo.save_question(var)
            variant_ids.append(var.question_id)

        return variant_ids

    def import_questions(self, questions_data: List[Dict], source: str = "import") -> Dict:
        """批量导入题目"""
        from ..models.question import Question

        imported = 0
        failed = 0
        errors = []

        for data in questions_data:
            try:
                # 添加元数据
                data['source'] = source
                data['imported_at'] = datetime.now().isoformat()

                question = Question(**data)
                self.repo.save_question(question)
                imported += 1
            except Exception as e:
                failed += 1
                errors.append({"data": data, "error": str(e)})

        return {
            "imported": imported,
            "failed": failed,
            "total": len(questions_data),
            "errors": errors[:5]  # 只返回前5个错误
        }


class EvaluationMonitor:
    """
    评测监控器
    监控评测运行状态、查看历史记录、分析趋势
    """

    def __init__(self):
        self.db = get_database()

    def get_running_evaluations(self) -> List[Dict]:
        """获取正在运行的评测"""
        with self.db.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT * FROM evaluations
                WHERE status = 'running'
                ORDER BY started_at DESC
            """)
            rows = cursor.fetchall()
            return [dict(row) for row in rows]

    def get_recent_evaluations(self, days: int = 7, limit: int = 50) -> List[Dict]:
        """获取最近的评测记录"""
        with self.db.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(f"""
                SELECT * FROM evaluations
                WHERE created_at >= date('now', '-{days} days')
                ORDER BY created_at DESC
                LIMIT ?
            """, (limit,))
            rows = cursor.fetchall()
            return [dict(row) for row in rows]

    def get_evaluation_detail(self, evaluation_id: str) -> Optional[Dict]:
        """获取评测详情"""
        eval_data = self.db.get_evaluation(evaluation_id)
        if not eval_data:
            return None

        # 获取详细结果
        with self.db.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT * FROM evaluation_details
                WHERE evaluation_id = ?
            """, (evaluation_id,))
            details = [dict(row) for row in cursor.fetchall()]

        return {
            "summary": eval_data,
            "details": details
        }

    def get_agent_performance(self, agent_id: str, months: int = 6) -> Dict:
        """获取Agent性能趋势"""
        trend = self.db.get_evaluation_trend(agent_id, months)

        # 计算统计数据
        if trend:
            scores = [t['avg_score'] for t in trend]
            return {
                "agent_id": agent_id,
                "trend": trend,
                "avg_score": sum(scores) / len(scores),
                "best_score": max(scores),
                "worst_score": min(scores),
                "total_evaluations": sum(t['evaluation_count'] for t in trend)
            }

        return {
            "agent_id": agent_id,
            "trend": [],
            "avg_score": 0,
            "total_evaluations": 0
        }

    def get_leaderboard_history(self, months: int = 12) -> List[Dict]:
        """获取排行榜历史"""
        with self.db.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(f"""
                SELECT
                    evaluation_date,
                    COUNT(DISTINCT agent_id) as agent_count,
                    AVG(overall_percentage) as avg_score,
                    MAX(overall_percentage) as top_score
                FROM leaderboard_history
                WHERE evaluation_date >= date('now', '-{months} months')
                GROUP BY evaluation_date
                ORDER BY evaluation_date DESC
            """)
            return [dict(row) for row in cursor.fetchall()]


class SystemManager:
    """
    系统管理器
    系统配置、日志查看、数据备份等
    """

    def __init__(self):
        self.db = get_database()
        self.repo = get_repository()

    def get_dashboard_stats(self) -> AdminDashboardStats:
        """获取仪表盘统计数据"""
        stats = AdminDashboardStats()

        # 题库统计
        repo_stats = self.repo.get_statistics()
        stats.total_questions = repo_stats.get('total_questions', 0)
        stats.questions_by_dimension = repo_stats.get('by_dimension', {})
        stats.questions_by_difficulty = repo_stats.get('by_difficulty', {})

        # 计算变体题数量
        all_questions = self.repo.load_all_questions()
        stats.variant_questions = sum(1 for q in all_questions if q.is_variant)

        # 评测统计
        db_stats = self.db.get_statistics()
        stats.total_evaluations = db_stats.get('total_evaluations', 0)
        stats.registered_agents = db_stats.get('total_agents', 0)

        # 本周评测
        with self.db.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT COUNT(*) as count FROM evaluations
                WHERE created_at >= date('now', '-7 days')
            """)
            stats.evaluations_this_week = cursor.fetchone()['count']

            # 今日评测
            cursor.execute("""
                SELECT COUNT(*) as count FROM evaluations
                WHERE date(created_at) = date('now')
            """)
            stats.evaluations_today = cursor.fetchone()['count']

            # 平均分数
            cursor.execute("""
                SELECT AVG(overall_percentage) as avg
                FROM evaluations
                WHERE status = 'completed'
            """)
            result = cursor.fetchone()
            stats.avg_score = round(result['avg'] or 0, 2)

        # 活跃Agent
        agents = self.db.get_registered_agents(active_only=True)
        stats.active_agents = len(agents)

        return stats

    def get_system_logs(self, level: str = "INFO", limit: int = 100) -> List[Dict]:
        """获取系统日志（简化版）"""
        # 实际实现应该从日志文件或日志服务获取
        return []

    def backup_data(self, backup_path: Optional[str] = None) -> str:
        """备份数据"""
        if backup_path is None:
            backup_dir = Path("backend/data/backups")
            backup_dir.mkdir(exist_ok=True)
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            backup_path = backup_dir / f"backup_{timestamp}.json"

        # 收集所有数据
        all_questions = self.repo.load_all_questions()
        all_evaluations = []

        with self.db.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM evaluations")
            all_evaluations = [dict(row) for row in cursor.fetchall()]

        backup_data = {
            "timestamp": datetime.now().isoformat(),
            "questions": [q.model_dump() for q in all_questions],
            "evaluations": all_evaluations
        }

        with open(backup_path, 'w', encoding='utf-8') as f:
            json.dump(backup_data, f, ensure_ascii=False, indent=2)

        return str(backup_path)

    def get_config(self) -> Dict:
        """获取系统配置"""
        return {
            "evaluation": {
                "default_timeout": 30,
                "max_concurrent": 5,
                "retry_attempts": 3
            },
            "scoring": {
                "partial_scoring_enabled": True,
                "keyword_weight": 0.3,
                "conclusion_weight": 0.7
            },
            "crawler": {
                "auto_crawl_enabled": False,
                "crawl_interval_hours": 24
            },
            "variation": {
                "default_variation_count": 3,
                "enable_date_variation": True,
                "enable_amount_variation": True
            }
        }

    def update_config(self, config_updates: Dict) -> bool:
        """更新系统配置"""
        # 实际实现应该保存到配置文件或数据库
        return True


# 便捷函数
def get_admin_dashboard() -> Dict:
    """获取管理员仪表盘数据"""
    manager = SystemManager()
    stats = manager.get_dashboard_stats()

    return {
        "questions": {
            "total": stats.total_questions,
            "by_dimension": stats.questions_by_dimension,
            "by_difficulty": stats.questions_by_difficulty,
            "variants": stats.variant_questions
        },
        "evaluations": {
            "total": stats.total_evaluations,
            "this_week": stats.evaluations_this_week,
            "today": stats.evaluations_today,
            "avg_score": stats.avg_score
        },
        "agents": {
            "registered": stats.registered_agents,
            "active": stats.active_agents
        },
        "system": {
            "health": stats.system_health,
            "last_crawl": stats.last_crawl_time.isoformat() if stats.last_crawl_time else None
        }
    }


class SubmissionManager:
    """
    Agent 提交审核管理器
    审核用户/企业提交的 Agent 申请
    """

    def __init__(self):
        self.sub_db = get_submissions_database()

    def list_submissions(
        self,
        status: Optional[SubmissionStatus] = None,
        page: int = 1,
        page_size: int = 20
    ) -> Dict:
        """分页查询提交列表"""
        all_submissions = self.sub_db.get_submissions(status=status, limit=500)

        # 分页
        total = len(all_submissions)
        start = (page - 1) * page_size
        end = start + page_size
        page_data = all_submissions[start:end]

        return {
            "total": total,
            "page": page,
            "page_size": page_size,
            "total_pages": (total + page_size - 1) // page_size,
            "submissions": [
                {
                    "id": s.id,
                    "applicant_name": s.applicant_name,
                    "company_name": s.company_name,
                    "email": s.email,
                    "phone": s.phone,
                    "agent_name": s.agent_name,
                    "agent_type": s.agent_type.value,
                    "model_platform": s.model_platform.value,
                    "api_endpoint": s.api_endpoint,
                    "status": s.status.value,
                    "submitted_at": s.submitted_at,
                    "reviewed_at": s.reviewed_at,
                    "reviewed_by": s.reviewed_by,
                    "review_notes": s.review_notes
                }
                for s in page_data
            ]
        }

    def get_submission_detail(self, submission_id: str) -> Optional[Dict]:
        """获取提交详情"""
        submission = self.sub_db.get_submission(submission_id)
        if not submission:
            return None

        return {
            "id": submission.id,
            "applicant_name": submission.applicant_name,
            "company_name": submission.company_name,
            "email": submission.email,
            "phone": submission.phone,
            "agent_name": submission.agent_name,
            "agent_type": submission.agent_type.value,
            "model_platform": submission.model_platform.value,
            "api_endpoint": submission.api_endpoint,
            "notes": submission.notes,
            "status": submission.status.value,
            "submitted_at": submission.submitted_at,
            "reviewed_at": submission.reviewed_at,
            "reviewed_by": submission.reviewed_by,
            "review_notes": submission.review_notes,
            "ip_address": submission.ip_address
        }

    def update_submission_status(
        self,
        submission_id: str,
        status: SubmissionStatus,
        review_notes: Optional[str] = None,
        reviewed_by: Optional[str] = None
    ) -> bool:
        """更新提交状态"""
        return self.sub_db.update_submission(
            submission_id,
            status=status,
            review_notes=review_notes,
            reviewed_by=reviewed_by
        )

    def get_statistics(self) -> Dict:
        """获取提交统计"""
        return self.sub_db.get_statistics()

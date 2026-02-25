"""
题库存储和管理模块
"""

import json
import os
from typing import List, Dict, Optional
from pathlib import Path

try:
    from ..models.question import Question, QuestionSet
except ImportError:
    import sys
    import os
    sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
    from models.question import Question, QuestionSet


class QuestionRepository:
    """
    题库仓库
    管理题目的加载、查询和保存
    """

    def __init__(self, data_dir: str = None):
        if data_dir is None:
            # 默认使用项目内的data目录
            current_file = Path(__file__).resolve()
            self.data_dir = current_file.parent.parent.parent / "data" / "questions"
        else:
            self.data_dir = Path(data_dir)

        self._questions: Dict[str, Question] = {}
        self._sets: Dict[str, QuestionSet] = {}

    def load_all_questions(self) -> List[Question]:
        """
        加载所有题库文件
        """
        questions = []

        for file_path in self.data_dir.glob("*.json"):
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    data = json.load(f)

                # 检查是否是题目集合
                if "questions" in data:
                    for q_data in data["questions"]:
                        question = Question(**q_data)
                        questions.append(question)
                        self._questions[question.question_id] = question

                    # 记录题目集合
                    if "metadata" in data:
                        meta = data["metadata"]
                        question_set = QuestionSet(
                            set_id=meta.get("set_id", file_path.stem),
                            name=meta.get("name", file_path.stem),
                            description=meta.get("description"),
                            questions=[q.question_id for q in questions[-len(data["questions"]):]],
                            total_score=meta.get("total_score", 0)
                        )
                        self._sets[question_set.set_id] = question_set

            except Exception as e:
                print(f"加载题库文件失败 {file_path}: {e}")

        return questions

    def get_question(self, question_id: str) -> Optional[Question]:
        """获取指定题目"""
        if not self._questions:
            self.load_all_questions()
        return self._questions.get(question_id)

    def get_questions_by_dimension(self, dimension: str) -> List[Question]:
        """按维度获取题目"""
        if not self._questions:
            self.load_all_questions()
        return [q for q in self._questions.values() if q.dimension == dimension]

    def get_questions_by_difficulty(self, difficulty: str) -> List[Question]:
        """按难度获取题目"""
        if not self._questions:
            self.load_all_questions()
        return [q for q in self._questions.values() if q.difficulty == difficulty]

    def get_question_set(self, set_id: str) -> Optional[QuestionSet]:
        """获取题目集合"""
        if not self._sets:
            self.load_all_questions()
        return self._sets.get(set_id)

    def save_question(self, question: Question, file_name: str = None):
        """保存单个题目"""
        if file_name is None:
            file_name = f"{question.question_id}.json"

        file_path = self.data_dir / file_name

        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(question.model_dump(), f, ensure_ascii=False, indent=2)

    def save_question_set(self, questions: List[Question], metadata: dict, file_name: str):
        """保存题目集合"""
        file_path = self.data_dir / file_name

        data = {
            "metadata": metadata,
            "questions": [q.model_dump() for q in questions]
        }

        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)

    def get_all_dimensions(self) -> List[str]:
        """获取所有维度"""
        if not self._questions:
            self.load_all_questions()
        return list(set(q.dimension for q in self._questions.values()))

    def get_statistics(self) -> dict:
        """获取题库统计信息"""
        if not self._questions:
            self.load_all_questions()

        stats = {
            "total_questions": len(self._questions),
            "by_dimension": {},
            "by_difficulty": {},
            "by_type": {}
        }

        for q in self._questions.values():
            # 按维度统计
            stats["by_dimension"][q.dimension] = stats["by_dimension"].get(q.dimension, 0) + 1
            # 按难度统计
            stats["by_difficulty"][q.difficulty] = stats["by_difficulty"].get(q.difficulty, 0) + 1
            # 按类型统计
            stats["by_type"][q.question_type] = stats["by_type"].get(q.question_type, 0) + 1

        return stats


# 全局题库仓库实例
_repo_instance: Optional[QuestionRepository] = None


def get_repository(data_dir: str = None) -> QuestionRepository:
    """获取题库仓库单例"""
    global _repo_instance
    if _repo_instance is None:
        _repo_instance = QuestionRepository(data_dir)
    return _repo_instance

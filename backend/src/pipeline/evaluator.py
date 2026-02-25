"""
评测流水线
执行完整的Agent评测流程
"""

import asyncio
import time
from typing import List, Optional, Dict, Any
from datetime import datetime

from models.agent import AgentConfig
from models.question import Question
from models.evaluation import (
    EvaluationResult, QuestionResult, EvaluationStatus, ValidationResult
)
from sandbox.factory import get_agent_adapter
from evaluators.factory import EvaluatorFactory
from db.question_repo import get_repository
from db.database import get_database


class EvaluationPipeline:
    """
    评测流水线
    负责执行完整的Agent评测流程
    """

    def __init__(
        self,
        agent_config: AgentConfig,
        concurrency: int = 3,
        timeout: int = 60
    ):
        self.agent_config = agent_config
        self.concurrency = concurrency
        self.timeout = timeout
        self.results: List[QuestionResult] = []

    async def evaluate_single_question(
        self,
        question: Question,
        semaphore: asyncio.Semaphore
    ) -> QuestionResult:
        """
        评测单道题目
        """
        async with semaphore:
            start_time = time.time()

            # 构建提示词
            prompt = self._build_prompt(question)

            # 调用Agent
            try:
                adapter = create_adapter(self.agent_config)

                agent_response = await asyncio.wait_for(
                    adapter.invoke(prompt),
                    timeout=self.timeout
                )

                latency_ms = (time.time() - start_time) * 1000

                # 解析输出
                parsed_output = self._try_parse_json(agent_response.content)

                # 评分
                evaluation_result = EvaluatorFactory.evaluate_question(
                    question=question,
                    agent_output=agent_response.content,
                    parsed_output=parsed_output,
                    tool_calls=agent_response.tool_calls
                )

                # 构建结果
                result = QuestionResult(
                    question_id=question.question_id,
                    dimension=question.dimension,
                    agent_output=agent_response.content,
                    parsed_output=parsed_output,
                    latency_ms=latency_ms,
                    score=evaluation_result["score"],
                    max_score=evaluation_result["max_score"],
                    validation_results=evaluation_result["validation_results"],
                    tool_calls=agent_response.tool_calls,
                    status=EvaluationStatus.COMPLETED
                )

                await adapter.close()

            except asyncio.TimeoutError:
                latency_ms = self.timeout * 1000
                result = QuestionResult(
                    question_id=question.question_id,
                    dimension=question.dimension,
                    agent_output="",
                    latency_ms=latency_ms,
                    score=0.0,
                    max_score=question.score,
                    status=EvaluationStatus.TIMEOUT,
                    error_message=f"执行超时（{self.timeout}秒）"
                )

            except Exception as e:
                latency_ms = (time.time() - start_time) * 1000
                result = QuestionResult(
                    question_id=question.question_id,
                    dimension=question.dimension,
                    agent_output="",
                    latency_ms=latency_ms,
                    score=0.0,
                    max_score=question.score,
                    status=EvaluationStatus.FAILED,
                    error_message=str(e)
                )

            return result

    def _build_prompt(self, question: Question) -> str:
        """
        构建评测提示词
        """
        prompt_parts = []

        if question.title:
            prompt_parts.append(f"【题目】{question.title}")

        if question.description:
            prompt_parts.append(f"【说明】{question.description}")

        prompt_parts.append(f"【问题】\n{question.content}")

        if question.context:
            prompt_parts.append(f"【背景信息】\n{question.context}")

        # 添加输出格式要求
        if question.expected_schema and question.expected_schema.output_instructions:
            prompt_parts.append(f"\n【输出要求】\n{question.expected_schema.output_instructions}")

        return "\n\n".join(prompt_parts)

    def _try_parse_json(self, text: str) -> Optional[Dict[str, Any]]:
        """
        尝试解析JSON
        """
        import json
        import re

        # 直接解析
        try:
            return json.loads(text)
        except json.JSONDecodeError:
            pass

        # 提取JSON代码块
        patterns = [
            r'```json\s*(.*?)\s*```',
            r'```\s*(.*?)\s*```',
            r'\{.*\}',
        ]

        for pattern in patterns:
            match = re.search(pattern, text, re.DOTALL)
            if match:
                try:
                    return json.loads(match.group(1) if pattern != r'\{.*\}' else match.group(0))
                except json.JSONDecodeError:
                    continue

        return None

    async def evaluate_questions(
        self,
        questions: List[Question]
    ) -> EvaluationResult:
        """
        评测多道题目
        """
        evaluation_id = f"eval_{datetime.now().strftime('%Y%m%d_%H%M%S')}"

        result = EvaluationResult(
            evaluation_id=evaluation_id,
            agent_id=self.agent_config.id,
            agent_name=self.agent_config.name,
            question_set_id="custom",
            status=EvaluationStatus.RUNNING,
            started_at=datetime.now().isoformat()
        )

        # 使用信号量控制并发
        semaphore = asyncio.Semaphore(self.concurrency)

        # 创建任务
        tasks = [
            self.evaluate_single_question(q, semaphore)
            for q in questions
        ]

        # 执行并收集结果
        for i, task in enumerate(asyncio.as_completed(tasks)):
            question_result = await task
            result.question_results.append(question_result)
            result.completed_questions = i + 1
            result.progress = (i + 1) / len(questions) * 100

        # 计算汇总
        result.status = EvaluationStatus.COMPLETED
        result.completed_at = datetime.now().isoformat()
        result.calculate_summary()

        # 保存到数据库
        try:
            db = get_database()
            db.save_evaluation(result.model_dump())
            print(f"✅ Evaluation saved to database: {result.evaluation_id}")
        except Exception as e:
            print(f"⚠️ Failed to save evaluation to database: {e}")

        return result

    async def evaluate_question_set(self, set_id: str) -> EvaluationResult:
        """
        评测指定的题目集合
        """
        repo = get_repository()
        question_set = repo.get_question_set(set_id)

        if not question_set:
            raise ValueError(f"题目集合不存在: {set_id}")

        questions = [
            repo.get_question(qid)
            for qid in question_set.questions
        ]
        questions = [q for q in questions if q is not None]

        return await self.evaluate_questions(questions)


# 便捷函数
async def evaluate_agent(
    agent_config: AgentConfig,
    questions: List[Question],
    concurrency: int = 3
) -> EvaluationResult:
    """
    便捷函数：评测Agent
    """
    pipeline = EvaluationPipeline(agent_config, concurrency=concurrency)
    return await pipeline.evaluate_questions(questions)

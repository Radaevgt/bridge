import json
import logging
import uuid

import httpx
from fastapi import HTTPException, status
from sqlalchemy import or_, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.config import settings
from app.models.chat import ChatRoom, Message
from app.models.lesson_plan import LessonPlan, LessonPlanStatus
from app.models.task_request import TaskRequest
from app.schemas.lesson_plan import LessonPlanGenerateRequest

logger = logging.getLogger(__name__)

SYSTEM_PROMPT = """You are an expert lesson planner working on the Bridge platform.
You receive a chat conversation between a specialist (tutor/consultant) and a client,
plus optional context about the task/request.

Your job: generate COMPREHENSIVE, DETAILED lesson materials that are sufficient for a full
60-90 minute session. The materials should be ready to use by the specialist without
additional preparation.

CRITICAL RULES:
1. Detect the language used in the conversation and generate ALL content in that SAME language.
2. Return ONLY valid JSON with exactly these keys:
   {
     "lesson_content": "...",
     "practice_exercises": "...",
     "homework": "...",
     "language": "en"
   }
3. Each section must be well-formatted Markdown with headers (##, ###), lists, bold text,
   code blocks (if relevant), tables, and real-world examples.

CONTENT REQUIREMENTS:
4. "lesson_content" (1500-2500 words minimum):
   - Start with clear learning objectives (3-5 bullet points)
   - Provide detailed theoretical foundation with explanations
   - Include 3-5 real-world examples with step-by-step walkthroughs
   - Add tips, common mistakes to avoid, and best practices
   - Use analogies and visual descriptions to explain complex concepts
   - Include a brief summary/recap section at the end
   - Structure with clear ## and ### headers for easy navigation

5. "practice_exercises" (5-7 exercises):
   - Progress from easy to challenging (clearly labeled: Easy/Medium/Hard)
   - Each exercise must have: clear instructions, expected outcome, hints
   - Include model answers or solution approaches for each exercise
   - Mix different exercise types: fill-in, open-ended, scenario-based, creative
   - Estimate time for each exercise (e.g., "~5 min", "~10 min")

6. "homework" (3-4 assignments):
   - Each assignment should take 15-30 minutes
   - Include clear success criteria and evaluation rubric
   - Mix theory review and practical application
   - Provide resources or references where applicable
   - Include a self-check section so the student can evaluate their own work

7. "language": ISO 639-1 code of the conversation language (e.g., "en", "ru", "es", "de").
8. Make the content practical, engaging, and appropriate for the learner's level (infer from chat).
9. Do NOT include any text outside the JSON object.
10. The total output should be substantial — at least 3000-4000 words across all sections."""


class LessonPlanService:
    def __init__(self, db: AsyncSession) -> None:
        self.db = db

    async def generate_lesson_plan(
        self, specialist_id: uuid.UUID, data: LessonPlanGenerateRequest
    ) -> LessonPlan:
        # 1. Verify specialist is a participant in this chat room
        result = await self.db.execute(
            select(ChatRoom).where(
                ChatRoom.id == data.room_id,
                ChatRoom.specialist_id == specialist_id,
            )
        )
        room = result.scalar_one_or_none()
        if not room:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You are not the specialist in this chat room",
            )

        # 2. Fetch chat messages (last 50)
        msg_result = await self.db.execute(
            select(Message)
            .where(Message.room_id == data.room_id)
            .order_by(Message.created_at.asc())
            .limit(50)
        )
        messages = list(msg_result.scalars().all())

        if len(messages) < 2:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Not enough messages in the chat to generate a lesson plan. Please have a conversation first.",
            )

        # 3. Fetch task request context (if provided)
        task_context = ""
        if data.request_id:
            req_result = await self.db.execute(
                select(TaskRequest).where(TaskRequest.id == data.request_id)
            )
            task_req = req_result.scalar_one_or_none()
            if task_req:
                task_context = (
                    f"Task Request Context:\n"
                    f"- Domain: {task_req.domain}\n"
                    f"- Description: {task_req.comment or 'N/A'}\n"
                    f"- Urgency: {task_req.urgency.value}\n"
                )

        # 4. Create lesson plan record with 'generating' status
        lesson_plan = LessonPlan(
            room_id=data.room_id,
            request_id=data.request_id,
            specialist_id=specialist_id,
            status=LessonPlanStatus.GENERATING,
        )
        self.db.add(lesson_plan)
        await self.db.commit()
        await self.db.refresh(lesson_plan)

        # 5. Build the user prompt from chat history
        chat_lines: list[str] = []
        for msg in messages:
            role = "Specialist" if msg.sender_id == room.specialist_id else "Client"
            chat_lines.append(f"[{role}]: {msg.content}")

        user_prompt = ""
        if task_context:
            user_prompt += task_context + "\n"
        if data.additional_context:
            user_prompt += f"Additional context from specialist: {data.additional_context}\n\n"
        user_prompt += "Chat conversation:\n" + "\n".join(chat_lines)

        # 6. Call Claude API
        ai_response = ""
        try:
            ai_response = await self._call_claude_api(SYSTEM_PROMPT, user_prompt)
            logger.info("Claude response (first 200 chars): %s", ai_response[:200])
            parsed = json.loads(ai_response)

            lesson_plan.lesson_content = parsed.get("lesson_content", "")
            lesson_plan.practice_exercises = parsed.get("practice_exercises", "")
            lesson_plan.homework = parsed.get("homework", "")
            lesson_plan.language = parsed.get("language", "en")
            lesson_plan.status = LessonPlanStatus.COMPLETED

        except json.JSONDecodeError as e:
            logger.error("Failed to parse Claude API JSON response: %s", e)
            logger.error("Raw response: %s", ai_response[:500])
            lesson_plan.lesson_content = ai_response
            lesson_plan.status = LessonPlanStatus.FAILED
            lesson_plan.error_message = f"Invalid JSON from AI: {str(e)}"

        except httpx.TimeoutException:
            logger.error("Claude API call timed out")
            lesson_plan.status = LessonPlanStatus.FAILED
            lesson_plan.error_message = "AI service timed out. Please try again."

        except Exception as e:
            logger.error("Claude API call failed: %s", e)
            lesson_plan.status = LessonPlanStatus.FAILED
            lesson_plan.error_message = f"AI service error: {str(e)}"

        await self.db.commit()
        await self.db.refresh(lesson_plan)
        return lesson_plan

    async def get_room_lesson_plans(
        self, room_id: uuid.UUID, user_id: uuid.UUID
    ) -> list[LessonPlan]:
        # Verify user is a participant
        result = await self.db.execute(
            select(ChatRoom).where(
                ChatRoom.id == room_id,
                or_(
                    ChatRoom.client_id == user_id,
                    ChatRoom.specialist_id == user_id,
                ),
            )
        )
        room = result.scalar_one_or_none()
        if not room:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Not a member of this chat",
            )

        result = await self.db.execute(
            select(LessonPlan)
            .where(LessonPlan.room_id == room_id)
            .order_by(LessonPlan.created_at.desc())
        )
        return list(result.scalars().all())

    async def _call_claude_api(
        self, system_prompt: str, user_prompt: str
    ) -> str:
        api_key = settings.ANTHROPIC_API_KEY
        if not api_key:
            raise Exception("ANTHROPIC_API_KEY is not configured")

        async with httpx.AsyncClient() as client:
            response = await client.post(
                "https://api.anthropic.com/v1/messages",
                headers={
                    "x-api-key": api_key,
                    "anthropic-version": "2023-06-01",
                    "content-type": "application/json",
                },
                json={
                    "model": "claude-sonnet-4-20250514",
                    "max_tokens": 8192,
                    "system": system_prompt,
                    "messages": [
                        {"role": "user", "content": user_prompt}
                    ],
                },
                timeout=180.0,
            )

            logger.info("Claude API response status: %d", response.status_code)

            if response.status_code != 200:
                error_text = response.text
                logger.error("Claude API error %d: %s", response.status_code, error_text)
                raise Exception(f"Claude API returned {response.status_code}: {error_text}")

            data = response.json()
            raw_text = data["content"][0]["text"]
            logger.info("Claude API raw response length: %d", len(raw_text))

            # Strip markdown code fences if present
            text = raw_text.strip()
            if text.startswith("```json"):
                text = text[7:]
            elif text.startswith("```"):
                text = text[3:]
            if text.endswith("```"):
                text = text[:-3]
            return text.strip()

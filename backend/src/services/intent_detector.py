"""
Intent Detector - Hybrid Keyword + LLM Approach

Constitutional Compliance:
- Principle VIII (Cost Efficiency): Keyword regex fast path (80% coverage, ~0ms)
- Research decision: Hybrid approach optimizes for accuracy/cost tradeoff
- LLM fallback only for ambiguous messages

Per research.md Decision 5 (Hybrid Intent Detection):
- Keyword patterns: 80% accuracy, <1ms latency, $0 cost
- LLM classification: 95% accuracy, 200-500ms latency, $0.0001/request
- Combined: Best of both worlds
"""
import re
from typing import Optional, Dict, Any
from enum import Enum


class Intent(str, Enum):
    """
    User intent categories for natural language task management.

    Per spec user stories US1-US4:
    - CREATE_TASK: Add new task (US1)
    - LIST_TASKS: Show all tasks (US2)
    - UPDATE_STATUS: Toggle task completion (US3)
    - DELETE_TASK: Remove task (US4)
    - CONVERSATIONAL: Greeting, small talk (no task action)
    - UNKNOWN: Cannot determine intent
    """
    CREATE_TASK = "CREATE_TASK"
    LIST_TASKS = "LIST_TASKS"
    UPDATE_STATUS = "UPDATE_STATUS"
    DELETE_TASK = "DELETE_TASK"
    CONVERSATIONAL = "CONVERSATIONAL"
    UNKNOWN = "UNKNOWN"


class IntentDetector:
    """
    Hybrid intent detection: keyword regex (fast path) + LLM fallback.

    Per research.md, keyword patterns cover ~80% of cases:
    - CREATE_TASK: "add", "create", "make", "new", "remind me"
    - LIST_TASKS: "list", "show", "display", "what are", "all tasks"
    - UPDATE_STATUS: "complete", "mark", "finish", "done", "uncomplete"
    - DELETE_TASK: "delete", "remove", "cancel", "drop"
    - CONVERSATIONAL: "hello", "hi", "thanks", "help", "what can you"

    If no keyword match, fallback to LLM classification (20% of cases).
    """

    # Keyword patterns for fast path detection (case-insensitive)
    PATTERNS = {
        Intent.CREATE_TASK: [
            r'\b(add|create|make|new|schedule|plan|remind me to)\b.*\btask\b',
            r'\b(add|create|make|new|remind me)\b',  # Without "task" keyword
            r'\btask\b.*\b(add|create|make|new)\b',
        ],
        Intent.LIST_TASKS: [
            r'\b(list|show|display|view|get|what are|tell me)\b.*\btasks?\b',
            r'\ball\s+tasks?\b',
            r'\bwhat.*(tasks?|to do|todo)\b',
            r'\b(tasks?|show|list)\b',
        ],
        Intent.UPDATE_STATUS: [
            r'\b(complete|finish|done|mark|toggle|update)\b.*\btask\b',
            r'\bmark\b.*\b(complete|done|finished|pending|incomplete)\b',
            r'\b(un)?complete\b',
        ],
        Intent.DELETE_TASK: [
            r'\b(delete|remove|cancel|drop|erase)\b.*\btask\b',
            r'\b(delete|remove|cancel|drop)\b',
        ],
        Intent.CONVERSATIONAL: [
            r'\b(hello|hi|hey|greetings|good morning|good afternoon|good evening)\b',
            r'\b(thanks|thank you|thx|appreciate)\b',
            r'\b(help|what can you|how do|guide|instructions)\b',
            r'\b(bye|goodbye|see you|later)\b',
        ],
    }

    @classmethod
    def detect_intent_fast_path(cls, message: str) -> Optional[Intent]:
        """
        Fast path: keyword regex matching (~80% coverage, <1ms).

        Args:
            message: User input message

        Returns:
            Intent enum if matched, None if no match (fallback to LLM)
        """
        message_lower = message.lower().strip()

        # Empty message
        if not message_lower:
            return Intent.UNKNOWN

        # Check each intent's patterns
        for intent, patterns in cls.PATTERNS.items():
            for pattern in patterns:
                if re.search(pattern, message_lower):
                    return intent

        # No keyword match - needs LLM fallback
        return None

    @classmethod
    async def detect_intent_llm_fallback(
        cls,
        message: str,
        llm_client: Any
    ) -> Intent:
        """
        LLM fallback: use OpenRouter API for ambiguous messages (~20% of cases).

        Per research.md, LLM classification provides 95% accuracy for edge cases
        that keyword patterns miss (e.g., "Can you help me remember to buy milk?")

        Args:
            message: User input message
            llm_client: OpenAI client configured for OpenRouter

        Returns:
            Intent enum (UNKNOWN if LLM fails to classify)
        """
        # Prompt for intent classification
        system_prompt = """You are an intent classifier for a task management AI assistant.
Classify the user's message into ONE of these categories:
- CREATE_TASK: User wants to add a new task
- LIST_TASKS: User wants to see their tasks
- UPDATE_STATUS: User wants to mark a task as complete/pending
- DELETE_TASK: User wants to delete a task
- CONVERSATIONAL: Greeting, thanks, help request, small talk
- UNKNOWN: Cannot determine intent

Respond with ONLY the category name, nothing else."""

        try:
            response = await llm_client.chat.completions.create(
                model="anthropic/claude-3.5-sonnet",  # From config.AGENT_MODEL
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": message}
                ],
                max_tokens=10,  # Only need category name
                temperature=0.0  # Deterministic classification
            )

            classification = response.choices[0].message.content.strip().upper()

            # Map to Intent enum
            try:
                return Intent[classification]
            except KeyError:
                # Invalid response from LLM
                return Intent.UNKNOWN

        except Exception:
            # LLM failure - default to UNKNOWN
            return Intent.UNKNOWN

    @classmethod
    async def detect_intent(
        cls,
        message: str,
        llm_client: Optional[Any] = None
    ) -> Dict[str, Any]:
        """
        Hybrid intent detection: keyword fast path + optional LLM fallback.

        Per research.md Decision 5:
        1. Try keyword regex (80% coverage, <1ms, $0)
        2. If no match and LLM available, use LLM classification (95% accuracy)
        3. Otherwise return UNKNOWN

        Args:
            message: User input message
            llm_client: Optional OpenAI client for LLM fallback

        Returns:
            Dict with intent, confidence, and method used:
            {
                "intent": Intent enum,
                "confidence": "high" | "medium" | "low",
                "method": "keyword" | "llm" | "unknown"
            }
        """
        # Step 1: Keyword fast path
        intent = cls.detect_intent_fast_path(message)

        if intent is not None:
            # Keyword match found
            return {
                "intent": intent,
                "confidence": "high",
                "method": "keyword"
            }

        # Step 2: LLM fallback (if available)
        if llm_client:
            intent = await cls.detect_intent_llm_fallback(message, llm_client)
            return {
                "intent": intent,
                "confidence": "medium" if intent != Intent.UNKNOWN else "low",
                "method": "llm" if intent != Intent.UNKNOWN else "unknown"
            }

        # Step 3: No match, no LLM available
        return {
            "intent": Intent.UNKNOWN,
            "confidence": "low",
            "method": "unknown"
        }

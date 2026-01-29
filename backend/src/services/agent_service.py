"""
Agent Service - OpenAI Agents SDK Integration

Constitutional Compliance:
- Principle III (Stateless Architecture): Context from database every request
- Principle IV (Tool-Only Mutation): Agent → MCP tools → Database (exclusive path)
- Principle VIII (Agent Behavior Standards): Natural language intent detection

Per spec-5-agent-behavior.md:
- Maps user NL input → MCP tool invocations
- Handles confirmations, clarifications, error handling
- Natural language date/time parsing
- Context-aware responses
"""
from typing import Dict, Any, Optional, List
from uuid import UUID
from datetime import datetime
import dateparser
from openai import AsyncOpenAI

from sqlmodel.ext.asyncio.session import AsyncSession

from ..models.message import MessageRole
from ..services.conversation_service import ConversationService
from ..services.mcp_server import MCPTools, MCPToolError
from ..core.config import settings


class AgentService:
    """
    Agent service for processing natural language task management.

    Uses OpenAI Agents SDK for intent detection and response generation.
    Calls MCP tools for all database mutations (Constitutional Principle IV).
    """

    def __init__(self):
        """Initialize OpenAI-compatible client (OpenRouter)"""
        if not settings.OPENAI_API_KEY:
            raise ValueError("OPENAI_API_KEY not configured")

        # Initialize client with OpenRouter base URL and required headers
        self.client = AsyncOpenAI(
            api_key=settings.OPENAI_API_KEY,
            base_url=settings.OPENROUTER_BASE_URL,
            default_headers={
                "HTTP-Referer": "http://localhost:3000",  # Required by OpenRouter
                "X-Title": "TaskFlow AI Chatbot",  # Optional, helps with OpenRouter rankings
            }
        )
        self.model = settings.AGENT_MODEL
        print(f"[AGENT SERVICE] Initialized with model: {self.model}")

    async def process_message(
        self,
        message: str,
        user_id: UUID,
        session: AsyncSession
    ) -> Dict[str, Any]:
        """
        Process user message and return agent response.

        Per Principle III (Stateless Architecture):
        1. Get or create conversation
        2. Store user message
        3. Reconstruct context from database
        4. Get agent response (with MCP tool calls if needed)
        5. Store agent response
        6. Return response

        Args:
            message: User's natural language input
            user_id: UUID of authenticated user
            session: Async database session

        Returns:
            Dict with agent response and any actions taken
        """
        try:
            print(f"[AGENT SERVICE] Processing message for user_id: {user_id}")
            print(f"[AGENT SERVICE] Message: {message}")

            # Step 1: Get or create conversation
            conversation = await ConversationService.get_or_create_conversation(
                user_id=user_id,
                session=session
            )
            # CRITICAL: Store ID immediately to avoid lazy loading issues
            conversation_id = conversation.id
            print(f"[AGENT SERVICE] Got conversation with ID: {conversation_id}")

            # Step 2: Store user message
            await ConversationService.add_message(
                conversation_id=conversation_id,
                role=MessageRole.USER,
                content=message,
                session=session
            )
            print(f"[AGENT SERVICE] Stored user message")

            # Step 3: Reconstruct context from database
            context_messages = await ConversationService.get_conversation_context(
                conversation_id=conversation_id,
                session=session,
                limit=50
            )
            print(f"[AGENT SERVICE] Retrieved {len(context_messages)} context messages")

            # Step 4: Detect intent and process with agent
            print(f"[AGENT SERVICE] Processing with agent...")
            response_text, actions = await self._process_with_agent(
                message=message,
                context_messages=context_messages,
                user_id=user_id,
                session=session
            )
            print(f"[AGENT SERVICE] Agent response: {response_text[:100]}...")

            # Step 5: Store agent response
            await ConversationService.add_message(
                conversation_id=conversation_id,
                role=MessageRole.AGENT,
                content=response_text,
                session=session
            )
            print(f"[AGENT SERVICE] Stored agent response")

            # Step 6: Return response
            return {
                "response": response_text,
                "actions": actions
            }

        except Exception as e:
            # Error handling per spec-5
            import traceback
            error_details = traceback.format_exc()
            print(f"[AGENT ERROR] {str(e)}")
            print(f"[AGENT ERROR TRACEBACK] {error_details}")
            error_response = f"⚠️ Unable to process your request. Please try again."
            return {
                "response": error_response,
                "actions": [],
                "error": str(e)
            }

    async def _process_with_agent(
        self,
        message: str,
        context_messages: List,
        user_id: UUID,
        session: AsyncSession
    ) -> tuple[str, List[Dict]]:
        """
        Process message with OpenAI agent and detect intent.

        Returns:
            Tuple of (response_text, actions_taken)
        """
        # Build conversation history for OpenAI
        messages = []

        # System prompt following STRICT rules
        system_prompt = """You are TaskFlow AI, a smart task assistant in a full-stack app.

CORE RULES (STRICT):

1. INTENT DETECTION (CRITICAL):
   - SHOW/LIST commands: NEVER create a task. Always list tasks.
   - CREATE: Sentences describing activities/plans: "tomorrow I'm going home", "buy milk"
   - DELETE: "delete task [ID or name]"
   - COMPLETE: "mark task [ID] as done"

2. TASK STRUCTURE:
   - Every task has a unique ID (UUID, show first 8 chars: 8f23a9c1)
   - Show: ID, title, time (09:03 AM format)

3. CREATE TASK response format:
   "✅ Task added!
   ID: 8f23a9c1
   Title: [task title]
   Time: 09:03 AM"

4. SHOW TASKS response format:
   "Here are your tasks:
   1️⃣ (8f23a9c1) task title – 09:03 AM
   2️⃣ (91ab3d2) another task – 08:40 AM"

5. DELETE TASK logic:
   - If ID provided: delete by ID
   - If name provided: find closest match
   - If multiple matches: ask with IDs:
     "I found 2 tasks:
     1) going to home (8f23a9c1)
     2) going to office (91ab3d2)
     Which one should I delete?"

6. UX RULES:
   - Be short, clear, friendly
   - No technical words
   - If unsure, ask ONE short question

GOAL: User talks normally, sees tasks instantly, uses IDs to delete/update."""

        messages.append({"role": "system", "content": system_prompt})

        # Add conversation history
        for msg in context_messages:
            messages.append({
                "role": "user" if msg.role == MessageRole.USER else "assistant",
                "content": msg.content
            })

        # Detect intent from message
        intent = self._detect_intent(message)
        actions = []

        # Route to appropriate MCP tool based on intent
        if intent == "CREATE":
            # Extract task info and call add_task MCP tool
            task_data = self._extract_task_data(message)
            try:
                result = await MCPTools.add_task(
                    title=task_data["title"],
                    user_id=user_id,
                    session=session,
                    description=task_data.get("description"),
                    due_date=task_data.get("due_date"),
                    reminder_time=task_data.get("reminder_time")
                )
                actions.append({"type": "task_created", "data": result})
                # Response with ID and time (as per spec)
                task_id_short = str(result['id'])[:8]  # First 8 chars of UUID
                created_time = self._format_time(result.get('created_at'))
                response_text = f"✅ Task added!\nID: {task_id_short}\nTitle: {result['title']}\nTime: {created_time}"

            except MCPToolError as e:
                response_text = f"⚠️ Hmm, I couldn't create that task. {e.message}"

        elif intent == "READ":
            # Call list_tasks MCP tool
            try:
                result = await MCPTools.list_tasks(
                    user_id=user_id,
                    session=session,
                    completed=False,  # Default to pending tasks
                    limit=10
                )
                actions.append({"type": "tasks_listed", "data": result})

                if result["count"] == 0:
                    response_text = "You have no tasks right now 📝"
                else:
                    # Format: 1️⃣ (8f23a9c1) task title – 09:03 AM
                    task_list = []
                    emoji_numbers = ["1️⃣", "2️⃣", "3️⃣", "4️⃣", "5️⃣", "6️⃣", "7️⃣", "8️⃣", "9️⃣", "🔟"]

                    for idx, task in enumerate(result["tasks"][:10]):
                        emoji = emoji_numbers[idx] if idx < len(emoji_numbers) else f"{idx+1})"
                        task_id_short = str(task['id'])[:8]
                        task_time = self._format_time(task.get('created_at'))
                        task_list.append(f"{emoji} ({task_id_short}) {task['title']} – {task_time}")

                    task_list_str = "\n".join(task_list)
                    response_text = f"Here are your tasks:\n{task_list_str}"

            except MCPToolError as e:
                response_text = f"⚠️ Hmm, I couldn't fetch your tasks right now. {e.message}"

        elif intent == "COMPLETE":
            response_text = "❓ Which task would you like to mark as complete? Please specify the task name."

        elif intent == "DELETE":
            # Extract task ID or name from message
            task_identifier = self._extract_task_identifier(message)

            try:
                # Get user's tasks to search
                tasks_result = await MCPTools.list_tasks(
                    user_id=user_id,
                    session=session,
                    completed=False,
                    limit=50
                )

                if tasks_result["count"] == 0:
                    response_text = "You don't have any tasks to delete 📝"
                else:
                    # Try to find task by ID or name
                    matching_tasks = self._find_task_by_identifier(task_identifier, tasks_result["tasks"])

                    if len(matching_tasks) == 1:
                        # Exact match - delete it
                        task = matching_tasks[0]
                        await MCPTools.delete_task(
                            task_id=task["id"],
                            user_id=user_id,
                            session=session
                        )
                        actions.append({"type": "task_deleted", "data": task})
                        response_text = f"✅ Deleted: {task['title']}"

                    elif len(matching_tasks) > 1:
                        # Multiple matches - ask for clarification with IDs
                        task_list = []
                        for i, t in enumerate(matching_tasks[:5], 1):
                            task_id_short = str(t['id'])[:8]
                            task_list.append(f"{i}) {t['title']} ({task_id_short})")

                        task_list_str = "\n".join(task_list)
                        response_text = f"I found {len(matching_tasks)} tasks:\n{task_list_str}\n\nWhich one should I delete?"

                    else:
                        # No match - show available tasks
                        task_list = []
                        for t in tasks_result["tasks"][:5]:
                            task_id_short = str(t['id'])[:8]
                            task_list.append(f"• {t['title']} ({task_id_short})")

                        task_list_str = "\n".join(task_list)
                        response_text = f"Task not found. Your tasks:\n{task_list_str}"

            except MCPToolError as e:
                response_text = f"⚠️ Couldn't delete task. {e.message}"

        else:
            # Use OpenRouter for general conversation
            try:
                print(f"[AGENT] Sending message to OpenRouter with model: {self.model}")
                completion = await self.client.chat.completions.create(
                    model=self.model,
                    messages=messages
                )
                response_text = completion.choices[0].message.content
                print(f"[AGENT] Received response from OpenRouter: {response_text[:100]}...")

            except Exception as e:
                print(f"[AGENT] OpenRouter API error: {str(e)}")
                import traceback
                print(traceback.format_exc())
                response_text = "⚠️ I'm having trouble processing your request. Please try again."

        return response_text, actions

    def _detect_intent(self, message: str) -> str:
        """
        STRICT intent detection following core rules.

        Priority order:
        1. SHOW/LIST (highest priority - must never create task)
        2. DELETE
        3. COMPLETE
        4. CREATE
        """
        message_lower = message.lower().strip()

        # SHOW/LIST intent - CHECK FIRST (highest priority)
        show_patterns = [
            "show", "list", "display", "view", "see",
            "what tasks", "my tasks", "all tasks", "get tasks"
        ]
        if any(pattern in message_lower for pattern in show_patterns):
            # Additional check: if message contains task-related list words
            if any(word in message_lower for word in ["tasks", "task", "todo", "list"]):
                return "READ"

        # DELETE intent
        delete_patterns = [
            "delete", "remove", "cancel", "get rid"
        ]
        if any(pattern in message_lower for pattern in delete_patterns):
            return "DELETE"

        # COMPLETE intent
        complete_patterns = [
            "mark done", "mark as done", "complete", "completed",
            "finish", "done with", "check off"
        ]
        if any(pattern in message_lower for pattern in complete_patterns):
            return "COMPLETE"

        # CONVERSATIONAL intent - greetings and small talk (MUST check before CREATE)
        conversational_patterns = [
            "hi", "hello", "hey", "hiya", "howdy",
            "good morning", "good afternoon", "good evening",
            "what's up", "whats up", "sup",
            "how are you", "how r u",
            "thanks", "thank you", "thx",
            "bye", "goodbye", "see you",
            "help", "what can you do", "how do you work"
        ]
        if any(pattern in message_lower for pattern in conversational_patterns):
            return "CONVERSATIONAL"

        # CREATE intent - activity/plan keywords
        create_keywords = [
            "tomorrow", "today", "tonight", "meeting", "buy", "call",
            "go to", "going to", "plan", "add task", "create task", "new task",
            "i need to", "i have to", "i should", "remind me"
        ]
        if any(keyword in message_lower for keyword in create_keywords):
            return "CREATE"

        # REMOVED: Short declarative statement fallback that was creating tasks on greetings
        # Old logic: if len(message_lower.split()) <= 8 and not message_lower.endswith('?'):
        #     return "CREATE"

        return "UNKNOWN"

    def _extract_task_data(self, message: str) -> Dict[str, Any]:
        """
        Extract task data from natural language message.

        Handles patterns like:
        - "add task buy milk tomorrow"
        - "tomorrow I'm going to the gym"
        - "buy milk"
        - "call mom next Monday"

        Uses dateparser for natural language date/time parsing per spec-5.
        """
        # Remove command keywords to get task content
        message_clean = message.lower()
        for keyword in ["add task", "create task", "new task", "remind me to", "add a task", "i need to", "i have to", "i should"]:
            message_clean = message_clean.replace(keyword, "")

        message_clean = message_clean.strip()

        # Parse dates from the entire message first
        due_date = None
        date_keywords = ["tomorrow", "next", "monday", "tuesday", "wednesday", "thursday",
                        "friday", "saturday", "sunday", "today", "tonight", "week", "month"]

        # Try to find date indicators in message
        words = message_clean.split()
        date_start_idx = None

        for idx, word in enumerate(words):
            if word in date_keywords:
                date_start_idx = idx
                break

        # If date keyword found, try to parse it
        title_text = message_clean
        if date_start_idx is not None:
            # Everything from date keyword onwards might be the date
            date_str = " ".join(words[date_start_idx:])
            parsed_date = dateparser.parse(date_str, settings={'PREFER_DATES_FROM': 'future'})

            if parsed_date:
                due_date = parsed_date
                # Title is everything before the date
                title_text = " ".join(words[:date_start_idx]).strip()

                # If title starts with "i'm", "i am", "i", clean it up
                for prefix in ["i'm", "i am", "i"]:
                    if title_text.startswith(prefix + " "):
                        # Remove the "I" part and extract the action
                        title_text = title_text[len(prefix):].strip()
                        # Remove "going to" if present
                        title_text = title_text.replace("going to", "").strip()
                        break

        # Clean up common conversational prefixes
        title_text = title_text.replace("going to", "").strip()

        return {
            "title": title_text if title_text else message_clean,
            "description": None,
            "due_date": due_date,
            "reminder_time": None
        }

    def _format_date(self, date_iso: str) -> str:
        """Format ISO date string for display"""
        try:
            dt = datetime.fromisoformat(date_iso.replace('Z', '+00:00'))
            return dt.strftime('%b %d, %Y')
        except:
            return date_iso

    def _format_time(self, datetime_iso: str) -> str:
        """Format ISO datetime string to time like '09:03 AM'"""
        try:
            if not datetime_iso:
                return datetime.now().strftime('%I:%M %p')
            dt = datetime.fromisoformat(datetime_iso.replace('Z', '+00:00'))
            return dt.strftime('%I:%M %p')
        except:
            return datetime.now().strftime('%I:%M %p')

    def _extract_task_identifier(self, message: str) -> str:
        """
        Extract task ID or name from delete command.

        Examples:
        - "delete task 8f23a9c1" → "8f23a9c1"
        - "delete task buy milk" → "buy milk"
        - "remove going to home" → "going to home"
        """
        message_lower = message.lower().strip()

        # Remove delete command keywords
        for keyword in ["delete task", "remove task", "cancel task", "delete the task", "delete my last task", "delete", "remove", "cancel"]:
            if message_lower.startswith(keyword):
                message_lower = message_lower[len(keyword):].strip()
                break

        # Remove common articles
        for word in ["the", "a", "an", "my"]:
            if message_lower.startswith(word + " "):
                message_lower = message_lower[len(word)+1:].strip()

        return message_lower

    def _find_task_by_identifier(self, identifier: str, tasks: List[Dict]) -> List[Dict]:
        """
        Find tasks by ID or name.

        Returns a list of matching tasks:
        - Empty list if no match
        - Single item if one match
        - Multiple items if ambiguous

        Priority:
        1. Exact ID match (first 8 chars)
        2. Exact title match (case-insensitive)
        3. Partial title match (substring)
        """
        if not identifier or len(tasks) == 0:
            return []

        identifier_lower = identifier.lower().strip()
        matching_tasks = []

        # 1. Check for ID match (first 8 characters)
        for task in tasks:
            task_id_short = str(task['id'])[:8].lower()
            if task_id_short == identifier_lower or str(task['id']).lower() == identifier_lower:
                return [task]  # Exact ID match - return immediately

        # 2. Exact title match (case-insensitive)
        for task in tasks:
            if task["title"].lower() == identifier_lower:
                return [task]  # Exact title match

        # 3. Partial title match (substring)
        for task in tasks:
            if identifier_lower in task["title"].lower() or task["title"].lower() in identifier_lower:
                matching_tasks.append(task)

        return matching_tasks

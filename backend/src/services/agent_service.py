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
        self.is_available = False
        self.client = None
        self.model = settings.AGENT_MODEL

        if not settings.OPENAI_API_KEY:
            print("[AGENT SERVICE WARNING] OPENAI_API_KEY not configured - Chat disabled")
            return

        # Initialize client with OpenRouter base URL and required headers
        try:
            self.client = AsyncOpenAI(
                api_key=settings.OPENAI_API_KEY,
                base_url=settings.OPENROUTER_BASE_URL,
                default_headers={
                    "HTTP-Referer": "http://localhost:3000",  # Required by OpenRouter
                    "X-Title": "TaskFlow AI Chatbot",  # Optional, helps with OpenRouter rankings
                }
            )
            self.is_available = True
            print(f"[AGENT SERVICE] Initialized with model: {self.model}")
        except Exception as e:
            print(f"[AGENT SERVICE ERROR] Failed to initialize: {str(e)}")

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
            # Log response length only (avoid emoji encoding issues on Windows)
            print(f"[AGENT SERVICE] Agent response generated ({len(response_text)} chars, {len(actions)} actions)")

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
            # Provide helpful error message without being generic
            error_response = f"I encountered an issue. Try using simple commands like:\n• 'add task [title]'\n• 'show tasks'\n• 'update task [id] to [new title]'\n• 'delete task [id]'\n• 'complete task [id]'"
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
        # Initialize actions list at the very beginning
        actions = []

        try:
            # Build conversation history for OpenAI
            messages = []

            # System prompt - concise and action-focused
            system_prompt = """You are TaskFlow AI, a friendly and efficient task assistant.

PERSONALITY:
- Polite, appreciative, and encouraging
- Use emojis sparingly for warmth (✅ 🎉 📝 💪)
- Celebrate completions, welcome greetings warmly

CORE RULES:
1. ACT IMMEDIATELY - No "let me", "I'll", "I can" - just DO IT
2. BE POLITE & BRIEF - Warm confirmations with appreciation
3. NEVER ask follow-up questions unless data is MISSING
4. INSTANT ACTIONS:
   - "show tasks" → list tasks immediately
   - "add task X" / "X tomorrow" → create task immediately
   - "update task [ID] to [new]" → update immediately
   - "delete task [ID/name]" → delete immediately
   - "complete task [ID/name]" → mark complete immediately

5. RESPONSE STYLE:
   - CREATE: "✅ Perfect! Task created successfully!\n\n📝 **[title]**\nID: 8f23a9c1\nCreated: 09:03 AM\n\nYour dashboard has been updated!"
   - UPDATE: "✅ Perfect! Task updated successfully!\n\n📝 **[new title]**\nID: 8f23a9c1\n\nYour dashboard has been updated!"
   - DELETE: "✅ Done! Task deleted successfully!\n\n🗑️ **[title]**\n\nYour dashboard has been updated!"
   - COMPLETE: "🎉 Awesome! Task completed!\n\n✅ **[title]**\n\nGreat job! One less thing to worry about 💪"
   - LIST: "📋 **Here are your 3 tasks:**\n\n1️⃣ (8f23a9c1) task – 09:03 AM\n\nTo complete a task, just say: 'complete task [ID]'"
   - GREETING: "Hello! 👋 I'm TaskFlow AI, your friendly task assistant. How can I help you today?"
   - THANKS: "You're very welcome! Happy to help you stay organized 😊"

6. ALWAYS acknowledge user actions with appreciation"""

            messages.append({"role": "system", "content": system_prompt})

            # Add conversation history
            for msg in context_messages:
                messages.append({
                    "role": "user" if msg.role == MessageRole.USER else "assistant",
                    "content": msg.content
                })

            # Check if this is first interaction (for greeting handling)
            is_first_message = len(context_messages) <= 1

            # Detect intent from message
            intent = self._detect_intent(message)
            print(f"[AGENT] Detected intent: {intent} for message: {message}")

            # Handle conversational greetings and help messages
            if intent == "CONVERSATIONAL" or intent == "HELP":
                # Check if this is a greeting or thank you
                message_lower = message.lower()

                # Appreciation/Thank you responses
                if any(word in message_lower for word in ["thanks", "thank you", "thx", "appreciate"]):
                    appreciation_responses = [
                        "You're very welcome! Happy to help you stay organized 😊",
                        "My pleasure! Let me know if you need anything else 🙂",
                        "Glad I could help! I'm here whenever you need me ✨",
                        "You're welcome! Feel free to add more tasks anytime 📝",
                    ]
                    import random
                    response_text = random.choice(appreciation_responses)
                    return response_text, actions

                # Greeting responses
                if any(word in message_lower for word in ["hi", "hello", "hey", "good morning", "good afternoon", "good evening"]):
                    greeting_responses = [
                        "Hello! 👋 I'm TaskFlow AI, your friendly task assistant. How can I help you today?",
                        "Hi there! 😊 Ready to help you organize your tasks. What would you like to do?",
                        "Hey! 🙂 I'm here to make task management super easy. Try 'add task' or 'show tasks' to get started!",
                    ]
                    import random
                    response_text = random.choice(greeting_responses)
                    return response_text, actions

                # Help/Capabilities explanation
                response_text = """I'm TaskFlow AI 🤖 — your instant task assistant!

I can help you with:
✅ **Create tasks**: "add task buy groceries" or "I am going to Karachi tomorrow"
📋 **Show tasks**: "show my tasks" or "list all tasks"
✏️ **Update tasks**: "update task [ID] to new title"
✅ **Complete tasks**: "complete task [ID or name]"
❌ **Delete tasks**: "delete task [ID or name]"

Just type naturally — I'll understand and act instantly! 🚀"""
                return response_text, actions

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
                    # CRITICAL: Add action IMMEDIATELY after successful operation
                    actions.append({"type": "task_created", "data": result})
                    print(f"[AGENT] Task created successfully: {result.get('id')}")

                    # Response formatting in try-except to preserve actions if formatting fails
                    try:
                        task_id_short = str(result.get('id', ''))[:8]
                        created_time = self._format_time(result.get('created_at'))
                        task_title = result.get('title', 'Untitled')

                        # Add due date info if available
                        due_info = ""
                        if task_data.get("due_date"):
                            try:
                                due_date_str = self._format_date(task_data["due_date"].isoformat())
                                due_info = f"\nDue: {due_date_str}"
                            except:
                                pass  # Ignore date formatting errors

                        response_text = f"✅ Perfect! Task created successfully!\n\n📝 **{task_title}**\nID: {task_id_short}\nCreated: {created_time}{due_info}\n\nYour dashboard has been updated!"
                    except Exception as format_error:
                        # Fallback response if formatting fails - but actions are preserved!
                        print(f"[AGENT WARNING] Response formatting failed: {format_error}")
                        response_text = f"✅ Perfect! Task '{result.get('title', 'Untitled')}' created successfully!\n\nYour dashboard has been updated!"

                except MCPToolError as e:
                    print(f"[AGENT ERROR] MCP tool error: {e.message}")
                    response_text = f"⚠️ Hmm, I couldn't create that task. {e.message}"
                except Exception as e:
                    print(f"[AGENT ERROR] Unexpected error in CREATE: {str(e)}")
                    response_text = f"⚠️ Sorry, I encountered an error creating the task. Please try again."

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
                        response_text = "You don't have any pending tasks right now! 🎉\n\nYou're all caught up! Type 'add task' to create a new one."
                    else:
                        # Format: 1️⃣ (8f23a9c1) task title – 09:03 AM
                        task_list = []
                        emoji_numbers = ["1️⃣", "2️⃣", "3️⃣", "4️⃣", "5️⃣", "6️⃣", "7️⃣", "8️⃣", "9️⃣", "🔟"]

                        for idx, task in enumerate(result["tasks"][:10]):
                            emoji = emoji_numbers[idx] if idx < len(emoji_numbers) else f"{idx+1})"
                            task_id_short = str(task['id'])[:8]
                            task_time = self._format_time(task.get('created_at'))
                            task_status = "✅" if task.get('is_completed') else "⏳"
                            task_list.append(f"{emoji} ({task_id_short}) {task['title']} – {task_time}")

                        task_list_str = "\n".join(task_list)
                        count_text = f"{result['count']} task" if result['count'] == 1 else f"{result['count']} tasks"
                        response_text = f"📋 **Here are your {count_text}:**\n\n{task_list_str}\n\nTo complete a task, just say: 'complete task [ID]'"

                except MCPToolError as e:
                    response_text = f"⚠️ Hmm, I couldn't fetch your tasks right now. {e.message}"

            elif intent == "UPDATE":
                # Extract task identifier and new title
                task_identifier, new_title = self._extract_update_data(message)

                if not new_title:
                    response_text = "❓ What would you like to update? Try: 'update task [ID] to [new title]'"
                else:
                    try:
                        # Get user's tasks to search
                        tasks_result = await MCPTools.list_tasks(
                            user_id=user_id,
                            session=session,
                            limit=50
                        )

                        if tasks_result["count"] == 0:
                            response_text = "You don't have any tasks to update 📝"
                        else:
                            # Find task by ID or name
                            matching_tasks = self._find_task_by_identifier(task_identifier, tasks_result["tasks"])

                            if len(matching_tasks) == 1:
                                # Update the task
                                task = matching_tasks[0]
                                result = await MCPTools.update_task(
                                    task_id=task["id"],
                                    user_id=user_id,
                                    session=session,
                                    title=new_title
                                )
                                # CRITICAL: Add action IMMEDIATELY
                                actions.append({"type": "task_updated", "data": result})
                                print(f"[AGENT] Task updated successfully: {result.get('id')}")

                                # Safe response formatting
                                try:
                                    task_id_short = str(result.get('id', ''))[:8]
                                    task_title = result.get('title', 'Untitled')
                                    response_text = f"✅ Perfect! Task updated successfully!\n\n📝 **{task_title}**\nID: {task_id_short}\n\nYour dashboard has been updated!"
                                except Exception as format_error:
                                    print(f"[AGENT WARNING] Response formatting failed: {format_error}")
                                    response_text = f"✅ Task updated successfully! Your dashboard has been updated!"

                            elif len(matching_tasks) > 1:
                                # Multiple matches - ask for clarification
                                task_list = []
                                for i, t in enumerate(matching_tasks[:5], 1):
                                    task_id_short = str(t['id'])[:8]
                                    task_list.append(f"{i}) {t['title']} ({task_id_short})")
                                task_list_str = "\n".join(task_list)
                                response_text = f"I found {len(matching_tasks)} tasks:\n{task_list_str}\n\nWhich one should I update?"

                            else:
                                # No match
                                response_text = f"Task '{task_identifier}' not found. Try 'show tasks' to see all."

                    except MCPToolError as e:
                        response_text = f"⚠️ Couldn't update task. {e.message}"

            elif intent == "COMPLETE":
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
                        response_text = "You don't have any pending tasks to complete 📝"
                    else:
                        # Try to find task by ID or name
                        matching_tasks = self._find_task_by_identifier(task_identifier, tasks_result["tasks"])

                        if len(matching_tasks) == 1:
                            # Exact match - complete it
                            task = matching_tasks[0]
                            result = await MCPTools.complete_task(
                                task_id=task["id"],
                                user_id=user_id,
                                session=session
                            )
                            # CRITICAL: Add action IMMEDIATELY
                            actions.append({"type": "task_completed", "data": result})
                            print(f"[AGENT] Task completed successfully: {result.get('id')}")

                            # Safe response formatting
                            try:
                                task_title = task.get('title', 'Task')
                                response_text = f"🎉 Awesome! Task completed!\n\n✅ **{task_title}**\n\nGreat job! One less thing to worry about 💪"
                            except Exception as format_error:
                                print(f"[AGENT WARNING] Response formatting failed: {format_error}")
                                response_text = f"🎉 Awesome! Task completed! Great job! 💪"

                        elif len(matching_tasks) > 1:
                            # Multiple matches - ask for clarification with IDs
                            task_list = []
                            for i, t in enumerate(matching_tasks[:5], 1):
                                task_id_short = str(t['id'])[:8]
                                task_list.append(f"{i}) {t['title']} ({task_id_short})")

                            task_list_str = "\n".join(task_list)
                            response_text = f"I found {len(matching_tasks)} tasks:\n{task_list_str}\n\nWhich one should I mark as complete?"

                        else:
                            # No match - show available tasks
                            task_list = []
                            for t in tasks_result["tasks"][:5]:
                                task_id_short = str(t['id'])[:8]
                                task_list.append(f"• {t['title']} ({task_id_short})")

                            task_list_str = "\n".join(task_list)
                            response_text = f"Task not found. Your pending tasks:\n{task_list_str}"

                except MCPToolError as e:
                    response_text = f"⚠️ Couldn't complete task. {e.message}"

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
                            # CRITICAL: Add action IMMEDIATELY
                            actions.append({"type": "task_deleted", "data": task})
                            print(f"[AGENT] Task deleted successfully: {task.get('id')}")

                            # Safe response formatting
                            try:
                                task_title = task.get('title', 'Task')
                                response_text = f"✅ Done! Task deleted successfully!\n\n🗑️ **{task_title}**\n\nYour dashboard has been updated!"
                            except Exception as format_error:
                                print(f"[AGENT WARNING] Response formatting failed: {format_error}")
                                response_text = f"✅ Done! Task deleted successfully! Your dashboard has been updated!"

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
                # UNKNOWN intent - provide helpful guidance instead of calling expensive AI API
                # This saves costs and provides faster, more reliable responses
                response_text = """I'm not sure what you want to do. Try these commands:

📝 **Create tasks:**
• "add task buy groceries"
• "meeting tomorrow at 3pm"

📋 **View tasks:**
• "show tasks"
• "list my tasks"

✏️ **Update tasks:**
• "update task [ID] to [new title]"

✅ **Complete tasks:**
• "complete task [ID or name]"

❌ **Delete tasks:**
• "delete task [ID or name]"

Type 'help' for more info!"""

            return response_text, actions

        except Exception as e:
            # CRITICAL: If any error occurs during processing, preserve actions!
            # This ensures dashboard refresh works even if response formatting fails
            print(f"[AGENT ERROR] Unexpected error in _process_with_agent: {str(e)}")
            import traceback
            traceback.print_exc()

            # Return error message but PRESERVE actions for dashboard refresh
            error_response = "⚠️ I encountered an issue, but your action may have been completed. Check your dashboard!"
            return error_response, actions  # ← Actions are preserved!

    def _detect_intent(self, message: str) -> str:
        """
        ROBUST intent detection with natural language support.

        Priority order:
        1. HELP (introduction and guidance)
        2. READ/SHOW (highest priority - must never create task)
        3. DELETE (before COMPLETE to avoid "delete done" confusion)
        4. COMPLETE
        5. UPDATE
        6. CONVERSATIONAL (greetings, thanks)
        7. CREATE (last, as it's most permissive)
        """
        message_lower = message.lower().strip()
        print(f"[INTENT DETECTION] Processing: '{message_lower}'")

        # HELP intent - CHECK FIRST (for assistance requests)
        # Use word-boundary check to avoid matching "how" inside "show", etc.
        import re
        help_patterns = [
            r"\bhelp\b", r"\bhow\b", r"what can you do", r"what do you do",
            r"how does this work", r"how to", r"\bguide\b", r"\binstructions\b",
            r"what is this", r"\bexplain\b", r"\bcapabilities\b", r"what are you"
        ]
        if any(re.search(pattern, message_lower) for pattern in help_patterns):
            print(f"[INTENT] HELP detected")
            return "HELP"

        # READ/SHOW intent - CHECK SECOND (highest priority for CRUD - must never create task)
        # More flexible: handle "show task", "show all task" (missing 's'), "list task", etc.
        show_patterns = [
            "show", "list", "display", "view", "see", "get",
            "what task", "my task", "all task", "your task"
        ]
        has_show_keyword = any(pattern in message_lower for pattern in show_patterns)
        has_task_keyword = any(word in message_lower for word in ["tasks", "task", "todo", "to-do", "to do"])

        if has_show_keyword and has_task_keyword:
            print(f"[INTENT] READ detected")
            return "READ"

        # DELETE intent - Check BEFORE complete to handle "delete done task" properly
        delete_patterns = [
            "delete", "remove", "cancel", "get rid", "erase", "clear"
        ]
        if any(pattern in message_lower for pattern in delete_patterns):
            # Must contain task reference to be delete command (avoid false positives)
            if any(word in message_lower for word in ["task", "todo", "to-do", "to do"]) or len(message_lower.split()) >= 2:
                print(f"[INTENT] DELETE detected")
                return "DELETE"

        # COMPLETE intent
        complete_patterns = [
            "mark done", "mark as done", "mark complete", "mark as complete",
            "complete task", "complete", "completed", "finish task", "finish",
            "done with", "done", "check off", "mark task done", "set as complete",
            "mark it done", "mark as finished", "finished"
        ]
        has_complete_keyword = any(pattern in message_lower for pattern in complete_patterns)

        if has_complete_keyword:
            # Must contain "task" reference or be short command
            if any(word in message_lower for word in ["task", "todo", "to-do", "to do"]) or len(message_lower.split()) <= 5:
                print(f"[INTENT] COMPLETE detected")
                return "COMPLETE"

        # UPDATE intent
        update_patterns = [
            "update", "change", "modify", "edit", "rename", "alter"
        ]
        if any(pattern in message_lower for pattern in update_patterns):
            # Must contain "task" or "to" separator to be update command
            if any(word in message_lower for word in ["task", "to "]):
                print(f"[INTENT] UPDATE detected")
                return "UPDATE"

        # CONVERSATIONAL intent - greetings and small talk (MUST check before CREATE)
        conversational_patterns = [
            # Greetings
            "hi", "hello", "hey", "hiya", "howdy", "yo",
            "good morning", "good afternoon", "good evening", "good day",
            "what's up", "whats up", "sup", "wassup",
            # Questions about assistant
            "how are you", "how r u", "who are you", "what are you",
            # Appreciation
            "thanks", "thank you", "thx", "ty", "appreciate", "appreciated",
            "you are good", "you're good", "nice", "great job",
            "awesome", "excellent", "well done", "perfect",
            # Farewells
            "bye", "goodbye", "see you", "later", "cya", "take care"
        ]

        # Check for conversational patterns, but exclude if combined with task keywords
        has_conversational = any(pattern in message_lower for pattern in conversational_patterns)
        has_task_action = any(word in message_lower for word in ["add", "create", "task", "todo", "delete", "update", "complete"])

        if has_conversational and not has_task_action:
            print(f"[INTENT] CONVERSATIONAL detected")
            return "CONVERSATIONAL"

        # CREATE intent - activity/plan keywords or explicit task creation
        # More robust: handle natural language like "I am going to Karachi"
        create_keywords = [
            # Explicit task creation
            "add task", "create task", "new task", "make task",
            "remind me", "remember to",
            # Time-based (future activities)
            "tomorrow", "today", "tonight", "next week", "next month",
            "monday", "tuesday", "wednesday", "thursday", "friday", "saturday", "sunday",
            # Common activities
            "meeting", "buy", "call", "email", "send", "write", "read",
            "go to", "going to", "plan to", "need to", "have to", "should",
            "i'm going", "i am going", "i'll", "i will",
            "schedule", "appointment", "event"
        ]

        if any(keyword in message_lower for keyword in create_keywords):
            print(f"[INTENT] CREATE detected")
            return "CREATE"

        # Fallback: If message is a short statement (not a question) and not clearly conversational
        # This handles natural language like "going to the gym" without explicit keywords
        words = message_lower.split()
        if len(words) >= 2 and len(words) <= 15 and not message_lower.endswith('?') and not has_conversational:
            # Additional heuristic: contains verb-like words suggesting action
            action_words = ["go", "get", "make", "do", "take", "bring", "send", "write", "read", "watch", "play"]
            if any(word in message_lower for word in action_words):
                print(f"[INTENT] CREATE detected (action-based fallback)")
                return "CREATE"

        print(f"[INTENT] UNKNOWN")
        return "UNKNOWN"

    def _extract_task_data(self, message: str) -> Dict[str, Any]:
        """
        Extract task data from natural language message.

        Handles patterns like:
        - "add task buy milk tomorrow"
        - "create task I am going to Karachi"
        - "tomorrow I'm going to the gym"
        - "buy milk"
        - "call mom next Monday"
        - "I am going to Karachi" → "going to Karachi"

        Uses dateparser for natural language date/time parsing per spec-5.
        """
        print(f"[EXTRACT] Raw message: '{message}'")

        # Remove command keywords to get task content (case-insensitive)
        message_clean = message.lower()
        command_keywords = [
            "add task", "add a task", "create task", "create a task", "new task", "make task",
            "remind me to", "remind me", "remember to", "remember",
            "i need to", "i have to", "i should", "i must",
            "add", "create", "make"
        ]

        # Remove command keywords (only first occurrence)
        for keyword in command_keywords:
            if message_clean.startswith(keyword):
                message_clean = message_clean[len(keyword):].strip()
                break

        print(f"[EXTRACT] After removing commands: '{message_clean}'")

        # Parse dates from the entire message first
        due_date = None
        date_keywords = [
            "tomorrow", "today", "tonight",
            "next week", "next month", "next",
            "monday", "tuesday", "wednesday", "thursday",
            "friday", "saturday", "sunday",
            "week", "month", "year"
        ]

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
            try:
                parsed_date = dateparser.parse(date_str, settings={'PREFER_DATES_FROM': 'future'})
                if parsed_date:
                    due_date = parsed_date
                    # Title is everything before the date
                    title_text = " ".join(words[:date_start_idx]).strip()
                    print(f"[EXTRACT] Parsed date: {parsed_date}, Title: '{title_text}'")
            except Exception as e:
                print(f"[EXTRACT] Date parsing failed: {e}")

        # Clean up common conversational prefixes from the title
        # Handle "I am going to Karachi" → "going to Karachi"
        # Handle "I'm going to the gym" → "going to the gym"
        conversational_prefixes = [
            "i'm ", "i am ", "im ", "i ",  # First person
            "we're ", "we are ", "were ", "we ",  # Plural
        ]

        for prefix in conversational_prefixes:
            if title_text.startswith(prefix):
                title_text = title_text[len(prefix):].strip()
                print(f"[EXTRACT] Removed prefix '{prefix}': '{title_text}'")
                break

        # Normalize whitespace
        title_text = " ".join(title_text.split())

        # Ensure we have a valid title (fallback to original message if needed)
        if not title_text or len(title_text.strip()) == 0:
            title_text = message_clean if message_clean else message

        print(f"[EXTRACT] Final title: '{title_text}'")

        return {
            "title": title_text,
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

    def _extract_update_data(self, message: str) -> tuple[str, str]:
        """
        Extract task identifier and new title from update command.

        Examples:
        - "update task 8f23a9c1 to buy groceries" → ("8f23a9c1", "buy groceries")
        - "change buy milk to buy almond milk" → ("buy milk", "buy almond milk")
        - "update my gym task to yoga session" → ("gym", "yoga session")

        Returns:
            Tuple of (task_identifier, new_title)
        """
        message_lower = message.lower().strip()

        # Remove update command keywords
        for keyword in ["update task", "change task", "modify task", "edit task", "rename task",
                       "update", "change", "modify", "edit", "rename"]:
            if message_lower.startswith(keyword):
                message_lower = message_lower[len(keyword):].strip()
                break

        # Look for "to" separator
        if " to " in message_lower:
            parts = message_lower.split(" to ", 1)
            task_identifier = parts[0].strip()
            new_title = parts[1].strip() if len(parts) > 1 else ""

            # Clean up task identifier
            for word in ["the", "a", "an", "my"]:
                if task_identifier.startswith(word + " "):
                    task_identifier = task_identifier[len(word)+1:].strip()

            return (task_identifier, new_title)

        # If no "to" separator, return empty new_title
        return (message_lower, "")

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

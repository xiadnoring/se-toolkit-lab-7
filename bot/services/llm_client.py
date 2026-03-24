"""LLM client with tool calling support for intent routing."""

import json
import sys
from typing import Any

import httpx


class LLMClient:
    """Client for LLM API with tool calling support.

    This client sends messages + tool definitions to the LLM and handles
    tool call responses in a loop until the LLM produces a final answer.
    """

    def __init__(self, api_key: str, base_url: str, model: str) -> None:
        """Initialize the LLM client.

        Args:
            api_key: API key for authentication
            base_url: Base URL of the LLM API (e.g., http://localhost:42005/v1)
            model: Model name to use (e.g., coder-model)
        """
        self.api_key = api_key
        self.base_url = base_url.rstrip("/")
        self.model = model
        self._client = httpx.Client(
            base_url=self.base_url,
            headers={
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json",
            },
            timeout=60.0,
        )

    def chat(
        self,
        messages: list[dict[str, Any]],
        tools: list[dict[str, Any]] | None = None,
    ) -> tuple[str, list[dict[str, Any]]]:
        """Send a chat message to the LLM.

        Args:
            messages: List of conversation messages with role and content
            tools: Optional list of tool definitions

        Returns:
            Tuple of (response_text, list_of_tool_calls)
        """
        payload: dict[str, Any] = {
            "model": self.model,
            "messages": messages,
        }

        if tools:
            payload["tools"] = tools
            payload["tool_choice"] = "auto"

        response = self._client.post("/chat/completions", json=payload)
        response.raise_for_status()
        data = response.json()

        choice = data["choices"][0]["message"]
        content = choice.get("content", "")
        tool_calls = choice.get("tool_calls", [])

        return content, tool_calls

    def format_tool_result(
        self,
        tool_call_id: str,
        tool_name: str,
        result: Any,
    ) -> dict[str, Any]:
        """Format a tool result for sending back to the LLM.

        Args:
            tool_call_id: The ID of the tool call from the LLM
            tool_name: The name of the tool that was called
            result: The result data (will be JSON serialized)

        Returns:
            Message dict ready to append to conversation
        """
        if isinstance(result, (dict, list)):
            content = json.dumps(result, default=str)
        else:
            content = str(result)

        return {
            "role": "tool",
            "content": content,
            "tool_call_id": tool_call_id,
            "name": tool_name,
        }


def get_tool_definitions() -> list[dict[str, Any]]:
    """Return all 9 backend endpoint tool definitions.

    These schemas tell the LLM what tools are available and how to call them.
    The LLM uses these to decide which tool to call for each user query.
    """
    return [
        {
            "type": "function",
            "function": {
                "name": "get_items",
                "description": "Get list of all labs and tasks. Use this to discover what labs are available or to find lab IDs.",
                "parameters": {
                    "type": "object",
                    "properties": {},
                    "required": [],
                },
            },
        },
        {
            "type": "function",
            "function": {
                "name": "get_learners",
                "description": "Get list of all enrolled learners and their groups. Use this to answer questions about student enrollment, group membership, or learner details.",
                "parameters": {
                    "type": "object",
                    "properties": {},
                    "required": [],
                },
            },
        },
        {
            "type": "function",
            "function": {
                "name": "get_scores",
                "description": "Get score distribution for a specific lab (4 buckets: 0-25, 26-50, 51-75, 76-100). Use this to see how students performed in a lab.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "lab": {
                            "type": "string",
                            "description": "Lab identifier, e.g., 'lab-01', 'lab-04'",
                        },
                    },
                    "required": ["lab"],
                },
            },
        },
        {
            "type": "function",
            "function": {
                "name": "get_pass_rates",
                "description": "Get per-task average scores and attempt counts for a lab. Use this to see detailed pass rates and performance metrics for each task within a lab.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "lab": {
                            "type": "string",
                            "description": "Lab identifier, e.g., 'lab-01', 'lab-04'",
                        },
                    },
                    "required": ["lab"],
                },
            },
        },
        {
            "type": "function",
            "function": {
                "name": "get_timeline",
                "description": "Get submission timeline showing submissions per day for a lab. Use this to see when students submitted their work.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "lab": {
                            "type": "string",
                            "description": "Lab identifier, e.g., 'lab-01', 'lab-04'",
                        },
                    },
                    "required": ["lab"],
                },
            },
        },
        {
            "type": "function",
            "function": {
                "name": "get_groups",
                "description": "Get per-group scores and student counts for a lab. Use this to compare group performance or find which group is doing best/worst.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "lab": {
                            "type": "string",
                            "description": "Lab identifier, e.g., 'lab-01', 'lab-04'",
                        },
                    },
                    "required": ["lab"],
                },
            },
        },
        {
            "type": "function",
            "function": {
                "name": "get_top_learners",
                "description": "Get top N learners by score for a lab. Use this to find the best performing students.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "lab": {
                            "type": "string",
                            "description": "Lab identifier, e.g., 'lab-01', 'lab-04'",
                        },
                        "limit": {
                            "type": "integer",
                            "description": "Number of top learners to return (default: 10)",
                        },
                    },
                    "required": ["lab"],
                },
            },
        },
        {
            "type": "function",
            "function": {
                "name": "get_completion_rate",
                "description": "Get completion rate percentage for a lab. Use this to see what percentage of students completed the lab.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "lab": {
                            "type": "string",
                            "description": "Lab identifier, e.g., 'lab-01', 'lab-04'",
                        },
                    },
                    "required": ["lab"],
                },
            },
        },
        {
            "type": "function",
            "function": {
                "name": "trigger_sync",
                "description": "Trigger a data sync from the autochecker. Use this to refresh the latest submission data.",
                "parameters": {
                    "type": "object",
                    "properties": {},
                    "required": [],
                },
            },
        },
    ]


class IntentRouter:
    """Routes user messages to backend tools via LLM.

    The router maintains a conversation loop:
    1. Send user message + tool definitions to LLM
    2. LLM returns tool calls (or final answer)
    3. Execute tool calls, get results
    4. Feed results back to LLM
    5. Repeat until LLM produces final answer
    """

    def __init__(self, llm_client: LLMClient, api_client: Any) -> None:
        """Initialize the intent router.

        Args:
            llm_client: The LLM client for chat completions
            api_client: The LMS API client for executing tool calls
        """
        self.llm = llm_client
        self.api = api_client
        self.tools = get_tool_definitions()

        # Map tool names to API methods
        self._tool_handlers: dict[str, callable] = {
            "get_items": self.api.get_labs_raw,
            "get_learners": self.api.get_learners,
            "get_scores": self.api.get_scores_distribution,
            "get_pass_rates": self.api.get_pass_rates,
            "get_timeline": self.api.get_timeline,
            "get_groups": self.api.get_groups,
            "get_top_learners": self.api.get_top_learners,
            "get_completion_rate": self.api.get_completion_rate,
            "trigger_sync": self.api.trigger_sync,
        }

    def _debug(self, message: str) -> None:
        """Print debug message to stderr (visible in --test mode)."""
        print(f"[tool] {message}", file=sys.stderr)

    async def route(self, user_message: str) -> str:
        """Route a user message through the LLM tool calling loop.

        Args:
            user_message: The user's natural language query

        Returns:
            The final response text
        """
        # System prompt that encourages tool use
        system_prompt = {
            "role": "system",
            "content": (
                "You are a helpful assistant for an LMS (Learning Management System). "
                "You have access to backend API tools that provide real data about labs, students, scores, and analytics. "
                "ALWAYS use the available tools to get actual data before answering. "
                "Never make up numbers or pretend to know data you haven't fetched. "
                "When the user asks about labs, scores, students, groups, or performance - call the appropriate tool first. "
                "After receiving tool results, analyze the data and provide a clear, specific answer with actual numbers and names. "
                "If you don't have enough information to call a tool, ask the user for clarification. "
                "For greetings or simple questions, you can respond directly without tools."
            ),
        }

        messages: list[dict[str, Any]] = [
            system_prompt,
            {"role": "user", "content": user_message},
        ]

        max_iterations = 5
        iteration = 0

        while iteration < max_iterations:
            iteration += 1

            try:
                content, tool_calls = self.llm.chat(messages, self.tools)
            except Exception as e:
                self._debug(f"LLM error: {e}")
                return f"LLM error: {e}"

            # If no tool calls, LLM has a final answer
            if not tool_calls:
                return (
                    content
                    or "I didn't understand. Here's what I can help with: ask about labs, scores, students, groups, or pass rates."
                )

            # Execute each tool call
            tool_results = []
            for tool_call in tool_calls:
                function = tool_call["function"]
                tool_name = function["name"]
                tool_call_id = tool_call["id"]

                try:
                    args = json.loads(function.get("arguments", "{}"))
                except json.JSONDecodeError:
                    args = {}

                self._debug(f"LLM called: {tool_name}({args})")

                # Call the appropriate API method
                handler = self._tool_handlers.get(tool_name)
                if handler:
                    try:
                        # Handle async methods
                        import asyncio

                        if asyncio.iscoroutinefunction(handler):
                            result = await handler(**args)
                        else:
                            result = handler(**args)
                        self._debug(f"Result: {str(result)[:100]}...")
                    except Exception as e:
                        result = {"error": str(e)}
                        self._debug(f"Tool error: {e}")
                else:
                    result = {"error": f"Unknown tool: {tool_name}"}

                # Format result for LLM
                tool_result_msg = self.llm.format_tool_result(
                    tool_call_id, tool_name, result
                )
                tool_results.append(tool_result_msg)

            # Add tool calls and results to conversation
            messages.append({"role": "assistant", "tool_calls": tool_calls})
            messages.extend(tool_results)

            self._debug(
                f"[summary] Feeding {len(tool_results)} tool result(s) back to LLM"
            )

        # If we exit the loop without a final answer
        return "I encountered an issue processing your request. Please try rephrasing your question."

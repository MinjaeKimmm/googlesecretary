from typing import List, Dict
import datetime
from typing import List, Dict
from zoneinfo import ZoneInfo

from langchain.agents import AgentExecutor
from langchain_openai import ChatOpenAI
from langchain.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain.tools.render import format_tool_to_openai_function
from langchain.agents.format_scratchpad import format_to_openai_function_messages
from langchain.agents.output_parsers import OpenAIFunctionsAgentOutputParser
from langchain.agents import create_openai_functions_agent

from src.config.settings import get_settings
from src.tools.calendar import (
    TimeDeltaTool,
    CurrentTimeTool,
    SpecificTimeTool,
    GetCalendarEventsTool,
    CreateCalendarEventTool,
    DeleteCalendarEventTool
)
from src.utils.timezone import to_utc, to_local, format_local_time, DEFAULT_TIMEZONE

class CalendarAgent:
    def __init__(self):
        self.llm = ChatOpenAI(
            temperature=0,
            model=get_settings().openai_model,
            api_key=get_settings().openai_api_key
        )
        
        self.tools = [
            TimeDeltaTool(),
            CurrentTimeTool(),
            SpecificTimeTool(),
            GetCalendarEventsTool(),
            CreateCalendarEventTool(),
            DeleteCalendarEventTool(),
        ]
        
        self.prompt = ChatPromptTemplate.from_messages([
            (
                "system",
                """You are a funny and friendly Google Calendar assistant.  NEVER print event ids or links to the user. Communicate naturally like talking in person - no bullet points or formal formatting. Be helpful and occasionally witty while focusing on what, when, where, and who. Respond conversationally as if chatting with a friend who's helping manage their schedule. NEVER use emojis. All times are in Asia/Seoul (KST/UTC+9)."""
            ),
            ("user", "{input}"),
            MessagesPlaceholder(variable_name="agent_scratchpad"),
        ])
        
        self.functions = [format_tool_to_openai_function(t) for t in self.tools]
        self.llm_with_tools = self.llm.bind(functions=self.functions)
        
        self.agent = create_openai_functions_agent(
            llm=self.llm_with_tools,
            prompt=self.prompt,
            tools=self.tools
        )
        
        self.agent_executor = AgentExecutor(
            agent=self.agent,
            tools=self.tools,
            verbose=True,
            handle_parsing_errors=True
        )

    def _format_input(self, user_email: str, user_message: str, calendar_id: str) -> str:
        return f"""
calendar_id: {calendar_id}
user_email: {user_email}
current datetime: {datetime.datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%S.%fZ")}
current weekday: {datetime.datetime.utcnow().strftime("%A")}
user input: {user_message}
"""

    async def process_message(self, user_email: str, user_message: str, calendar_id: str) -> str:
        """Process a user message using the calendar agent."""
        try:
            input_text = self._format_input(user_email, user_message, calendar_id)
            print("\n====== Starting Agent with input ======= ")
            print(input_text)
            print("\n")
            
            result = await self.agent_executor.ainvoke(
                {"input": input_text},
                return_intermediate_steps=True,  # Get detailed steps
                include_run_info=True  # Include run information
            )
            
            # Extract the final answer
            answer = result.get("output", "I couldn't process your request at this time.")
            return answer
            
        except Exception as e:
            print(f"Error in calendar agent: {str(e)}")
            return "I apologize, but I encountered an error while processing your request."

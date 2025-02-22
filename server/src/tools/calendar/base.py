from typing import Type, Optional
from pydantic import BaseModel
from langchain.tools import BaseTool

class CalendarBaseTool(BaseTool):
    """Base class for all calendar tools."""
    name: str
    description: str
    args_schema: Optional[Type[BaseModel]] = None
    
    def _run(self, *args, **kwargs):
        """Sync run not implemented for calendar tools."""
        raise NotImplementedError("Calendar tools only support async operations")

    async def _arun(self, *args, **kwargs):
        """Default async implementation that delegates to the tool's async run method."""
        return await self._run(*args, **kwargs)

    @property
    def args_schema(self) -> Type[BaseModel]:
        """Return the schema for the tool's arguments."""
        raise NotImplementedError("Each tool must define its argument schema")

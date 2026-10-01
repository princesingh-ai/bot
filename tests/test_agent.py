import unittest
import asyncio
from unittest.mock import patch, AsyncMock, MagicMock
from app.agent.agent import run_agent

class TestAgent(unittest.IsolatedAsyncioTestCase):

    async def test_direct_response(self):
        # Setup mock MCP client
        mock_client = MagicMock()
        mock_client.list_tools = AsyncMock(return_value=[])
        
        # Setup mock Chat response
        with patch('app.agent.agent.chat') as mock_chat:
            mock_response = MagicMock()
            mock_message = MagicMock(content="Hello", tool_calls=None, reasoning_content=None)
            mock_response.choices = [MagicMock(message=mock_message)]
            mock_chat.return_value = mock_response
            
            res = await run_agent("hello", mock_client)
            self.assertEqual(res, "Hello")

if __name__ == '__main__':
    unittest.main()

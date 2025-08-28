"""
Simple Agent Controller for Flight Review
"""

import json
import logging
from typing import Dict, Any, Optional

from flight_agent import get_flight_agent

logger = logging.getLogger(__name__)

class AgentResponse:
    """Agent response wrapper"""
    
    def __init__(self, success: bool, response: str, error: str = None, data: Dict[str, Any] = None):
        self.success = success
        self.response = response
        self.error = error
        self.data = data or {}
    
    def to_dict(self):
        """Convert to dictionary"""
        return {
            "success": self.success,
            "response": self.response,
            "error": self.error,
            "data": self.data
        }

class SimpleAgentController:
    """Simple Agent Controller"""
    
    def __init__(self):
        self.flight_agent = get_flight_agent()
        logger.info("Simple Agent Controller initialized")
    
    def is_available(self):
        """Check if agent is available"""
        return self.flight_agent.initialized

    def process_query(self, query: str, flight_data: Dict[str, Any] = None, model: str = None) -> AgentResponse:
        """Process user query"""
        try:
            result = self.flight_agent.analyze_with_function_calling(query, flight_data or {}, model or "gpt-4o-mini")

            if result["success"]:
                return AgentResponse(
                    success=True,
                    response=result["analysis"],
                    data=result.get("metadata", {})
                )
            else:
                return AgentResponse(
                    success=False,
                    response=result.get("analysis", "分析失败"),
                    error=result.get("error")
                )
                
        except Exception as e:
            logger.error(f"Error processing query: {e}")
            return AgentResponse(
                success=False,
                response="处理请求时出现错误",
                error=str(e)
            )
    
    def quick_analysis(self, analysis_type: str, flight_data: Dict[str, Any] = None) -> AgentResponse:
        """Quick analysis"""
        try:
            result = self.flight_agent.quick_analysis(analysis_type, flight_data)
            
            if result["success"]:
                return AgentResponse(
                    success=True,
                    response=result["response"],
                    data=result.get("usage", {})
                )
            else:
                return AgentResponse(
                    success=False,
                    response=result["response"],
                    error=result.get("error")
                )
                
        except Exception as e:
            logger.error(f"Error in quick analysis: {e}")
            return AgentResponse(
                success=False,
                response="快速分析时出现错误",
                error=str(e)
            )

# Global controller instance
_controller = None

def get_agent_controller():
    """Get global agent controller instance"""
    global _controller
    if _controller is None:
        _controller = SimpleAgentController()
    return _controller

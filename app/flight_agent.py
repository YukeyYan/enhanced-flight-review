#!/usr/bin/env python3
"""
Flight Analysis Agent with Function Calling
飞行分析Agent - 支持函数调用
"""

import json
import logging
import time
from typing import Dict, Any, List, Optional
from openai import OpenAI
from llm_config import get_llm_config
from ulog_tools import ULogDataTools, ULOG_TOOLS

logger = logging.getLogger(__name__)

class FlightAnalysisAgent:
    """飞行分析Agent - 支持OpenAI函数调用"""
    
    def __init__(self):
        self.config = get_llm_config()
        self.client = None
        self.initialized = False
        self.tools = ULOG_TOOLS
        self._init_client()
        
    def _init_client(self):
        """初始化OpenAI客户端"""
        try:
            api_key = self.config.get_api_key()
            if not api_key or api_key == "your_openai_api_key_here":
                logger.error("OpenAI API key not configured")
                return
                
            self.client = OpenAI(api_key=api_key)
            self.initialized = True
            logger.info("Flight Analysis Agent initialized successfully")
            
        except Exception as e:
            logger.error(f"Failed to initialize OpenAI client: {e}")
            self.initialized = False
    
    def analyze_with_function_calling(self, question: str, flight_data: Dict[str, Any], 
                                    model: str = "gpt-4o-mini") -> Dict[str, Any]:
        """
        使用函数调用进行飞行分析
        
        Args:
            question: 用户问题
            flight_data: 飞行数据
            model: 使用的模型
            
        Returns:
            分析结果
        """
        if not self.initialized:
            return {
                "success": False,
                "error": "Agent未正确初始化",
                "analysis": "OpenAI客户端未正确初始化，请检查API密钥配置。"
            }
        
        try:
            # 创建数据访问工具
            ulog_tools = ULogDataTools(flight_data)
            
            # 系统提示词
            system_prompt = """你是一名专业的无人机飞行分析专家，具有深厚的航空工程、飞行控制系统和PX4固件知识。

你的专业领域包括：
- 无人机飞行控制系统分析
- PX4/ArduPilot固件诊断  
- 飞行数据解读和异常检测
- 电池管理系统分析
- GPS和导航系统评估
- 振动和机械系统诊断
- 飞行安全评估

你可以使用以下工具函数来获取详细的飞行数据：
- get_battery_status_data: 获取电池状态数据
- get_power_system_data: 获取电力系统数据
- get_flight_performance_data: 获取飞行性能数据
- get_gps_navigation_data: 获取GPS导航数据

请基于用户问题，主动调用相关的工具函数获取数据，然后进行专业分析。回答要专业但易懂，使用中文回复。"""

            # 构建消息
            messages = [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": f"请分析以下问题：{question}"}
            ]
            
            # 第一次调用 - 可能触发函数调用
            start_time = time.time()
            response = self.client.chat.completions.create(
                model=model,
                messages=messages,
                tools=self.tools,
                tool_choice="auto",
                max_tokens=4000,
                temperature=0.3
            )
            
            # 处理函数调用
            response_message = response.choices[0].message
            messages.append(response_message)
            
            function_calls_made = []
            
            # 如果有函数调用请求
            if response_message.tool_calls:
                for tool_call in response_message.tool_calls:
                    function_name = tool_call.function.name
                    function_args = json.loads(tool_call.function.arguments)
                    
                    logger.info(f"Agent calling function: {function_name} with args: {function_args}")
                    
                    # 执行函数调用
                    function_result = self._execute_function_call(
                        ulog_tools, function_name, function_args
                    )
                    
                    function_calls_made.append({
                        "function": function_name,
                        "arguments": function_args,
                        "result_summary": self._summarize_function_result(function_result)
                    })
                    
                    # 添加函数调用结果到消息历史
                    messages.append({
                        "tool_call_id": tool_call.id,
                        "role": "tool",
                        "name": function_name,
                        "content": json.dumps(function_result, ensure_ascii=False)
                    })
                
                # 第二次调用 - 基于函数调用结果生成最终分析
                final_response = self.client.chat.completions.create(
                    model=model,
                    messages=messages,
                    max_tokens=4000,
                    temperature=0.3
                )
                
                final_analysis = final_response.choices[0].message.content
                total_tokens = response.usage.total_tokens + final_response.usage.total_tokens
                
            else:
                # 没有函数调用，直接使用第一次响应
                final_analysis = response_message.content
                total_tokens = response.usage.total_tokens
            
            processing_time = time.time() - start_time
            
            return {
                "success": True,
                "analysis": final_analysis,
                "metadata": {
                    "model_used": model,
                    "processing_time": processing_time,
                    "tokens_used": total_tokens,
                    "function_calls": function_calls_made,
                    "has_function_calls": len(function_calls_made) > 0
                }
            }
            
        except Exception as e:
            logger.error(f"Flight analysis with function calling failed: {e}")
            return {
                "success": False,
                "error": str(e),
                "analysis": f"分析过程中出现错误: {str(e)}"
            }
    
    def _execute_function_call(self, ulog_tools: ULogDataTools, 
                             function_name: str, function_args: Dict[str, Any]) -> Dict[str, Any]:
        """执行函数调用"""
        try:
            if function_name == "get_battery_status_data":
                time_range = function_args.get("time_range")
                return ulog_tools.get_battery_status_data(time_range)
                
            elif function_name == "get_power_system_data":
                return ulog_tools.get_power_system_data()
                
            elif function_name == "get_flight_performance_data":
                return ulog_tools.get_flight_performance_data()
                
            elif function_name == "get_gps_navigation_data":
                analysis_type = function_args.get("analysis_type", "comprehensive")
                return ulog_tools.get_gps_navigation_data(analysis_type)
                
            else:
                return {"error": f"Unknown function: {function_name}"}
                
        except Exception as e:
            logger.error(f"Function call execution failed: {e}")
            return {"error": str(e)}
    
    def _summarize_function_result(self, result: Dict[str, Any]) -> str:
        """总结函数调用结果"""
        if "error" in result:
            return f"错误: {result['error']}"
        
        # 根据结果类型生成摘要
        if "battery_data" in str(result) or "voltage" in str(result):
            return "获取了电池状态数据"
        elif "gps" in str(result) or "satellite" in str(result):
            return "获取了GPS导航数据"
        elif "performance" in str(result) or "speed" in str(result):
            return "获取了飞行性能数据"
        else:
            return "获取了飞行数据"

# 全局实例
_flight_agent = None

def get_flight_agent() -> FlightAnalysisAgent:
    """获取飞行分析Agent实例"""
    global _flight_agent
    if _flight_agent is None:
        _flight_agent = FlightAnalysisAgent()
    return _flight_agent

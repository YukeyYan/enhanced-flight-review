"""
LLM Agent Tornado 处理器
提供LLM智能分析的HTTP接口
"""

import json
import asyncio
import logging
import time
from typing import Dict, Any, Optional

import tornado.web
from tornado.concurrent import run_on_executor
from concurrent.futures import ThreadPoolExecutor

# 导入LLM Agent模块
import sys
import os
sys.path.append(os.path.join(os.path.dirname(os.path.realpath(__file__)), '..', 'llm_agent'))
sys.path.append(os.path.join(os.path.dirname(os.path.realpath(__file__)), '..'))

try:
    from llm_agent.agent_controller import get_agent_controller, AgentResponse
    from llm_agent.config import get_llm_config
except ImportError:
    # 备用导入方式
    from agent_controller import get_agent_controller, AgentResponse
    from config import get_llm_config

# 配置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class LLMAnalysisHandler(tornado.web.RequestHandler):
    """LLM分析请求处理器"""
    
    # 用于执行异步操作的线程池
    executor = ThreadPoolExecutor(max_workers=4)
    
    def initialize(self):
        """初始化处理器"""
        try:
            self.agent_controller = get_agent_controller()
            logger.info("LLM Agent Controller initialized successfully")
        except Exception as e:
            logger.error(f"Failed to initialize LLM Agent Controller: {e}")
            self.agent_controller = None
    
    def set_default_headers(self):
        """设置默认HTTP头"""
        self.set_header("Access-Control-Allow-Origin", "*")
        self.set_header("Access-Control-Allow-Headers", "Content-Type, Authorization")
        self.set_header("Access-Control-Allow-Methods", "POST, GET, OPTIONS")
        self.set_header("Content-Type", "application/json")
    
    def options(self):
        """处理OPTIONS请求（CORS预检请求）"""
        self.set_status(200)
        self.finish()
    
    def _validate_request_data(self, data: Dict[str, Any]) -> tuple:
        """
        验证请求数据
        
        Args:
            data: 请求数据
            
        Returns:
            (是否有效, 错误信息)
        """
        if not isinstance(data, dict):
            return False, "请求数据必须是JSON格式"
        
        if 'question' not in data:
            return False, "缺少必需的'question'字段"
        
        question = data['question']
        if not question or not isinstance(question, str) or not question.strip():
            return False, "问题内容不能为空"
        
        if len(question) > 1000:
            return False, "问题长度不能超过1000字符"
        
        return True, ""
    
    def _serialize_metadata(self, metadata: Dict[str, Any]) -> Dict[str, Any]:
        """
        序列化metadata，处理不能JSON序列化的对象
        
        Args:
            metadata: 元数据字典
            
        Returns:
            可序列化的元数据字典
        """
        serialized = {}
        for key, value in metadata.items():
            try:
                # 测试是否可以JSON序列化
                json.dumps(value)
                serialized[key] = value
            except TypeError:
                # 如果不能序列化，转换为字符串
                if hasattr(value, '__dict__'):
                    # 如果是对象，尝试转换为字典
                    try:
                        from dataclasses import asdict
                        serialized[key] = asdict(value)
                    except:
                        serialized[key] = str(value)
                else:
                    serialized[key] = str(value)
        return serialized
    
    def _extract_flight_data_from_log_id(self, log_id: str) -> Dict[str, Any]:
        """
        从日志ID提取飞行数据（模拟实现）
        
        Args:
            log_id: 日志ID
            
        Returns:
            飞行数据字典
        """
        # TODO: 实际实现应该从数据库或文件系统中加载ULog数据
        # 这里提供模拟数据用于测试
        try:
            # 尝试从现有系统加载数据
            sys.path.append(os.path.join(os.path.dirname(os.path.realpath(__file__)), '..', 'plot_app'))
            from db_entry import get_db_entry_from_log_id
            
            db_entry = get_db_entry_from_log_id(log_id)
            if db_entry:
                # 从数据库条目提取基本信息
                flight_data = {
                    'log_id': log_id,
                    'duration': getattr(db_entry, 'duration_s', 0),
                    'distance': getattr(db_entry, 'distance_m', 0),
                    'max_altitude': getattr(db_entry, 'max_altitude_m', 0),
                    'flight_modes': getattr(db_entry, 'flight_modes', []),
                    'start_time': str(getattr(db_entry, 'start_time_utc', '')),
                    'end_time': str(getattr(db_entry, 'end_time_utc', '')),
                    'vehicle_name': getattr(db_entry, 'vehicle_name', ''),
                    'vehicle_type': getattr(db_entry, 'vehicle_type', ''),
                    'hardware': getattr(db_entry, 'hardware', ''),
                    'software': getattr(db_entry, 'software_version', ''),
                }
                
                # 尝试提取更多统计数据（如果可用）
                # TODO: 实现具体的统计数据提取逻辑
                
                return flight_data
            else:
                logger.warning(f"No database entry found for log_id: {log_id}")
                
        except Exception as e:
            logger.error(f"Error loading flight data for log_id {log_id}: {e}")
        
        # 返回模拟数据
        return {
            'log_id': log_id,
            'duration': 300,  # 5分钟
            'distance': 1500,  # 1.5km
            'max_altitude': 50,  # 50米
            'flight_modes': ['Manual', 'Position', 'Return'],
            'start_time': '2024-01-15 10:30:00',
            'end_time': '2024-01-15 10:35:00',
            'vehicle_name': 'Test Drone',
            'vehicle_type': 'Quadrotor',
            'hardware': 'Pixhawk 4',
            'software': 'PX4 v1.14',
            'attitude_roll_std': 2.5,
            'attitude_pitch_std': 3.1,
            'attitude_yaw_range': 45,
            'battery_voltage_min': 14.2,
            'battery_voltage_max': 16.8,
            'battery_current_avg': 8.5,
            'battery_current_max': 15.2,
            'gps_satellites_avg': 12,
            'detected_anomalies': []
        }
    
    @run_on_executor
    def _run_async_analysis(self, question: str, flight_data: Dict[str, Any], 
                           session_id: Optional[str] = None) -> AgentResponse:
        """
        在线程池中运行异步分析
        
        Args:
            question: 用户问题
            flight_data: 飞行数据
            session_id: 会话ID
            
        Returns:
            分析结果
        """
        try:
            # 在新的事件循环中运行异步操作
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            
            try:
                result = loop.run_until_complete(
                    self.agent_controller.analyze_question(question, flight_data, session_id)
                )
                return result
            finally:
                loop.close()
                
        except Exception as e:
            logger.error(f"Error in async analysis: {e}")
            # 返回错误响应
            from dataclasses import asdict
            error_response = AgentResponse(
                success=False,
                intent="error",
                analysis=f"分析过程中出现错误: {str(e)}",
                charts=[],
                suggestions=[],
                confidence=0.0,
                processing_time=0.0,
                metadata={},
                error=str(e)
            )
            return error_response
    
    async def post(self):
        """处理POST请求 - 执行LLM分析"""
        try:
            # 检查Agent控制器是否可用
            if self.agent_controller is None:
                self.set_status(500)
                response = {
                    'success': False,
                    'error': 'LLM Agent未能正确初始化，请检查配置'
                }
                await self.finish(json.dumps(response, ensure_ascii=False))
                return
            
            # 解析请求数据
            try:
                # 尝试不同的编码方式
                body_text = self.request.body.decode('utf-8', errors='replace')
                data = json.loads(body_text)
            except (json.JSONDecodeError, UnicodeDecodeError) as e:
                self.set_status(400)
                response = {
                    'success': False,
                    'error': f'无效的JSON数据: {str(e)}'
                }
                await self.finish(json.dumps(response, ensure_ascii=False))
                return
            
            # 验证请求数据
            is_valid, error_msg = self._validate_request_data(data)
            if not is_valid:
                self.set_status(400)
                response = {
                    'success': False,
                    'error': error_msg
                }
                await self.finish(json.dumps(response, ensure_ascii=False))
                return
            
            # 提取请求参数
            question = data['question'].strip()
            log_id = data.get('log_id', '')
            session_id = data.get('session_id', None)
            
            logger.info(f"Processing analysis request: {question[:50]}... (log_id: {log_id})")
            
            # 获取飞行数据
            if log_id:
                flight_data = self._extract_flight_data_from_log_id(log_id)
            else:
                # 使用提供的飞行数据或默认数据
                flight_data = data.get('flight_data', {
                    'duration': 0,
                    'note': '未提供具体的飞行数据，分析结果可能不够准确'
                })
            
            # 执行分析
            start_time = time.time()
            analysis_result = await self._run_async_analysis(question, flight_data, session_id)
            processing_time = time.time() - start_time
            
            # 构建响应
            response = {
                'success': analysis_result.success,
                'data': {
                    'intent': analysis_result.intent,
                    'analysis': analysis_result.analysis,
                    'charts': analysis_result.charts,
                    'suggestions': analysis_result.suggestions,
                    'confidence': analysis_result.confidence,
                    'processing_time': processing_time,
                    'metadata': self._serialize_metadata(analysis_result.metadata)
                }
            }
            
            if not analysis_result.success:
                response['error'] = analysis_result.error
                self.set_status(500)
            
            logger.info(f"Analysis completed in {processing_time:.2f}s, success: {analysis_result.success}")
            
            await self.finish(json.dumps(response, ensure_ascii=False, indent=2))
            
        except Exception as e:
            logger.error(f"Unexpected error in LLM analysis handler: {e}")
            self.set_status(500)
            response = {
                'success': False,
                'error': f'服务器内部错误: {str(e)}'
            }
            await self.finish(json.dumps(response, ensure_ascii=False))

class LLMChatHandler(tornado.web.RequestHandler):
    """LLM聊天界面处理器"""
    
    def get(self):
        """返回聊天界面HTML"""
        # TODO: 实现聊天界面HTML模板
        html_content = """
<!DOCTYPE html>
<html>
<head>
    <title>Flight Review - AI Assistant</title>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <style>
        body { font-family: Arial, sans-serif; margin: 0; padding: 20px; background-color: #f5f5f5; }
        .container { max-width: 1200px; margin: 0 auto; background: white; padding: 20px; border-radius: 8px; box-shadow: 0 2px 10px rgba(0,0,0,0.1); }
        .chat-header { text-align: center; margin-bottom: 30px; color: #333; }
        .chat-container { border: 1px solid #ddd; height: 400px; overflow-y: auto; padding: 15px; margin-bottom: 15px; background: #fafafa; }
        .message { margin-bottom: 15px; padding: 10px; border-radius: 5px; }
        .user-message { background: #e3f2fd; margin-left: 20%; }
        .bot-message { background: #f1f8e9; margin-right: 20%; }
        .input-group { display: flex; gap: 10px; }
        .question-input { flex: 1; padding: 10px; border: 1px solid #ddd; border-radius: 4px; }
        .send-btn { padding: 10px 20px; background: #2196f3; color: white; border: none; border-radius: 4px; cursor: pointer; }
        .send-btn:hover { background: #1976d2; }
        .send-btn:disabled { background: #ccc; cursor: not-allowed; }
        .quick-questions { margin-bottom: 20px; }
        .quick-btn { margin: 5px; padding: 8px 15px; background: #f0f0f0; border: 1px solid #ddd; border-radius: 20px; cursor: pointer; font-size: 14px; }
        .quick-btn:hover { background: #e0e0e0; }
        .status { text-align: center; color: #666; font-style: italic; }
    </style>
</head>
<body>
    <div class="container">
        <div class="chat-header">
            <h1>🤖 Flight Review AI Assistant</h1>
            <p>询问您的飞行日志相关问题，获得专业的AI分析建议</p>
        </div>
        
        <div class="quick-questions">
            <h3>常见问题快速询问：</h3>
            <button class="quick-btn" onclick="askQuestion('为什么我的无人机会振荡？')">为什么会振荡？</button>
            <button class="quick-btn" onclick="askQuestion('这次飞行的整体表现如何？')">整体表现如何？</button>
            <button class="quick-btn" onclick="askQuestion('电池性能是否正常？')">电池性能正常吗？</button>
            <button class="quick-btn" onclick="askQuestion('GPS信号质量怎么样？')">GPS信号质量？</button>
            <button class="quick-btn" onclick="askQuestion('有检测到什么异常吗？')">有异常吗？</button>
        </div>
        
        <div class="chat-container" id="chatContainer">
            <div class="message bot-message">
                <strong>AI Assistant:</strong> 您好！我是Flight Review的AI助手。请告诉我您想了解的飞行日志问题，我会为您提供专业的分析和建议。
            </div>
        </div>
        
        <div class="input-group">
            <input type="text" class="question-input" id="questionInput" placeholder="输入您的问题..." 
                   onkeypress="handleKeyPress(event)">
            <button class="send-btn" id="sendBtn" onclick="sendQuestion()">发送</button>
        </div>
        
        <div class="status" id="status"></div>
    </div>

    <script>
        function addMessage(content, isUser = false) {
            const container = document.getElementById('chatContainer');
            const messageDiv = document.createElement('div');
            messageDiv.className = `message ${isUser ? 'user-message' : 'bot-message'}`;
            messageDiv.innerHTML = `<strong>${isUser ? '您' : 'AI Assistant'}:</strong> ${content}`;
            container.appendChild(messageDiv);
            container.scrollTop = container.scrollHeight;
        }

        function setStatus(message) {
            document.getElementById('status').textContent = message;
        }

        function askQuestion(question) {
            document.getElementById('questionInput').value = question;
            sendQuestion();
        }

        function handleKeyPress(event) {
            if (event.key === 'Enter') {
                sendQuestion();
            }
        }

        async function sendQuestion() {
            const input = document.getElementById('questionInput');
            const sendBtn = document.getElementById('sendBtn');
            const question = input.value.trim();
            
            if (!question) {
                alert('请输入问题！');
                return;
            }

            // 禁用输入
            input.disabled = true;
            sendBtn.disabled = true;
            setStatus('正在分析中，请稍候...');
            
            // 添加用户消息
            addMessage(question, true);
            input.value = '';

            try {
                const response = await fetch('/api/llm/analyze', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                    },
                    body: JSON.stringify({
                        question: question,
                        log_id: new URLSearchParams(window.location.search).get('log') || ''
                    })
                });

                const result = await response.json();
                
                if (result.success) {
                    let analysis = result.data.analysis;
                    if (result.data.charts && result.data.charts.length > 0) {
                        analysis += `<br><br><strong>建议查看的图表：</strong><br>` + 
                                   result.data.charts.map(chart => `• ${chart}`).join('<br>');
                    }
                    if (result.data.suggestions && result.data.suggestions.length > 0) {
                        analysis += `<br><br><strong>优化建议：</strong><br>` + 
                                   result.data.suggestions.map(s => `• ${s.suggestion || s}`).join('<br>');
                    }
                    addMessage(analysis);
                } else {
                    addMessage(`抱歉，分析失败：${result.error}`);
                }
            } catch (error) {
                addMessage(`网络错误：${error.message}`);
            } finally {
                // 重新启用输入
                input.disabled = false;
                sendBtn.disabled = false;
                setStatus('');
                input.focus();
            }
        }
    </script>
</body>
</html>
        """
        
        self.set_header("Content-Type", "text/html; charset=utf-8")
        self.write(html_content)

class LLMStatusHandler(tornado.web.RequestHandler):
    """LLM Agent状态检查处理器"""
    
    def get(self):
        """获取LLM Agent状态"""
        try:
            config = get_llm_config()
            agent_controller = get_agent_controller()
            
            status = {
                'llm_available': True,
                'config_valid': config.validate_config(),
                'openai_model': config.get('openai', 'model', 'Unknown'),
                'stats': agent_controller.get_stats() if agent_controller else {}
            }
            
        except Exception as e:
            status = {
                'llm_available': False,
                'error': str(e),
                'config_valid': False
            }
        
        self.set_header("Content-Type", "application/json")
        self.write(json.dumps(status, indent=2))

if __name__ == "__main__":
    # 测试代码
    import tornado.ioloop
    import tornado.web
    
    app = tornado.web.Application([
        (r"/api/llm/analyze", LLMAnalysisHandler),
        (r"/api/llm/chat", LLMChatHandler),
        (r"/api/llm/status", LLMStatusHandler),
    ])
    
    app.listen(8888)
    print("LLM Agent test server started on http://localhost:8888")
    print("Test endpoints:")
    print("  - Chat interface: http://localhost:8888/api/llm/chat")
    print("  - Status check: http://localhost:8888/api/llm/status")
    
    tornado.ioloop.IOLoop.current().start()
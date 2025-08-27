"""
简化版LLM Agent Tornado 处理器
提供基本的LLM智能分析HTTP接口
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

# 配置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class SimpleLLMAnalysisHandler(tornado.web.RequestHandler):
    """简化版LLM分析请求处理器"""
    
    # 用于执行异步操作的线程池
    executor = ThreadPoolExecutor(max_workers=2)
    
    def initialize(self):
        """初始化处理器"""
        try:
            from agent_controller import get_agent_controller
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
        self.set_header("Content-Type", "application/json; charset=utf-8")
    
    def options(self):
        """处理OPTIONS请求（CORS预检请求）"""
        self.set_status(200)
        self.finish()
    
    @run_on_executor
    def _run_async_analysis(self, question: str, flight_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        在线程池中运行异步分析
        
        Args:
            question: 用户问题
            flight_data: 飞行数据
            
        Returns:
            分析结果字典
        """
        try:
            # 在新的事件循环中运行异步操作
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            
            try:
                result = loop.run_until_complete(
                    self.agent_controller.analyze_question(question, flight_data)
                )
                
                # 转换为字典格式
                return {
                    'success': result.success,
                    'intent': result.intent,
                    'analysis': result.analysis,
                    'charts': result.charts,
                    'suggestions': result.suggestions,
                    'confidence': result.confidence,
                    'processing_time': result.processing_time,
                    'error': result.error
                }
            finally:
                loop.close()
                
        except Exception as e:
            logger.error(f"Error in async analysis: {e}")
            return {
                'success': False,
                'intent': 'error',
                'analysis': f'分析过程中出现错误: {str(e)}',
                'charts': [],
                'suggestions': [],
                'confidence': 0.0,
                'processing_time': 0.0,
                'error': str(e)
            }
    
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
                self.finish(json.dumps(response, ensure_ascii=False))
                return
            
            # 解析请求数据
            try:
                data = json.loads(self.request.body.decode('utf-8'))
            except json.JSONDecodeError as e:
                self.set_status(400)
                response = {
                    'success': False,
                    'error': f'无效的JSON数据: {str(e)}'
                }
                self.finish(json.dumps(response, ensure_ascii=False))
                return
            
            # 验证请求数据
            question = data.get('question', '').strip()
            if not question:
                self.set_status(400)
                response = {
                    'success': False,
                    'error': '问题内容不能为空'
                }
                self.finish(json.dumps(response, ensure_ascii=False))
                return
            
            # 提取请求参数
            log_id = data.get('log_id', '')
            
            logger.info(f"Processing analysis request: {question[:50]}...")
            
            # 使用模拟飞行数据
            flight_data = {
                'log_id': log_id or 'test-flight',
                'duration': 300,
                'distance': 1500,
                'max_altitude': 50,
                'flight_modes': ['Manual', 'Position', 'Return'],
                'attitude_roll_std': 2.5,
                'attitude_pitch_std': 3.1,
                'attitude_yaw_range': 45,
                'battery_voltage_min': 14.2,
                'battery_current_avg': 8.5,
                'detected_anomalies': []
            }
            
            # 执行分析
            start_time = time.time()
            analysis_result = await self._run_async_analysis(question, flight_data)
            processing_time = time.time() - start_time
            
            # 构建响应
            response = {
                'success': analysis_result['success'],
                'data': {
                    'intent': analysis_result['intent'],
                    'analysis': analysis_result['analysis'],
                    'charts': analysis_result['charts'],
                    'suggestions': analysis_result['suggestions'],
                    'confidence': analysis_result['confidence'],
                    'processing_time': processing_time
                }
            }
            
            if not analysis_result['success']:
                response['error'] = analysis_result['error']
                self.set_status(500)
            
            logger.info(f"Analysis completed in {processing_time:.2f}s, success: {analysis_result['success']}")
            
            self.finish(json.dumps(response, ensure_ascii=False, indent=2))
            
        except Exception as e:
            logger.error(f"Unexpected error in LLM analysis handler: {e}")
            self.set_status(500)
            response = {
                'success': False,
                'error': f'服务器内部错误: {str(e)}'
            }
            self.finish(json.dumps(response, ensure_ascii=False))

class SimpleLLMChatHandler(tornado.web.RequestHandler):
    """简化版LLM聊天界面处理器"""
    
    def get(self):
        """返回聊天界面HTML"""
        html_content = """<!DOCTYPE html>
<html>
<head>
    <title>Flight Review - AI Assistant</title>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <style>
        body { font-family: Arial, sans-serif; margin: 0; padding: 20px; background: #f5f5f5; }
        .container { max-width: 1000px; margin: 0 auto; background: white; padding: 20px; border-radius: 8px; }
        .title { text-align: center; color: #333; margin-bottom: 30px; }
        .chat-box { border: 1px solid #ddd; height: 400px; overflow-y: auto; padding: 15px; margin-bottom: 15px; background: #fafafa; }
        .message { margin: 10px 0; padding: 10px; border-radius: 5px; }
        .user-msg { background: #e3f2fd; margin-left: 20%; }
        .bot-msg { background: #f1f8e9; margin-right: 20%; }
        .input-area { display: flex; gap: 10px; }
        .question-input { flex: 1; padding: 10px; border: 1px solid #ddd; border-radius: 4px; }
        .send-btn { padding: 10px 20px; background: #2196f3; color: white; border: none; border-radius: 4px; cursor: pointer; }
        .send-btn:hover { background: #1976d2; }
        .send-btn:disabled { background: #ccc; }
        .quick-btns { margin-bottom: 15px; }
        .quick-btn { margin: 5px; padding: 8px 15px; background: #f0f0f0; border: 1px solid #ddd; border-radius: 15px; cursor: pointer; }
        .quick-btn:hover { background: #e0e0e0; }
        .status { text-align: center; color: #666; font-style: italic; margin-top: 10px; }
    </style>
</head>
<body>
    <div class="container">
        <div class="title">
            <h1>Flight Review AI Assistant</h1>
            <p>询问您的飞行日志相关问题，获得专业的AI分析建议</p>
        </div>
        
        <div class="quick-btns">
            <h3>快速提问：</h3>
            <button class="quick-btn" onclick="askQuestion('为什么我的无人机会振荡？')">为什么会振荡？</button>
            <button class="quick-btn" onclick="askQuestion('这次飞行的整体表现如何？')">整体表现如何？</button>
            <button class="quick-btn" onclick="askQuestion('电池性能是否正常？')">电池性能正常吗？</button>
            <button class="quick-btn" onclick="askQuestion('GPS信号质量怎么样？')">GPS信号质量？</button>
            <button class="quick-btn" onclick="askQuestion('有检测到什么异常吗？')">有异常吗？</button>
        </div>
        
        <div class="chat-box" id="chatBox">
            <div class="message bot-msg">
                <strong>AI助手:</strong> 您好！我是Flight Review的AI助手。请告诉我您想了解的飞行日志问题，我会为您提供专业的分析和建议。
            </div>
        </div>
        
        <div class="input-area">
            <input type="text" class="question-input" id="questionInput" placeholder="输入您的问题..." onkeypress="handleKeyPress(event)">
            <button class="send-btn" id="sendBtn" onclick="sendQuestion()">发送</button>
        </div>
        
        <div class="status" id="status"></div>
    </div>

    <script>
        function addMessage(content, isUser) {
            const chatBox = document.getElementById('chatBox');
            const msgDiv = document.createElement('div');
            msgDiv.className = 'message ' + (isUser ? 'user-msg' : 'bot-msg');
            msgDiv.innerHTML = '<strong>' + (isUser ? '您' : 'AI助手') + ':</strong> ' + content;
            chatBox.appendChild(msgDiv);
            chatBox.scrollTop = chatBox.scrollHeight;
        }

        function setStatus(msg) {
            document.getElementById('status').textContent = msg;
        }

        function askQuestion(question) {
            document.getElementById('questionInput').value = question;
            sendQuestion();
        }

        function handleKeyPress(event) {
            if (event.key === 'Enter') sendQuestion();
        }

        async function sendQuestion() {
            const input = document.getElementById('questionInput');
            const sendBtn = document.getElementById('sendBtn');
            const question = input.value.trim();
            
            if (!question) {
                alert('请输入问题！');
                return;
            }

            input.disabled = true;
            sendBtn.disabled = true;
            setStatus('正在分析中，请稍候...');
            
            addMessage(question, true);
            input.value = '';

            try {
                const response = await fetch('/api/llm/analyze', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ question: question })
                });

                const result = await response.json();
                
                if (result.success) {
                    let analysis = result.data.analysis;
                    if (result.data.charts && result.data.charts.length > 0) {
                        analysis += '<br><br><strong>建议查看图表:</strong><br>' + 
                                   result.data.charts.map(c => '• ' + c).join('<br>');
                    }
                    addMessage(analysis, false);
                } else {
                    addMessage('抱歉，分析失败：' + (result.error || '未知错误'), false);
                }
            } catch (error) {
                addMessage('网络错误：' + error.message, false);
            } finally {
                input.disabled = false;
                sendBtn.disabled = false;
                setStatus('');
                input.focus();
            }
        }
    </script>
</body>
</html>"""
        
        self.set_header("Content-Type", "text/html; charset=utf-8")
        self.write(html_content)

class SimpleLLMStatusHandler(tornado.web.RequestHandler):
    """简化版状态检查处理器"""
    
    def get(self):
        """获取LLM Agent状态"""
        try:
            from config import get_llm_config
            from agent_controller import get_agent_controller
            
            config = get_llm_config()
            agent_controller = get_agent_controller()
            
            status = {
                'llm_available': True,
                'config_valid': config.validate_config(),
                'openai_model': config.get('openai', 'model', 'Unknown'),
                'stats': agent_controller.get_stats()
            }
            
        except Exception as e:
            status = {
                'llm_available': False,
                'error': str(e),
                'config_valid': False
            }
        
        self.set_header("Content-Type", "application/json; charset=utf-8")
        self.write(json.dumps(status, indent=2, ensure_ascii=False))
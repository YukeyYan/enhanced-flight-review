#!/usr/bin/env python3
"""
ULog Data Access Tools for Agent Function Calling
ULog数据访问工具 - 用于Agent函数调用
"""

import json
import logging
import numpy as np
from typing import Dict, Any, List, Optional, Tuple
from battery_system_knowledge import analyze_battery_configuration

logger = logging.getLogger(__name__)

class ULogDataTools:
    """ULog数据访问工具类"""
    
    def __init__(self, flight_data: Dict[str, Any] = None):
        self.flight_data = flight_data or {}
        self.log_id = self.flight_data.get('log_id')
        
    def get_battery_status_data(self, time_range: Tuple[float, float] = None) -> Dict[str, Any]:
        """
        获取电池状态数据
        
        Args:
            time_range: (start_time, end_time) 时间范围，单位秒
            
        Returns:
            电池状态数据字典
        """
        try:
            # 从flight_data中提取电池相关数据
            battery_data = {
                "log_id": self.log_id,
                "summary": {
                    "voltage_max_v": self.flight_data.get('battery_voltage_max_v', 0),
                    "voltage_min_v": self.flight_data.get('battery_voltage_min_v', 0),
                    "current_max_a": self.flight_data.get('battery_current_max_a', 0),
                    "discharged_total_mah": self.flight_data.get('battery_discharged_mah', 0),
                    "flight_duration_s": self.flight_data.get('duration', 0)
                }
            }
            
            # 分析电池配置
            if battery_data["summary"]["voltage_max_v"] > 0:
                config_analysis = analyze_battery_configuration(battery_data["summary"]["voltage_max_v"])
                battery_data["configuration"] = config_analysis
            
            # 添加电池健康评估
            from battery_system_knowledge import assess_battery_health
            if all(battery_data["summary"][key] > 0 for key in ["voltage_min_v", "voltage_max_v", "current_max_a"]):
                health_analysis = assess_battery_health(
                    battery_data["summary"]["voltage_min_v"],
                    battery_data["summary"]["voltage_max_v"],
                    battery_data["summary"]["current_max_a"],
                    battery_data["summary"]["flight_duration_s"]
                )
                battery_data["health_assessment"] = health_analysis
            
            # 添加系统消息中的电池相关警告
            system_msgs = self.flight_data.get('system_messages', {})
            if 'messages' in system_msgs:
                battery_warnings = []
                for msg in system_msgs['messages']:
                    if any(keyword in msg.lower() for keyword in ['battery', 'voltage', 'power', 'current']):
                        battery_warnings.append(msg)
                if battery_warnings:
                    battery_data["system_warnings"] = battery_warnings
            
            return battery_data
            
        except Exception as e:
            logger.error(f"Failed to get battery status data: {e}")
            return {"error": str(e), "log_id": self.log_id}
    
    def get_power_system_data(self) -> Dict[str, Any]:
        """
        获取电力系统数据
        
        Returns:
            电力系统数据字典
        """
        try:
            power_data = {
                "log_id": self.log_id,
                "battery_system": self.get_battery_status_data(),
                "system_messages": self.flight_data.get('system_messages', {}),
                "power_related_events": []
            }
            
            # 提取电池相关的系统消息
            if 'system_messages' in self.flight_data:
                messages = self.flight_data['system_messages']
                if 'categorized' in messages and 'battery_warnings' in messages['categorized']:
                    power_data["battery_warnings"] = messages['categorized']['battery_warnings']
            
            return power_data
            
        except Exception as e:
            logger.error(f"Failed to get power system data: {e}")
            return {"error": str(e), "log_id": self.log_id}
    
    def get_flight_performance_data(self) -> Dict[str, Any]:
        """
        获取飞行性能数据
        
        Returns:
            飞行性能数据字典
        """
        try:
            performance_data = {
                "log_id": self.log_id,
                "basic_metrics": {
                    "flight_duration_s": self.flight_data.get('duration', 0),
                    "total_distance_m": self.flight_data.get('total_distance_m', 0),
                    "max_altitude_diff_m": self.flight_data.get('max_altitude_diff_m', 0),
                    "max_speed_ms": self.flight_data.get('max_speed_ms', 0),
                    "average_speed_ms": self.flight_data.get('average_speed_ms', 0),
                    "max_horizontal_speed_ms": self.flight_data.get('max_horizontal_speed_ms', 0)
                },
                "attitude_performance": {
                    "max_tilt_angle_deg": self.flight_data.get('max_tilt_angle_deg', 0),
                    "max_roll_rate_dps": self.flight_data.get('max_roll_rate_dps', 0),
                    "max_pitch_rate_dps": self.flight_data.get('max_pitch_rate_dps', 0),
                    "max_yaw_rate_dps": self.flight_data.get('max_yaw_rate_dps', 0)
                },
                "system_info": {
                    "mav_type": self.flight_data.get('mav_type', 'Unknown'),
                    "hardware": self.flight_data.get('hardware', 'Unknown'),
                    "software": self.flight_data.get('software', 'Unknown'),
                    "estimator": self.flight_data.get('estimator', 'Unknown')
                }
            }
            
            # 计算性能指标
            duration_min = performance_data["basic_metrics"]["flight_duration_s"] / 60
            if duration_min > 0:
                performance_data["efficiency_metrics"] = {
                    "average_speed_kmh": performance_data["basic_metrics"]["average_speed_ms"] * 3.6,
                    "distance_per_minute_m": performance_data["basic_metrics"]["total_distance_m"] / duration_min,
                    "flight_efficiency": "high" if performance_data["basic_metrics"]["average_speed_ms"] > 5 else "normal"
                }
            
            return performance_data
            
        except Exception as e:
            logger.error(f"Failed to get flight performance data: {e}")
            return {"error": str(e), "log_id": self.log_id}
    
    def get_gps_navigation_data(self, analysis_type: str = "comprehensive") -> Dict[str, Any]:
        """
        获取GPS导航数据
        
        Args:
            analysis_type: 分析类型 ("comprehensive", "accuracy", "satellite", "position")
            
        Returns:
            GPS和导航系统数据字典
        """
        try:
            gps_data = {
                "log_id": self.log_id,
                "analysis_type": analysis_type,
                "basic_info": {
                    "has_position_data": self.flight_data.get('has_position_data', False),
                    "total_distance_m": self.flight_data.get('total_distance_m', 0),
                    "max_altitude_diff_m": self.flight_data.get('max_altitude_diff_m', 0),
                    "max_horizontal_speed_ms": self.flight_data.get('max_horizontal_speed_ms', 0),
                    "estimator": self.flight_data.get('estimator', 'Unknown')
                }
            }
            
            # 从flight_data中提取GPS精度相关数据
            gps_accuracy = {}
            gps_quality_fields = [
                'gps_satellites_used', 'gps_satellites_visible', 
                'gps_hdop', 'gps_vdop', 'gps_pdop',
                'gps_horizontal_accuracy_m', 'gps_vertical_accuracy_m',
                'gps_speed_accuracy_ms', 'gps_fix_type',
                'gps_noise_per_ms', 'gps_jamming_indicator'
            ]
            
            for field in gps_quality_fields:
                if field in self.flight_data:
                    key = field.replace('gps_', '')
                    gps_accuracy[key] = self.flight_data[field]
            
            # 使用简化的字段名
            if 'gps_satellites_avg' in self.flight_data:
                gps_accuracy['satellites_avg'] = self.flight_data['gps_satellites_avg']
            if 'gps_satellites_min' in self.flight_data:
                gps_accuracy['satellites_min'] = self.flight_data['gps_satellites_min']
            if 'gps_eph_max' in self.flight_data:
                gps_accuracy['horizontal_accuracy_max_m'] = self.flight_data['gps_eph_max']
            if 'gps_epv_max' in self.flight_data:
                gps_accuracy['vertical_accuracy_max_m'] = self.flight_data['gps_epv_max']
            
            if gps_accuracy:
                gps_data["gps_accuracy"] = gps_accuracy
            
            # GPS质量评估
            if 'satellites_avg' in gps_accuracy:
                sat_avg = gps_accuracy['satellites_avg']
                if sat_avg >= 12:
                    quality = "优秀"
                    quality_score = 95
                elif sat_avg >= 8:
                    quality = "良好"
                    quality_score = 80
                elif sat_avg >= 6:
                    quality = "一般"
                    quality_score = 60
                else:
                    quality = "较差"
                    quality_score = 30
                
                gps_data["quality_assessment"] = {
                    "overall_quality": quality,
                    "quality_score": quality_score,
                    "satellite_count_analysis": {
                        "average": sat_avg,
                        "minimum": gps_accuracy.get('satellites_min', 0),
                        "status": "充足" if sat_avg >= 8 else "不足"
                    }
                }
            
            # 导航性能分析
            if gps_data["basic_info"]["total_distance_m"] > 0:
                gps_data["navigation_performance"] = {
                    "position_tracking": "正常" if gps_data["basic_info"]["has_position_data"] else "异常",
                    "distance_accuracy": "高" if gps_accuracy.get('horizontal_accuracy_max_m', 10) < 2 else "中等",
                    "altitude_tracking": "正常" if gps_data["basic_info"]["max_altitude_diff_m"] > 0 else "无数据"
                }
            
            # 系统警告
            system_msgs = self.flight_data.get('system_messages', {})
            if 'messages' in system_msgs:
                gps_warnings = []
                for msg in system_msgs['messages']:
                    if any(keyword in msg.lower() for keyword in ['gps', 'satellite', 'position', 'navigation']):
                        gps_warnings.append(msg)
                if gps_warnings:
                    gps_data["system_alerts"] = gps_warnings
            
            # 根据分析类型过滤返回数据
            if analysis_type == "accuracy":
                return {k: v for k, v in gps_data.items() 
                       if k in ["log_id", "gps_accuracy", "quality_assessment", "system_alerts"]}
            elif analysis_type == "satellite":
                return {k: v for k, v in gps_data.items() 
                       if k in ["log_id", "gps_accuracy", "quality_assessment"]}
            elif analysis_type == "position":
                return {k: v for k, v in gps_data.items() 
                       if k in ["log_id", "navigation_performance", "basic_info"]}
            
            return gps_data
            
        except Exception as e:
            logger.error(f"Failed to get GPS navigation data: {e}")
            return {"error": str(e), "log_id": self.log_id}

# 定义Agent可用的工具函数
ULOG_TOOLS = [
    # 🔋 Battery System - 电池系统
    {
        "type": "function",
        "function": {
            "name": "get_battery_status_data",
            "description": "获取当前飞行日志的电池状态数据，包括电压、电流、容量、温度等详细信息",
            "parameters": {
                "type": "object",
                "properties": {
                    "time_range": {
                        "type": "array",
                        "items": {"type": "number"},
                        "description": "时间范围 [开始时间, 结束时间]，单位秒。不提供则获取全部数据"
                    }
                }
            }
        }
    },
    {
        "type": "function", 
        "function": {
            "name": "get_power_system_data",
            "description": "获取完整的电力系统数据，包括电池状态、系统电压、电力相关警告等",
            "parameters": {
                "type": "object",
                "properties": {}
            }
        }
    },
    
    # 🛩️ Flight Performance - 飞行性能
    {
        "type": "function",
        "function": {
            "name": "get_flight_performance_data", 
            "description": "获取飞行性能指标，包括速度、高度、距离、姿态角速度等数据",
            "parameters": {
                "type": "object",
                "properties": {}
            }
        }
    },
    
    # 📡 GPS & Navigation - GPS和导航
    {
        "type": "function",
        "function": {
            "name": "get_gps_navigation_data",
            "description": "获取GPS和导航系统数据，包括卫星数量、精度、定位质量等信息",
            "parameters": {
                "type": "object", 
                "properties": {
                    "analysis_type": {
                        "type": "string",
                        "enum": ["comprehensive", "accuracy", "satellite", "position"],
                        "description": "分析类型：comprehensive(全面), accuracy(精度), satellite(卫星), position(定位)"
                    }
                }
            }
        }
    }
]

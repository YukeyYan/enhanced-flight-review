#!/usr/bin/env python3
"""
Battery System Knowledge Base
电池系统知识库 - 用于Agent专业分析
"""

import logging
from typing import Dict, Any, Tuple, List

logger = logging.getLogger(__name__)

def analyze_battery_configuration(voltage_max: float) -> Dict[str, Any]:
    """
    分析电池配置
    
    Args:
        voltage_max: 最大电压
        
    Returns:
        电池配置分析结果
    """
    try:
        # 基于最大电压推断电池配置
        if voltage_max >= 24.0:  # 6S
            cell_count = 6
            nominal_voltage = 22.2
            full_charge_voltage = 25.2
            low_voltage_warning = 21.0
            critical_voltage = 19.8
        elif voltage_max >= 16.0:  # 4S
            cell_count = 4
            nominal_voltage = 14.8
            full_charge_voltage = 16.8
            low_voltage_warning = 14.0
            critical_voltage = 13.2
        elif voltage_max >= 12.0:  # 3S
            cell_count = 3
            nominal_voltage = 11.1
            full_charge_voltage = 12.6
            low_voltage_warning = 10.5
            critical_voltage = 9.9
        elif voltage_max >= 8.0:   # 2S
            cell_count = 2
            nominal_voltage = 7.4
            full_charge_voltage = 8.4
            low_voltage_warning = 7.0
            critical_voltage = 6.6
        else:  # 1S or unknown
            cell_count = 1
            nominal_voltage = 3.7
            full_charge_voltage = 4.2
            low_voltage_warning = 3.5
            critical_voltage = 3.3
        
        return {
            "cell_count": cell_count,
            "configuration": f"{cell_count}S",
            "nominal_voltage": nominal_voltage,
            "full_charge_voltage": full_charge_voltage,
            "low_voltage_warning": low_voltage_warning,
            "critical_voltage": critical_voltage,
            "voltage_per_cell_max": voltage_max / cell_count,
            "chemistry": "LiPo" if cell_count > 1 else "Li-ion/LiPo"
        }
        
    except Exception as e:
        logger.error(f"Battery configuration analysis failed: {e}")
        return {"error": str(e)}

def assess_battery_health(voltage_min: float, voltage_max: float, 
                         current_max: float, flight_duration: int) -> Dict[str, Any]:
    """
    评估电池健康状态
    
    Args:
        voltage_min: 最低电压
        voltage_max: 最高电压
        current_max: 最大电流
        flight_duration: 飞行时长(秒)
        
    Returns:
        电池健康评估结果
    """
    try:
        config = analyze_battery_configuration(voltage_max)
        if "error" in config:
            return config
        
        # 计算电压降
        voltage_drop = voltage_max - voltage_min
        voltage_drop_per_cell = voltage_drop / config["cell_count"]
        
        # 评估电压降健康度
        if voltage_drop_per_cell < 0.5:
            voltage_health = "优秀"
            voltage_score = 95
        elif voltage_drop_per_cell < 1.0:
            voltage_health = "良好"
            voltage_score = 80
        elif voltage_drop_per_cell < 2.0:
            voltage_health = "一般"
            voltage_score = 60
        else:
            voltage_health = "较差"
            voltage_score = 30
        
        # 评估最低电压安全性
        critical_voltage = config["critical_voltage"]
        low_voltage_warning = config["low_voltage_warning"]
        
        if voltage_min >= low_voltage_warning:
            safety_status = "安全"
            safety_score = 90
        elif voltage_min >= critical_voltage:
            safety_status = "注意"
            safety_score = 60
        else:
            safety_status = "危险"
            safety_score = 20
        
        # 计算C-rate (需要电池容量信息，这里给出估算)
        estimated_capacity_ah = max(1.0, current_max / 10)  # 粗略估算
        c_rate = current_max / estimated_capacity_ah if estimated_capacity_ah > 0 else 0
        
        # C-rate评估
        if c_rate < 5:
            c_rate_health = "保守"
        elif c_rate < 15:
            c_rate_health = "正常"
        elif c_rate < 25:
            c_rate_health = "激进"
        else:
            c_rate_health = "过载"
        
        # 综合健康评分
        overall_score = (voltage_score + safety_score) / 2
        
        if overall_score >= 85:
            overall_health = "优秀"
        elif overall_score >= 70:
            overall_health = "良好"
        elif overall_score >= 50:
            overall_health = "一般"
        else:
            overall_health = "需要关注"
        
        return {
            "overall_health": overall_health,
            "overall_score": overall_score,
            "voltage_analysis": {
                "voltage_drop_v": voltage_drop,
                "voltage_drop_per_cell_v": voltage_drop_per_cell,
                "health_status": voltage_health,
                "score": voltage_score
            },
            "safety_analysis": {
                "min_voltage_v": voltage_min,
                "safety_threshold_v": low_voltage_warning,
                "critical_threshold_v": critical_voltage,
                "status": safety_status,
                "score": safety_score
            },
            "performance_analysis": {
                "max_current_a": current_max,
                "estimated_c_rate": c_rate,
                "c_rate_category": c_rate_health,
                "flight_duration_min": flight_duration / 60
            },
            "recommendations": generate_battery_recommendations(
                overall_health, voltage_health, safety_status, c_rate_health
            )
        }
        
    except Exception as e:
        logger.error(f"Battery health assessment failed: {e}")
        return {"error": str(e)}

def generate_battery_recommendations(overall_health: str, voltage_health: str, 
                                   safety_status: str, c_rate_health: str) -> List[str]:
    """生成电池使用建议"""
    recommendations = []
    
    if overall_health in ["需要关注", "一般"]:
        recommendations.append("建议检查电池老化程度，考虑更换电池")
    
    if voltage_health == "较差":
        recommendations.append("电压降过大，检查电池内阻和连接线路")
    
    if safety_status == "危险":
        recommendations.append("⚠️ 电池电压过低，立即停止使用并充电")
    elif safety_status == "注意":
        recommendations.append("电池电压偏低，建议尽快充电")
    
    if c_rate_health == "过载":
        recommendations.append("电流消耗过大，检查电机和螺旋桨配置")
    elif c_rate_health == "激进":
        recommendations.append("电流消耗较高，注意电池温度和寿命")
    
    if not recommendations:
        recommendations.append("电池状态良好，继续保持良好的使用习惯")
    
    return recommendations

def get_battery_knowledge_summary() -> Dict[str, Any]:
    """获取电池知识库摘要"""
    return {
        "supported_configurations": ["1S", "2S", "3S", "4S", "6S"],
        "chemistry_types": ["LiPo", "Li-ion"],
        "health_metrics": [
            "voltage_drop_analysis",
            "safety_threshold_check", 
            "c_rate_assessment",
            "overall_health_score"
        ],
        "recommendation_categories": [
            "usage_optimization",
            "safety_warnings",
            "maintenance_suggestions",
            "replacement_indicators"
        ]
    }

# 🚁 Enhanced Flight Review - 专业无人机飞行日志分析系统

[![License](https://img.shields.io/badge/License-BSD%203--Clause-blue.svg)](https://opensource.org/licenses/BSD-3-Clause)
[![Python](https://img.shields.io/badge/Python-3.7+-green.svg)](https://python.org)
[![PX4](https://img.shields.io/badge/PX4-Compatible-orange.svg)](https://px4.io)

基于官方 PX4 Flight Review 的增强版本，提供专业的无人机飞行日志分析和可视化功能。

## 🎯 项目特色

### ✨ 核心功能
- 🌍 **3D 地球可视化** - 基于 Cesium 的真实地形飞行轨迹
- 📊 **全面数据分析** - 支持 100+ 种 PX4 数据主题
- 🔍 **智能异常检测** - 自动识别飞行安全问题
- 📈 **专业图表** - 高质量交互式数据可视化
- 📤 **多格式导出** - CSV、KML、JSON、PDF 等格式

### 🚀 增强特性
- 📋 **详细使用文档** - 完整的系统说明和故障排除
- 🛠️ **自定义启动脚本** - 简化的启动和配置流程
- 🔧 **问题修复指南** - 常见问题的解决方案
- 📊 **系统状态监控** - 实时系统健康检查

## 📁 支持的文件格式

| 格式 | 扩展名 | 描述 | 状态 |
|------|--------|------|------|
| ULog | `.ulg` | PX4 标准飞行日志 | ✅ 完全支持 |
| 压缩 ULog | `.ulg.gz` | 压缩的日志文件 | ✅ 自动解压 |
| 加密 ULog | `.ulge` | 加密的日志文件 | ✅ 需要密钥 |

## 🚀 快速开始

### 环境要求

- Python 3.7+
- 现代浏览器 (Chrome/Firefox 推荐)
- 互联网连接 (首次使用需下载配置文件)

### 安装依赖

```bash
pip install bokeh jinja2 pyulog requests scipy simplekml pyfftw pylint smopy pycryptodome
```

### 启动系统

#### 方法1: 直接分析文件 (推荐)
```bash
cd app
python serve.py --file /path/to/your/file.ulg --show --port 5007
```

#### 方法2: 启动服务器
```bash
cd app
python serve.py --port 5007 --host localhost
```

#### 方法3: 使用启动脚本
```bash
python start_flight_review.py
```

### 访问系统

- **主页**: http://localhost:5007
- **上传页面**: http://localhost:5007/upload
- **浏览页面**: http://localhost:5007/browse

## 📊 分析功能

### 🎛️ 飞行控制分析
- **姿态分析** - Roll/Pitch/Yaw 角度和角速度
- **位置轨迹** - 2D/3D 飞行路径可视化
- **控制性能** - PID 参数效果评估
- **执行器状态** - 电机和舵机输出分析

### 🎯 传感器数据分析
- **IMU 数据** - 加速度计、陀螺仪、磁力计
- **GPS 定位** - 位置精度和信号质量
- **气压高度** - 高度测量和漂移分析
- **传感器融合** - EKF2 状态估计器分析

### 🔋 系统健康监控
- **电池状态** - 电压、电流、功率、剩余电量
- **系统负载** - CPU 使用率和内存占用
- **温度监控** - 各组件温度变化
- **错误检测** - 自动识别系统异常

### 🌍 3D 可视化
- **真实地形** - 基于卫星数据的地球表面
- **飞行回放** - 可控制的飞行过程重现
- **多视角** - 自由视角和跟踪模式
- **数据叠加** - 实时显示飞行参数

## 🔍 异常检测

系统能够自动检测以下异常情况：

### ⚠️ 飞行安全异常
- 姿态发散和振荡
- GPS 跳跃和位置漂移
- 传感器饱和和噪声异常

### 🔋 系统健康异常
- 电池低电压和电压跌落
- CPU 过载和内存不足
- 温度异常和系统错误

### 🛠️ 控制系统异常
- 执行器饱和和失效
- 控制跟踪误差过大
- 系统振荡和不稳定

## 📤 数据导出

支持多种格式的数据导出：

- **CSV** - 表格数据，便于进一步分析
- **KML** - Google Earth 兼容的轨迹文件
- **JSON** - 结构化数据，便于程序处理
- **PNG/SVG** - 高质量图表图像
- **PDF** - 完整的分析报告

## 📚 文档

- 📋 **[系统使用说明](ulogview.md)** - 详细的功能介绍和使用方法
- 🔧 **[上传问题修复](upload_fix_guide.md)** - 常见问题解决方案
- 📊 **[系统状态报告](system_status.md)** - 当前系统配置和状态

## ⚙️ 配置

### Cesium 3D 可视化配置

1. 获取免费 API 密钥: https://cesium.com/ion/signup/
2. 编辑 `app/config_user.ini`:
```ini
[general]
cesium_api_key = YOUR_API_KEY_HERE
```

### 数据库初始化

```bash
cd app
python setup_db.py
```

## 🛠️ 故障排除

### 常见问题

1. **服务器无法启动**
   - 检查端口是否被占用
   - 验证 Python 依赖是否完整安装

2. **3D 可视化无法显示**
   - 检查 Cesium API 密钥配置
   - 确保浏览器支持 WebGL

3. **文件上传失败**
   - 使用命令行直接加载文件
   - 检查文件格式和完整性

4. **分析速度慢**
   - 减少文件大小或采样率
   - 使用更高性能的计算机

## 🤝 贡献

欢迎提交 Issue 和 Pull Request！

### 开发环境设置

```bash
git clone https://github.com/your-username/flight_review_enhanced.git
cd flight_review_enhanced
pip install -r app/requirements.txt
```

## 📄 许可证

本项目基于 BSD 3-Clause 许可证开源。详见 [LICENSE.md](LICENSE.md)。

## 🙏 致谢

- [PX4 Flight Review](https://github.com/PX4/flight_review) - 原始项目
- [PX4 Autopilot](https://px4.io) - 飞控系统
- [Cesium](https://cesium.com) - 3D 地球可视化
- [Bokeh](https://bokeh.org) - 数据可视化框架

## 📞 支持

如有问题或建议，请：
1. 查看 [使用文档](ulogview.md)
2. 搜索现有 Issues
3. 创建新的 Issue

---

**让飞行数据分析变得简单而专业！** 🚁✨

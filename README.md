# 🚁 Enhanced Flight Review with AI Assistant

A professional UAV flight log analysis system based on PX4 Flight Review, enhanced with an intelligent AI assistant sidebar for real-time flight data analysis.

## ✨ Key Features

### 🌍 Core Flight Review Features
- **Complete Flight Data Analysis** - All standard PX4 Flight Review functionality
- **3D Visualization** - Cesium-based 3D flight trajectory on real Earth terrain
- **Interactive Charts** - Professional flight data visualization with Plotly
- **Multi-format Support** - ULog, compressed ULog, and encrypted ULog files

### 🤖 AI Assistant Enhancement
- **Intelligent Sidebar** - AI-powered flight analysis assistant
- **Real-time Analysis** - Ask questions about your flight data
- **Professional Insights** - Get expert-level analysis and recommendations
- **Interactive Chat** - Natural language interface for flight data queries

### 📊 Analysis Capabilities
- **Attitude Analysis** - Roll/Pitch/Yaw performance evaluation
- **Position Tracking** - GPS accuracy and trajectory analysis  
- **Sensor Data** - IMU, magnetometer, barometer analysis
- **Battery Performance** - Power consumption and health monitoring
- **Control System** - Actuator performance and PID analysis
- **System Health** - CPU load, temperature, and error detection

## 🚀 Quick Start

### Prerequisites
- Python 3.7+
- Modern web browser (Chrome/Firefox recommended)
- Internet connection (for initial configuration download)

### Installation

1. **Clone the repository**
```bash
git clone https://github.com/YukeyYan/enhanced-flight-review.git
cd enhanced-flight-review
```

2. **Install dependencies**
```bash
pip install -r app/requirements.txt
```

3. **Configure Cesium API (for 3D visualization)**
```bash
# Get free API key from https://cesium.com/ion/signup/
# Edit app/config_user.ini and add your key:
echo "[general]" > app/config_user.ini
echo "cesium_api_key = YOUR_API_KEY_HERE" >> app/config_user.ini
```

4. **Initialize database**
```bash
cd app
python setup_db.py
```

### Usage

#### Method 1: Direct File Analysis (Recommended)
```bash
cd app
python serve.py --file /path/to/your/file.ulg --show --port 5007
```

#### Method 2: Web Server Mode
```bash
cd app
python serve.py --port 5007 --host localhost
```

Then visit: http://localhost:5007

## 🤖 AI Assistant Features

The AI assistant sidebar provides:

- **Flight Safety Analysis** - Automatic detection of safety issues
- **Performance Evaluation** - Control system performance assessment  
- **Anomaly Detection** - Identification of unusual flight patterns
- **Expert Recommendations** - Professional advice for flight improvements
- **Interactive Q&A** - Natural language queries about flight data

### Example AI Queries
- "Why is my drone oscillating during hover?"
- "How is the battery performance in this flight?"
- "Are there any GPS accuracy issues?"
- "What caused the altitude variations?"
- "Is the control system performing well?"

## 📁 Project Structure

```
enhanced-flight-review/
├── app/
│   ├── serve.py                 # Main server application
│   ├── config_user.ini          # User configuration (API keys)
│   ├── config_default.ini       # Default configuration
│   ├── requirements.txt         # Python dependencies
│   ├── setup_db.py             # Database initialization
│   ├── plot_app/               # Core plotting and analysis
│   │   ├── main.py             # Main application logic
│   │   ├── templates/          # HTML templates with AI sidebar
│   │   ├── static/             # CSS, JS, and assets
│   │   └── tornado_handlers/   # Web request handlers
│   └── tornado_handlers/       # Additional web handlers
│       ├── llm_agent.py        # AI assistant backend
│       └── llm_agent_simple.py # Simplified AI interface
├── LICENSE.md                  # BSD 3-Clause License
└── README.md                   # This file
```

## 🔧 Configuration

### Cesium 3D Visualization
1. Sign up for free at https://cesium.com/ion/signup/
2. Get your access token
3. Add to `app/config_user.ini`:
```ini
[general]
cesium_api_key = your_token_here
```

### AI Assistant (Optional)
The AI assistant requires an OpenAI API key for advanced analysis:
1. Get API key from https://openai.com/api/
2. Set environment variable: `export OPENAI_API_KEY=your_key_here`

## 🌐 Supported File Formats

| Format | Extension | Description | Status |
|--------|-----------|-------------|--------|
| ULog | `.ulg` | PX4 standard flight logs | ✅ Full support |
| Compressed ULog | `.ulg.gz` | Compressed flight logs | ✅ Auto-decompress |
| Encrypted ULog | `.ulge` | Encrypted flight logs | ✅ With key |

## 🛠️ Development

### Running in Development Mode
```bash
cd app
python serve.py --port 5007 --show
```

### Contributing
1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Submit a pull request

## 📄 License

This project is licensed under the BSD 3-Clause License - see the [LICENSE.md](LICENSE.md) file for details.

## 🙏 Acknowledgments

- [PX4 Flight Review](https://github.com/PX4/flight_review) - Original project
- [PX4 Autopilot](https://px4.io) - Flight control system
- [Cesium](https://cesium.com) - 3D Earth visualization
- [Bokeh](https://bokeh.org) - Data visualization framework

## 📞 Support

- 📖 Check the documentation in the web interface
- 🐛 Report issues on GitHub
- 💬 Use the AI assistant for flight analysis questions

---

**Professional flight data analysis made simple with AI assistance!** 🚁✨

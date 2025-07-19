# Sannetic Explorer Web Dashboard

## Overview

The **Sannetic Explorer Web Dashboard** is a real-time status monitoring interface designed in the style of **Stargate Universe (SGU)**. It provides comprehensive system insights through your web browser with a dark, technical aesthetic featuring monospace fonts, clean lines, professional status indicators, and an **animated starfield background** for an authentic space exploration atmosphere.

## 🚀 Quick Start

### Start the Dashboard
```bash
make dashboard
```

### Open in Browser
```bash
make open-dashboard
```

**URL:** http://localhost:8080

## 📊 Dashboard Features

### 1. **System Health Monitor**
- **[SYS]** Overall system status (ONLINE/WARNING/ERROR)
- System uptime tracking
- Component health checks:
  - Data directory integrity
  - Logs directory status
  - Scripts availability
  - Configuration files

### 2. **Data Statistics**
- **[DATA]** **Total Objects:** Real-time count of all tracked objects
- **Satellites:** 29 artificial satellites
- **Planets:** 10 planets in our solar system
- **Natural Satellites:** 315+ moons and natural satellites
- **Spacecraft:** Active space missions
- **Stars:** Stellar objects
- **Data Quality Assessment:** Excellent/Good/Fair/Poor rating

### 3. **Error Monitoring**
- ⚠️ **Real-time Error Count**
- 📝 **Recent Error Details** with timestamps
- 🔍 **Component-specific Error Tracking**
- 📋 **Error History** from log files

### 4. **API Status**
- 🔑 **API Credentials Status:**
  - OpenAI API (AI features)
  - N2YO API (real-time tracking)
  - Space-Track API (TLE data)
- 📊 **Availability Counter:** X/3 APIs configured

### 5. **AI System Status**
- 🤖 **AI Features Availability:**
  - AI Assistant (error debugging, calculations)
  - Enhanced Delta Manager (smart updates)
  - AI Health Check (system analysis)
- ✅ **AI Activation Status**

### 6. **Recent Activity**
- 📝 **Live Activity Feed**
- 🕒 **Timestamped Events**
- 🎯 **Component-specific Actions**
- 📊 **Activity Statistics**

### 7. **Terminal Log Viewer**
- 💻 **Terminal-style Interface**
- 🎨 **Color-coded Log Levels:**
  - 🔴 **ERROR** - Critical issues
  - 🟡 **WARNING** - Attention needed
  - 🟢 **INFO** - Normal operations
- 📜 **Live Log Streaming**
- 🔄 **Auto-scroll to Latest**

## 🔄 Auto-Refresh System

- **⏰ 30-second Auto-refresh** for all data
- **🔄 Real-time Countdown** indicator
- **🔁 Manual Refresh** buttons available
- **📱 Mobile-friendly** responsive design

## Design Philosophy

### SGU-Inspired Interface
- **Dark Theme** with deep black background (#0a0a0a)
- **Animated Starfield Background** with slowly moving stars and nebula effects
- **Monospace Typography** (Courier New) for technical authenticity
- **Minimal Color Palette** focused on functionality
- **Clean Geometric Lines** without rounded corners
- **Status Indicators** with subtle glow effects:
  - Green (#00ff88): Healthy/Available/Online
  - Orange (#ffaa00): Warning/Limited
  - Red (#ff4444): Error/Unavailable/Offline
  - Gray (#666666): Unknown/Disabled

### Animated Background Features
- **Starfield Animation:** 20+ individual stars moving horizontally across the screen (120s cycle)
- **Nebula Effects:** Slowly rotating and scaling colored gas clouds with transparency
- **Performance Optimized:** CSS-only animations with low CPU usage
- **Subtle Opacity:** Background effects don't interfere with text readability
- **Color Harmony:** Nebula colors match the interface accent colors (blue, green, orange)

### Interactive Elements
- **🔄 Refresh Buttons** for manual updates
- **📊 Progress Bars** for data quality
- **🏷️ API Status Badges**
- **📋 Scrollable Log Terminal**

## 🛠️ Technical Details

### Backend (Flask)
- **🐍 Python Flask** web framework
- **📊 Real-time Data Collection** from system components
- **💾 Intelligent Caching** (30-second intervals)
- **🔄 RESTful API Endpoints:**
  - `/api/status` - System status JSON
  - `/api/logs` - Live logs JSON
  - `/api/refresh` - Force cache refresh

### Frontend (HTML/CSS/JavaScript)
- **📱 Responsive Design** with CSS Grid
- **⚡ Vanilla JavaScript** (no dependencies)
- **🔄 Asynchronous Updates** using Fetch API
- **🎨 Advanced CSS Animations** for starfield and nebula effects
- **🌌 Multiple Animation Layers** for depth and realism

### Animation Performance
- **CSS-only Animations** (no JavaScript animation loops)
- **Hardware Acceleration** using transform properties
- **Low CPU Usage** optimized for continuous operation
- **Smooth 60fps** animation on modern browsers
- **Responsive Scaling** adapts to different screen sizes

### Performance
- **⚡ Fast Loading** with optimized data queries
- **💾 Smart Caching** reduces system load
- **📊 Efficient Polling** every 30 seconds
- **🔄 Background Processing** for data collection

## 📋 API Endpoints

### GET /api/status
Returns comprehensive system status:
```json
{
  "system_health": {...},
  "data_statistics": {...},
  "error_summary": {...},
  "api_status": {...},
  "ai_status": {...},
  "recent_activity": {...}
}
```

### GET /api/logs?lines=N
Returns formatted log entries:
```json
{
  "logs": ["<span class='log-info'>...</span>"],
  "timestamp": "2025-06-18T10:01:43.188006"
}
```

### GET /api/refresh
Forces immediate cache refresh:
```json
{
  "status": "refreshed",
  "timestamp": "2025-06-18T10:01:43.188006"
}
```

## 🔧 Configuration

### Port Configuration
- **Default Port:** 8080 (avoids macOS AirPlay conflict)
- **Host:** 0.0.0.0 (accessible from network)
- **Protocol:** HTTP (local development)

### Animation Settings
- **Starfield Speed:** 120s per cycle (adjustable in CSS)
- **Nebula Rotation:** 180s per cycle (adjustable in CSS)
- **Star Opacity:** 0.3 (adjustable in CSS)
- **Nebula Opacity:** 0.4-0.6 (animated)

### Customization
- **Log Lines:** Configurable via `?lines=N` parameter
- **Refresh Interval:** Modifiable in JavaScript (default: 30s)
- **Cache Duration:** Adjustable in Python backend (default: 30s)
- **Animation Speed:** Modifiable in CSS keyframes

## 🚨 Troubleshooting

### Common Issues

**Dashboard won't start:**
```bash
# Check if port 8080 is available
lsof -i :8080

# Kill existing process if needed
kill -9 $(lsof -t -i:8080)
```

**No data showing:**
- Ensure `logs/` directory exists
- Check `Data/` directory structure
- Verify file permissions

**Animation performance issues:**
- Check browser hardware acceleration settings
- Disable animations by commenting out CSS keyframes if needed
- Use Chrome/Firefox for best performance

**Browser won't open:**
- Manually navigate to http://localhost:8080
- Check firewall settings
- Ensure Flask server is running

### Debug Mode
```bash
# Run with debug output
python web_dashboard.py
```

## 🔮 Future Enhancements

- **🔐 Authentication** system
- **📊 Historical Data** charts and graphs
- **🔔 Real-time Notifications** for critical events
- **📱 Mobile App** companion
- **🌐 Multi-language Support**
- **📈 Performance Metrics** dashboard
- **🔄 WebSocket** real-time updates
- **📊 Data Export** functionality
- **🌌 Additional Background Themes** (asteroid fields, planetary views)
- **🎵 Ambient Space Sounds** (optional)

## 🤝 Integration

The dashboard integrates seamlessly with:
- **🤖 AI Assistant** system
- **📊 Delta Update Manager**
- **🛰️ Satellite Tracking** system
- **📝 Logging Infrastructure**
- **🔄 Automation Scripts**

---

**Created:** June 2025  
**Last Updated:** June 18, 2025  
**Version:** 2.0.0 - SGU Edition with Animated Starfield 
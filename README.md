# UART 通信助手 Pro (UART Assistant Pro)

<div align="center">

![Version](https://img.shields.io/badge/version-1.0.0-blue.svg)
![License](https://img.shields.io/badge/license-MIT-green.svg)
![Python](https://img.shields.io/badge/python-3.8%2B-yellow.svg)
![Frontend](https://img.shields.io/badge/frontend-HTML5%2FJS-orange.svg)

**一个极简、炫酷且功能强大的 Web 版串口调试助手**

[English](README_EN.md) | [简体中文](README.md)

</div>

---

## ✨ 简介 (Introduction)

**UART 通信助手 Pro** 是一款基于 Python (aiohttp) 和现代 Web 技术构建的跨平台串口调试工具。它不仅具备传统串口助手的所有功能，还引入了现代化的 UI 设计、实时数据可视化统计、协议构建器以及专为物联网 (IoT) 开发设计的传感器仪表盘。

无论是嵌入式开发、硬件调试，还是物联网教学演示，它都能提供极致流畅的体验。

## 🚀 核心特性 (Features)

### 🎨 现代化 UI/UX
*   **极致美学**：采用 Apple San Francisco 字体栈，搭配毛玻璃效果与流畅动画，提供原生应用般的视觉体验。
*   **多主题切换**：内置 Apple Gray, Sakura, Mint, Ocean 等 12 种精美配色方案，随心切换。
*   **响应式布局**：完美适配各种屏幕尺寸，支持分栏视图。

### 🔌 强大的串口通信
*   **全参数配置**：支持波特率、数据位 (5-8)、停止位 (1/1.5/2)、校验位 (None/Odd/Even/Mark/Space) 及流控 (RTS/CTS, XON/XOFF)。
*   **多编码支持**：实时切换 UTF-8, GBK, ASCII, Latin-1 编码，彻底告别乱码。
*   **智能分包**：支持自定义帧头/帧尾分割 HEX 数据包，让数据流一目了然。

### 🛠 专业调试工具
*   **协议构建器**：内置 TX 构建器，自动计算校验和 (SUM/XOR/CRC8)，支持自定义帧头、功能码、序列号。
*   **快捷指令库**：支持添加、编辑、导入/导出常用指令，支持绑定键盘快捷键 (F1-F12)。
*   **循环发送**：支持毫秒级精度的自动循环发送。

### 📊 数据可视化
*   **实时统计**：实时监控 RX/TX 字节数、包数及传输速率。
*   **流量图表**：内置 Chart.js 绘制的实时流量占比环形图。
*   **IoT 仪表盘**：专为演示设计的传感器仪表盘，支持：
    *   **ADC 传感器**：动态进度条显示声音、湿度、压力等数值。
    *   **IIC 数码管**：模拟真实数码管显示效果。
    *   **GPIO 控制**：交互式 LED 开关与状态回传指示灯。

### 📝 智能日志系统
*   **炫酷日志视图**：极客风格的日志打印，区分 RX/TX/System/Error 消息类型。
*   **双向同步**：系统消息与错误信息同时同步至发送与接收窗口，不错过任何关键状态。
*   **精确时间戳**：毫秒级时间戳记录，完美对齐。

## 📸 截图预览 (Screenshots)

### 通信终端 (Terminal)
> 极简的左右分栏设计，左侧配置与快捷指令，右侧日志与发送控制。
*(在此处插入截图)*

### 数据统计 (Statistics)
> 实时监控通信流量与速率。
*(在此处插入截图)*

### 传感器仪表盘 (IoT Dashboard)
> 交互式的传感器数据可视化面板。
*(在此处插入截图)*

## 🛠 安装与运行 (Installation)

### 环境要求
*   Python 3.8+
*   现代浏览器 (Chrome, Edge, Firefox, Safari)

### 1. 克隆仓库
```bash
git clone https://github.com/yourusername/uart-assistant-pro.git
cd uart-assistant-pro
```

### 2. 安装依赖
```bash
pip install -r requirements.txt
```
> *如果没有 requirements.txt，请安装以下库：*
> `pip install aiohttp pyserial`

### 3. 运行程序
```bash
python app.py
```

### 4. 访问应用
打开浏览器访问：
`http://localhost:8080` (默认端口)

## 📖 使用指南 (Usage)

1.  **连接设备**：在左侧选择串口号（支持自动刷新），配置波特率等参数，点击“连接设备”。
2.  **发送数据**：
    *   **基本发送**：在右侧输入框输入内容，支持 HEX 发送与自动换行。
    *   **协议发送**：切换到“协议传输” Tab，配置地址、功能码与数据，自动生成带校验的协议帧。
3.  **查看数据**：
    *   **HEX 查看**：勾选右上角“HEX 查看”。
    *   **分包设置**：点击⚙️图标，设置帧头帧尾（如 `7B` ... `7D`），实现自动分包显示。
4.  **仪表盘演示**：
    *   发送 `SENSOR:45,60,1024` 格式数据更新 ADC 图表。
    *   发送 `LED:ON` 或 `LED:OFF` 控制开关状态。

## 🤝 贡献 (Contributing)

欢迎提交 Issue 和 Pull Request！如果你有好的想法，请随时分享。

## 📄 许可证 (License)

本项目采用 MIT 许可证。详情请参阅 [LICENSE](LICENSE) 文件。

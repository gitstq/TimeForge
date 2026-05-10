<!-- 
  TimeForge README - 多语言版本
  Languages: 简体中文, 繁體中文, English
-->

<p align="center">
  <img src="https://img.shields.io/badge/version-1.0.0-blue.svg" alt="Version">
  <img src="https://img.shields.io/badge/python-3.8+-green.svg" alt="Python">
  <img src="https://img.shields.io/badge/license-MIT-orange.svg" alt="License">
  <img src="https://img.shields.io/badge/platform-Windows%20%7C%20macOS%20%7C%20Linux-lightgrey.svg" alt="Platform">
</p>

<p align="center">
  <a href="#简体中文">简体中文</a> | 
  <a href="#繁體中文">繁體中文</a> | 
  <a href="#english">English</a>
</p>

---

<h1 id="简体中文" align="center">⏰ TimeForge</h1>

<p align="center">
  <strong>功能强大的终端时间管理工具</strong>
</p>

<p align="center">
  倒计时 · 秒表 · 番茄钟 · 统计分析
</p>

---

## 🎉 项目介绍

**TimeForge** 是一款专为开发者和终端用户设计的轻量级时间管理工具。它提供了倒计时、秒表、番茄钟三种核心功能，帮助你更好地管理时间、提升工作效率。

### 💡 为什么选择 TimeForge？

- 🚀 **零配置启动** - 安装后即可使用，无需复杂配置
- 🎨 **精美终端界面** - 基于 Rich 库的现代化终端UI
- ⌨️ **灵活的时间输入** - 支持多种时间格式（10m、1h30m、5:00等）
- 📊 **完整的统计功能** - 记录你的时间使用情况
- 🔔 **跨平台声音提示** - 支持 Windows、macOS、Linux
- 🍅 **专业番茄钟** - 可自定义工作和休息时间

### 🌟 自研差异化亮点

本项目参考了 [termdown](https://github.com/trehn/termdown) 的产品思路，但进行了全面的独立自研开发，主要差异化特性包括：

| 特性 | TimeForge | termdown |
|------|-----------|----------|
| 番茄钟模式 | ✅ 内置完整番茄钟 | ❌ 需要额外配置 |
| 统计分析 | ✅ 完整统计系统 | ❌ 无统计功能 |
| 会话记录 | ✅ 自动保存历史 | ❌ 无历史记录 |
| 模块化架构 | ✅ 可扩展API | ⚠️ 单文件结构 |
| 多种时间格式 | ✅ 更灵活的解析 | ⚠️ 基础格式 |

---

## ✨ 核心特性

### ⏳ 倒计时模式

- 支持多种时间输入格式
- 实时进度条显示
- 完成时声音提醒

### ⏱️ 秒表模式

- 精确计时
- 支持圈数记录
- 暂停/恢复功能

### 🍅 番茄钟模式

- 可自定义工作/休息时间
- 自动切换工作和休息
- 统计完成的番茄数

### 📊 统计分析

- 总使用时长统计
- 按类型分类统计
- 连续使用天数追踪

---

## 🚀 快速开始

### 环境要求

- Python 3.8 或更高版本
- 支持 Windows、macOS、Linux

### 安装

```bash
# 使用 pip 安装
pip install timeforge

# 或从源码安装
git clone https://github.com/gitstq/TimeForge.git
cd TimeForge
pip install -e .
```

### 基本使用

```bash
# 10分钟倒计时
timeforge countdown 10m

# 1小时30分钟倒计时
timeforge countdown 1h30m

# 使用冒号格式
timeforge countdown 5:00

# 启动秒表
timeforge stopwatch

# 启动番茄钟（默认25分钟工作）
timeforge pomodoro

# 自定义番茄钟（30分钟工作）
timeforge pomodoro -w 30

# 查看统计
timeforge stats

# 查看配置
timeforge config
```

---

## 📖 详细使用指南

### 时间格式支持

TimeForge 支持多种时间输入格式：

| 格式 | 示例 | 说明 |
|------|------|------|
| 纯数字 | `90` | 默认为秒 |
| 秒 | `30s`, `90s` | 秒数 |
| 分钟 | `5m`, `10m` | 分钟数 |
| 小时 | `1h`, `2h` | 小时数 |
| 组合 | `1h30m`, `1h30m30s` | 组合时间 |
| 冒号 | `5:00`, `1:30:00` | MM:SS 或 HH:MM:SS |

### 番茄钟配置

```bash
# 设置工作时间为30分钟
timeforge config -w 30

# 设置短休息为10分钟
timeforge config -s 10

# 设置长休息为20分钟
timeforge config -l 20

# 禁用声音
timeforge config --sound false
```

### 键盘快捷键

| 按键 | 功能 |
|------|------|
| `Ctrl+C` | 停止当前计时器 |
| `p` | 暂停/恢复（开发中） |
| `l` | 记录圈数（秒表模式） |

---

## 💡 设计思路与迭代规划

### 设计理念

TimeForge 采用模块化架构设计，核心组件包括：

- **核心模块 (core.py)** - 基础数据结构和工具类
- **计时器模块 (timer.py)** - 各种计时器实现
- **显示模块 (display.py)** - 终端UI渲染
- **声音模块 (sound.py)** - 跨平台声音提示
- **统计模块 (stats.py)** - 数据统计分析

### 后续迭代计划

- [ ] Web Dashboard 统计面板
- [ ] 自定义主题支持
- [ ] 任务关联功能
- [ ] 云同步支持
- [ ] 更多声音选项

---

## 📦 打包与部署指南

### 从源码构建

```bash
# 克隆仓库
git clone https://github.com/gitstq/TimeForge.git
cd TimeForge

# 安装开发依赖
pip install -e ".[dev]"

# 运行测试
pytest

# 构建分发包
pip install build
python -m build
```

### 打包可执行文件

```bash
# 使用 PyInstaller
pip install pyinstaller
pyinstaller --onefile --name timeforge timeforge/cli.py
```

---

## 🤝 贡献指南

欢迎所有形式的贡献！

1. Fork 本仓库
2. 创建功能分支 (`git checkout -b feature/AmazingFeature`)
3. 提交更改 (`git commit -m 'feat: 添加某个功能'`)
4. 推送到分支 (`git push origin feature/AmazingFeature`)
5. 创建 Pull Request

### 提交规范

- `feat:` 新功能
- `fix:` 修复问题
- `docs:` 文档更新
- `refactor:` 代码重构
- `test:` 测试相关

---

## 📄 开源协议

本项目采用 [MIT](LICENSE) 协议开源。

---

<p align="center">
  Made with ❤️ by TimeForge Team
</p>

---

<h1 id="繁體中文" align="center">⏰ TimeForge</h1>

<p align="center">
  <strong>功能強大的終端時間管理工具</strong>
</p>

<p align="center">
  倒數計時 · 碼錶 · 番茄鐘 · 統計分析
</p>

---

## 🎉 專案介紹

**TimeForge** 是一款專為開發者和終端用戶設計的輕量級時間管理工具。它提供了倒數計時、碼錶、番茄鐘三種核心功能，幫助你更好地管理時間、提升工作效率。

### 💡 為什麼選擇 TimeForge？

- 🚀 **零配置啟動** - 安裝後即可使用，無需複雜配置
- 🎨 **精美終端界面** - 基於 Rich 庫的現代化終端UI
- ⌨️ **靈活的時間輸入** - 支援多種時間格式（10m、1h30m、5:00等）
- 📊 **完整的統計功能** - 記錄你的時間使用情況
- 🔔 **跨平台聲音提示** - 支援 Windows、macOS、Linux
- 🍅 **專業番茄鐘** - 可自定義工作和休息時間

---

## ✨ 核心特性

### ⏳ 倒數計時模式
- 支援多種時間輸入格式
- 即時進度條顯示
- 完成時聲音提醒

### ⏱️ 碼錶模式
- 精確計時
- 支援圈數記錄
- 暫停/恢復功能

### 🍅 番茄鐘模式
- 可自定義工作/休息時間
- 自動切換工作和休息
- 統計完成的番茄數

### 📊 統計分析
- 總使用時長統計
- 按類型分類統計
- 連續使用天數追蹤

---

## 🚀 快速開始

### 環境要求

- Python 3.8 或更高版本
- 支援 Windows、macOS、Linux

### 安裝

```bash
# 使用 pip 安裝
pip install timeforge

# 或從源碼安裝
git clone https://github.com/gitstq/TimeForge.git
cd TimeForge
pip install -e .
```

### 基本使用

```bash
# 10分鐘倒數計時
timeforge countdown 10m

# 1小時30分鐘倒數計時
timeforge countdown 1h30m

# 啟動碼錶
timeforge stopwatch

# 啟動番茄鐘
timeforge pomodoro

# 查看統計
timeforge stats
```

---

## 📄 開源協議

本專案採用 [MIT](LICENSE) 協議開源。

---

<h1 id="english" align="center">⏰ TimeForge</h1>

<p align="center">
  <strong>A Powerful Terminal Time Management Tool</strong>
</p>

<p align="center">
  Countdown · Stopwatch · Pomodoro · Statistics
</p>

---

## 🎉 Introduction

**TimeForge** is a lightweight time management tool designed for developers and terminal users. It provides three core features: countdown timer, stopwatch, and pomodoro timer, helping you manage your time better and boost productivity.

### 💡 Why Choose TimeForge?

- 🚀 **Zero Configuration** - Ready to use after installation
- 🎨 **Beautiful Terminal UI** - Modern terminal interface based on Rich library
- ⌨️ **Flexible Time Input** - Support multiple time formats (10m, 1h30m, 5:00, etc.)
- 📊 **Complete Statistics** - Track your time usage
- 🔔 **Cross-platform Sound** - Support Windows, macOS, Linux
- 🍅 **Professional Pomodoro** - Customizable work and break times

### 🌟 Differentiated Features

This project was inspired by [termdown](https://github.com/trehn/termdown) but developed independently with these unique features:

| Feature | TimeForge | termdown |
|---------|-----------|----------|
| Pomodoro Mode | ✅ Built-in | ❌ Requires config |
| Statistics | ✅ Complete system | ❌ None |
| Session History | ✅ Auto-save | ❌ None |
| Modular Architecture | ✅ Extensible API | ⚠️ Single file |
| Time Formats | ✅ More flexible | ⚠️ Basic |

---

## ✨ Core Features

### ⏳ Countdown Mode
- Multiple time input formats
- Real-time progress bar
- Sound notification on completion

### ⏱️ Stopwatch Mode
- Precise timing
- Lap recording support
- Pause/Resume functionality

### 🍅 Pomodoro Mode
- Customizable work/break times
- Auto-switch between work and break
- Track completed pomodoros

### 📊 Statistics
- Total usage time tracking
- Statistics by type
- Streak tracking

---

## 🚀 Quick Start

### Requirements

- Python 3.8 or higher
- Windows, macOS, or Linux

### Installation

```bash
# Install with pip
pip install timeforge

# Or install from source
git clone https://github.com/gitstq/TimeForge.git
cd TimeForge
pip install -e .
```

### Basic Usage

```bash
# 10 minute countdown
timeforge countdown 10m

# 1 hour 30 minutes countdown
timeforge countdown 1h30m

# Start stopwatch
timeforge stopwatch

# Start pomodoro (default 25 min work)
timeforge pomodoro

# Custom pomodoro (30 min work)
timeforge pomodoro -w 30

# View statistics
timeforge stats

# View config
timeforge config
```

---

## 📖 Detailed Usage

### Time Format Support

TimeForge supports multiple time input formats:

| Format | Example | Description |
|--------|---------|-------------|
| Number | `90` | Default: seconds |
| Seconds | `30s`, `90s` | Seconds |
| Minutes | `5m`, `10m` | Minutes |
| Hours | `1h`, `2h` | Hours |
| Combined | `1h30m`, `1h30m30s` | Combined time |
| Colon | `5:00`, `1:30:00` | MM:SS or HH:MM:SS |

### Pomodoro Configuration

```bash
# Set work time to 30 minutes
timeforge config -w 30

# Set short break to 10 minutes
timeforge config -s 10

# Set long break to 20 minutes
timeforge config -l 20

# Disable sound
timeforge config --sound false
```

---

## 💡 Design & Roadmap

### Architecture

TimeForge uses a modular architecture:

- **Core Module (core.py)** - Base data structures and utilities
- **Timer Module (timer.py)** - Timer implementations
- **Display Module (display.py)** - Terminal UI rendering
- **Sound Module (sound.py)** - Cross-platform sound
- **Stats Module (stats.py)** - Data analysis

### Roadmap

- [ ] Web Dashboard
- [ ] Custom themes
- [ ] Task association
- [ ] Cloud sync
- [ ] More sound options

---

## 📦 Build & Deploy

### Build from Source

```bash
# Clone repository
git clone https://github.com/gitstq/TimeForge.git
cd TimeForge

# Install dev dependencies
pip install -e ".[dev]"

# Run tests
pytest

# Build distribution
pip install build
python -m build
```

### Build Executable

```bash
pip install pyinstaller
pyinstaller --onefile --name timeforge timeforge/cli.py
```

---

## 🤝 Contributing

Contributions are welcome!

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'feat: add some feature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

### Commit Convention

- `feat:` New feature
- `fix:` Bug fix
- `docs:` Documentation
- `refactor:` Code refactoring
- `test:` Tests

---

## 📄 License

This project is licensed under the [MIT](LICENSE) License.

---

<p align="center">
  Made with ❤️ by TimeForge Team
</p>

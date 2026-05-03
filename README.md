<p align="center">
  <a href="#简体中文">简体中文</a> |
  <a href="#繁體中文">繁體中文</a> |
  <a href="#english">English</a>
</p>

---

<!-- lang:zh-CN -->

# 简体中文

<div id="简体中文"></div>

<p align="center">
  <strong>TimeForge</strong> — 轻量级终端时间追踪与生产力分析工具
</p>

<p align="center">
  <img src="https://img.shields.io/badge/Python-3.8+-blue.svg" alt="Python 3.8+">
  <img src="https://img.shields.io/badge/License-MIT-green.svg" alt="MIT License">
  <img src="https://img.shields.io/badge/Dependencies-0-red.svg" alt="Zero Dependencies">
</p>

---

## 🎉 项目介绍

**TimeForge** 是一款专为开发者打造的轻量级终端时间追踪与生产力分析 CLI 工具。它用纯 Python 实现，**零外部依赖**，开箱即用。

### 为什么做 TimeForge？

在日常开发工作中，你是否也遇到过这些问题：

- **时间黑洞**：一天下来不知道时间花在了哪里
- **工具臃肿**：现有时间追踪工具要么太重、要么太贵、要么需要联网
- **数据孤岛**：时间数据与代码提交（Git commit）脱节，无法关联分析
- **效率盲区**：缺乏对自身工作模式和效率的量化认知

TimeForge 正是为了解决这些痛点而生。灵感来源于对**高效时间管理**的追求——我们相信，好的时间管理工具应该像一把精准的手术刀，而不是一把瑞士军刀。

### 差异化亮点

| 特性 | TimeForge | 其他工具 |
|------|-----------|----------|
| 外部依赖 | **零依赖** | 通常需要 Node.js、数据库等 |
| 数据存储 | **本地 JSON** | 云端存储，隐私风险 |
| 番茄钟 | **内置** | 需要额外安装插件 |
| Git 关联 | **自动关联 commit** | 不支持或需手动操作 |
| 报告格式 | **4 种格式导出** | 通常仅 1-2 种 |
| 生产力分析 | **内置智能分析** | 需付费升级 |

---

## ✨ 核心特性

### ⏱️ 精准时间追踪

完整的计时生命周期管理，支持开始、停止、暂停、继续、查看状态、查看日志、列表、删除和编辑：

```bash
# 开始追踪一个任务
timeforge start "修复登录页 Bug" --project "web-app"

# 暂停当前任务
timeforge pause

# 继续暂停的任务
timeforge resume

# 停止当前任务
timeforge stop

# 查看当前状态
timeforge status

# 查看今日日志
timeforge log --today

# 查看所有记录
timeforge list

# 删除一条记录
timeforge delete <id>

# 编辑一条记录
timeforge edit <id> --project "mobile-app" --description "优化首页加载速度"
```

### 🍅 内置番茄钟

可配置工作/休息时长，终端实时进度条显示：

```bash
# 启动 25 分钟番茄钟（默认）
timeforge pomodoro start

# 自定义工作时长 50 分钟，休息 10 分钟
timeforge pomodoro start --work 50 --break 10

# 查看番茄钟状态
timeforge pomodoro status

# 停止番茄钟
timeforge pomodoro stop
```

### 📊 多格式报告

支持 **JSON / CSV / HTML / Markdown** 四种格式导出：

```bash
# 生成 JSON 报告
timeforge report --format json --output report.json

# 生成 CSV 报告
timeforge report --format csv --output report.csv

# 生成 HTML 报告（可在浏览器中查看）
timeforge report --format html --output report.html

# 生成 Markdown 报告
timeforge report --format markdown --output report.md
```

### 🧠 智能生产力分析

深入洞察你的工作模式，包含效率评分、连续工作天数（streak）和智能建议：

```bash
# 查看生产力分析报告
timeforge analyze

# 查看指定时间范围的分析
timeforge analyze --from 2025-01-01 --to 2025-01-31

# 查看项目时间分布
timeforge analyze --by project
```

分析内容包括：

- **项目时间分布**：各项目耗时占比可视化
- **效率评分**：基于工作模式计算综合效率分
- **连续天数 Streak**：激励你保持每日记录习惯
- **智能建议**：根据数据自动生成优化建议

### 🔗 Git 集成

自动关联 Git commit 到时间记录，让代码变更与时间投入一目了然：

```bash
# 在 Git 仓库中启动追踪（自动关联当前分支和最新 commit）
timeforge start "开发新功能" --project "backend" --git

# 查看带 Git 信息的记录
timeforge log --git
```

### 🎨 美观终端界面

丰富的终端显示能力，让命令行也能赏心悦目：

- **ANSI 彩色输出**：不同状态、不同项目使用不同颜色区分
- **表格展示**：记录列表以整齐的表格形式呈现
- **进度条**：番茄钟和计时器实时显示进度
- **柱状图**：分析结果以终端柱状图可视化

### 📦 零外部依赖

纯 Python 3.8+ 实现，无需安装任何第三方库：

```
pip install timeforge
# 完成！无需 pip install 其他任何东西
```

### 💾 本地数据存储

所有数据以 JSON 格式存储在本地，数据完全自主可控：

```
~/.timeforge/
├── records.json      # 时间记录
├── config.json       # 用户配置
└── pomodoro.json     # 番茄钟状态
```

---

## 🚀 快速开始

### 环境要求

- **Python 3.8** 或更高版本

### 安装

```bash
# 从 PyPI 安装
pip install timeforge

# 或从 GitHub 安装最新版本
pip install git+https://github.com/gitstq/TimeForge.git
```

### 快速使用

```bash
# 1. 开始追踪一个任务
timeforge start "编写项目文档" --project "docs"

# 2. 查看当前状态
timeforge status

# 3. 停止任务
timeforge stop

# 4. 查看今日日志
timeforge log --today

# 5. 生成 HTML 报告
timeforge report --format html --output weekly_report.html

# 6. 查看生产力分析
timeforge analyze
```

五分钟上手，从此掌控你的时间。

---

## 📖 详细使用指南

### 时间追踪进阶用法

```bash
# 带标签的追踪
timeforge start "代码审查" --project "review" --tags "urgent,frontend"

# 追溯添加记录（补充之前忘记记录的任务）
timeforge start "紧急修复" --project "hotfix" --at "2025-01-15 09:30"

# 按日期范围查看日志
timeforge log --from 2025-01-01 --to 2025-01-31

# 按项目筛选日志
timeforge log --project "web-app"

# 按标签筛选日志
timeforge log --tags "urgent"
```

### 番茄钟使用

```bash
# 启动标准番茄钟（25 分钟工作 / 5 分钟休息）
timeforge pomodoro start

# 长休息模式（25 分钟工作 / 15 分钟休息）
timeforge pomodoro start --long-break

# 自定义时长
timeforge pomodoro start --work 45 --break 10 --long-break-duration 20

# 查看今日番茄钟统计
timeforge pomodoro stats

# 连续番茄钟模式（自动开始下一轮）
timeforge pomodoro start --auto
```

### 报告生成示例

```bash
# 本周报告
timeforge report --format html --output week.html --period week

# 本月报告
timeforge report --format markdown --output month.md --period month

# 自定义日期范围报告
timeforge report --format csv --output q1.csv --from 2025-01-01 --to 2025-03-31

# 按项目汇总的报告
timeforge report --format json --output summary.json --group-by project
```

### 分析功能说明

```bash
# 综合分析（默认显示本周数据）
timeforge analyze

# 按日分析
timeforge analyze --by day

# 按项目分析
timeforge analyze --by project

# 按标签分析
timeforge analyze --by tag

# 指定时间范围
timeforge analyze --from 2025-01-01 --to 2025-12-31
```

**分析输出示例：**

```
📊 生产力分析报告
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
📅 分析周期: 2025-01-01 ~ 2025-01-31

⏱️ 总计时长: 156h 30m
🔥 连续天数: 22 天
📈 效率评分: 87/100

📋 项目分布:
  web-app    ████████████████░░░░  65%  (101h 42m)
  backend    ██████░░░░░░░░░░░░░░  25%  (39h 08m)
  docs       ███░░░░░░░░░░░░░░░░░  10%  (15h 40m)

💡 智能建议:
  • 你在上午 9:00-11:30 效率最高，建议将重要任务安排在此时段
  • web-app 项目占比过高，建议合理分配时间
  • 周三产出最低，可以考虑安排为学习或整理日
```

### Git 关联使用

```bash
# 自动关联（在 Git 仓库目录内）
timeforge start "开发 API 接口" --project "backend" --git

# 停止时自动记录当前 commit hash
timeforge stop

# 查看带 Git 信息的日志
timeforge log --git

# 生成包含 Git 信息的报告
timeforge report --format html --output report.html --git
```

### 配置管理

```bash
# 查看当前配置
timeforge config

# 设置默认项目
timeforge config set default_project "my-project"

# 设置番茄钟默认工作时长
timeforge config set pomodoro_work 50

# 设置数据存储路径
timeforge config set data_dir "/path/to/custom/dir"

# 重置配置
timeforge config reset
```

---

## 💡 设计思路与迭代规划

### 设计理念

| 理念 | 说明 |
|------|------|
| **简洁高效** | 每个命令都经过精心设计，最少按键完成最多操作 |
| **数据自主** | 所有数据本地存储，不依赖任何云服务，隐私完全可控 |
| **开发者友好** | 终端原生体验，与 Git 等开发工具无缝集成 |

### 技术选型原因

- **纯 Python**：降低入门门槛，跨平台兼容性好
- **零外部依赖**：安装即用，不引入版本冲突风险
- **JSON 存储**：人类可读，便于备份和迁移
- **CLI 界面**：开发者最熟悉的工作环境，无需切换上下文

### 后续计划

| 阶段 | 计划内容 | 状态 |
|------|----------|------|
| v1.0 | 核心时间追踪 + 番茄钟 + 报告 | ✅ 已完成 |
| v1.1 | Git 集成 + 生产力分析 | ✅ 已完成 |
| v2.0 | Web 仪表盘（本地可视化面板） | 🔄 规划中 |
| v2.1 | 团队协作（共享项目时间统计） | 📋 计划中 |
| v2.5 | 数据导入导出（支持 Toggl/Clockify 格式） | 📋 计划中 |
| v3.0 | 插件系统（支持自定义扩展） | 💡 构想中 |

---

## 📦 安装与部署指南

### 从 PyPI 安装（推荐）

```bash
pip install timeforge
```

### 从源码安装

```bash
# 克隆仓库
git clone https://github.com/gitstq/TimeForge.git
cd TimeForge

# 安装
pip install .
```

### 开发模式安装

```bash
# 克隆仓库
git clone https://github.com/gitstq/TimeForge.git
cd TimeForge

# 以开发模式安装（修改源码后立即生效）
pip install -e .
```

### 验证安装

```bash
timeforge --version
timeforge --help
```

---

## 🤝 贡献指南

我们欢迎并感谢所有形式的贡献！无论是提交 Bug、改进文档，还是提交代码。

### 提交 PR 规范

1. **Fork** 本仓库
2. 创建特性分支：`git checkout -b feature/your-feature-name`
3. 提交更改：`git commit -m "feat: 添加你的功能描述"`
4. 推送分支：`git push origin feature/your-feature-name`
5. 提交 **Pull Request**

**Commit 消息规范：**

| 类型 | 说明 |
|------|------|
| `feat:` | 新功能 |
| `fix:` | 修复 Bug |
| `docs:` | 文档更新 |
| `style:` | 代码格式调整（不影响逻辑） |
| `refactor:` | 代码重构 |
| `test:` | 测试相关 |
| `chore:` | 构建/工具链相关 |

### Issue 规则

- 提交 Bug 前，请先搜索是否已有相同 Issue
- Bug 报告请包含：复现步骤、期望行为、实际行为、运行环境
- 功能建议请描述使用场景和预期效果

---

## 📄 开源协议

本项目基于 [MIT License](https://opensource.org/licenses/MIT) 开源。

```
MIT License

Copyright (c) 2025 TimeForge Contributors

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
```

---

<p align="center">
  用 <strong>TimeForge</strong> 锻造你的时间，让每一分钟都有价值 ⏱️
</p>

---

<!-- lang:zh-TW -->

# 繁體中文

<div id="繁體中文"></div>

<p align="center">
  <strong>TimeForge</strong> — 輕量級終端時間追蹤與生產力分析工具
</p>

<p align="center">
  <img src="https://img.shields.io/badge/Python-3.8+-blue.svg" alt="Python 3.8+">
  <img src="https://img.shields.io/badge/License-MIT-green.svg" alt="MIT License">
  <img src="https://img.shields.io/badge/Dependencies-0-red.svg" alt="Zero Dependencies">
</p>

---

## 🎉 專案介紹

**TimeForge** 是一款專為開發者打造的輕量級終端時間追蹤與生產力分析 CLI 工具。它用純 Python 實現，**零外部依賴**，開箱即用。

### 為什麼要做 TimeForge？

在日常開發工作中，你是否也遇到過這些問題：

- **時間黑洞**：一天下來不知道時間花在了哪裡
- **工具臃腫**：現有時間追蹤工具要麼太重、要麼太貴、要麼需要連網
- **資料孤島**：時間資料與程式碼提交（Git commit）脫節，無法關聯分析
- **效率盲區**：缺乏對自身工作模式和效率的量化認知

TimeForge 正是為了解決這些痛點而生。靈感來源於對**高效時間管理**的追求——我們相信，好的時間管理工具應該像一把精準的手術刀，而不是一把瑞士軍刀。

### 差異化亮點

| 特性 | TimeForge | 其他工具 |
|------|-----------|----------|
| 外部依賴 | **零依賴** | 通常需要 Node.js、資料庫等 |
| 資料儲存 | **本地 JSON** | 雲端儲存，隱私風險 |
| 番茄鐘 | **內建** | 需要額外安裝外掛 |
| Git 關聯 | **自動關聯 commit** | 不支援或需手動操作 |
| 報告格式 | **4 種格式匯出** | 通常僅 1-2 種 |
| 生產力分析 | **內建智慧分析** | 需付費升級 |

---

## ✨ 核心特性

### ⏱️ 精準時間追蹤

完整的計時生命週期管理，支援開始、停止、暫停、繼續、查看狀態、查看日誌、列表、刪除和編輯：

```bash
# 開始追蹤一個任務
timeforge start "修復登入頁 Bug" --project "web-app"

# 暫停當前任務
timeforge pause

# 繼續暫停的任務
timeforge resume

# 停止當前任務
timeforge stop

# 查看當前狀態
timeforge status

# 查看今日日誌
timeforge log --today

# 查看所有記錄
timeforge list

# 刪除一條記錄
timeforge delete <id>

# 編輯一條記錄
timeforge edit <id> --project "mobile-app" --description "優化首頁載入速度"
```

### 🍅 內建番茄鐘

可配置工作/休息時長，終端即時進度條顯示：

```bash
# 啟動 25 分鐘番茄鐘（預設）
timeforge pomodoro start

# 自訂工作時長 50 分鐘，休息 10 分鐘
timeforge pomodoro start --work 50 --break 10

# 查看番茄鐘狀態
timeforge pomodoro status

# 停止番茄鐘
timeforge pomodoro stop
```

### 📊 多格式報告

支援 **JSON / CSV / HTML / Markdown** 四種格式匯出：

```bash
# 產生 JSON 報告
timeforge report --format json --output report.json

# 產生 CSV 報告
timeforge report --format csv --output report.csv

# 產生 HTML 報告（可在瀏覽器中查看）
timeforge report --format html --output report.html

# 產生 Markdown 報告
timeforge report --format markdown --output report.md
```

### 🧠 智慧生產力分析

深入洞察你的工作模式，包含效率評分、連續工作天數（streak）和智慧建議：

```bash
# 查看生產力分析報告
timeforge analyze

# 查看指定時間範圍的分析
timeforge analyze --from 2025-01-01 --to 2025-01-31

# 查看專案時間分佈
timeforge analyze --by project
```

分析內容包括：

- **專案時間分佈**：各專案耗時佔比視覺化
- **效率評分**：基於工作模式計算綜合效率分
- **連續天數 Streak**：激勵你保持每日記錄習慣
- **智慧建議**：根據資料自動產生最佳化建議

### 🔗 Git 整合

自動關聯 Git commit 到時間記錄，讓程式碼變更與時間投入一目瞭然：

```bash
# 在 Git 倉庫中啟動追蹤（自動關聯當前分支和最新 commit）
timeforge start "開發新功能" --project "backend" --git

# 查看帶 Git 資訊的記錄
timeforge log --git
```

### 🎨 美觀終端介面

豐富的終端顯示能力，讓命令列也能賞心悅目：

- **ANSI 彩色輸出**：不同狀態、不同專案使用不同顏色區分
- **表格展示**：記錄列表以整齊的表格形式呈現
- **進度條**：番茄鐘和計時器即時顯示進度
- **長條圖**：分析結果以終端長條圖視覺化

### 📦 零外部依賴

純 Python 3.8+ 實現，無需安裝任何第三方函式庫：

```
pip install timeforge
# 完成！無需 pip install 其他任何東西
```

### 💾 本地資料儲存

所有資料以 JSON 格式儲存在本地，資料完全自主可控：

```
~/.timeforge/
├── records.json      # 時間記錄
├── config.json       # 使用者配置
└── pomodoro.json     # 番茄鐘狀態
```

---

## 🚀 快速開始

### 環境要求

- **Python 3.8** 或更高版本

### 安裝

```bash
# 從 PyPI 安裝
pip install timeforge

# 或從 GitHub 安裝最新版本
pip install git+https://github.com/gitstq/TimeForge.git
```

### 快速使用

```bash
# 1. 開始追蹤一個任務
timeforge start "編寫專案文件" --project "docs"

# 2. 查看當前狀態
timeforge status

# 3. 停止任務
timeforge stop

# 4. 查看今日日誌
timeforge log --today

# 5. 產生 HTML 報告
timeforge report --format html --output weekly_report.html

# 6. 查看生產力分析
timeforge analyze
```

五分鐘上手，從此掌控你的時間。

---

## 📖 詳細使用指南

### 時間追蹤進階用法

```bash
# 帶標籤的追蹤
timeforge start "程式碼審查" --project "review" --tags "urgent,frontend"

# 追溯新增記錄（補充之前忘記記錄的任務）
timeforge start "緊急修復" --project "hotfix" --at "2025-01-15 09:30"

# 按日期範圍查看日誌
timeforge log --from 2025-01-01 --to 2025-01-31

# 按專案篩選日誌
timeforge log --project "web-app"

# 按標籤篩選日誌
timeforge log --tags "urgent"
```

### 番茄鐘使用

```bash
# 啟動標準番茄鐘（25 分鐘工作 / 5 分鐘休息）
timeforge pomodoro start

# 長休息模式（25 分鐘工作 / 15 分鐘休息）
timeforge pomodoro start --long-break

# 自訂時長
timeforge pomodoro start --work 45 --break 10 --long-break-duration 20

# 查看今日番茄鐘統計
timeforge pomodoro stats

# 連續番茄鐘模式（自動開始下一輪）
timeforge pomodoro start --auto
```

### 報告產生範例

```bash
# 本週報告
timeforge report --format html --output week.html --period week

# 本月報告
timeforge report --format markdown --output month.md --period month

# 自訂日期範圍報告
timeforge report --format csv --output q1.csv --from 2025-01-01 --to 2025-03-31

# 按專案彙總的報告
timeforge report --format json --output summary.json --group-by project
```

### 分析功能說明

```bash
# 綜合分析（預設顯示本週資料）
timeforge analyze

# 按日分析
timeforge analyze --by day

# 按專案分析
timeforge analyze --by project

# 按標籤分析
timeforge analyze --by tag

# 指定時間範圍
timeforge analyze --from 2025-01-01 --to 2025-12-31
```

**分析輸出範例：**

```
📊 生產力分析報告
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
📅 分析週期: 2025-01-01 ~ 2025-01-31

⏱️ 總計時長: 156h 30m
🔥 連續天數: 22 天
📈 效率評分: 87/100

📋 專案分佈:
  web-app    ████████████████░░░░  65%  (101h 42m)
  backend    ██████░░░░░░░░░░░░░░  25%  (39h 08m)
  docs       ███░░░░░░░░░░░░░░░░░  10%  (15h 40m)

💡 智慧建議:
  • 你在上午 9:00-11:30 效率最高，建議將重要任務安排在此時段
  • web-app 專案佔比過高，建議合理分配時間
  • 週三產出最低，可以考慮安排為學習或整理日
```

### Git 關聯使用

```bash
# 自動關聯（在 Git 倉庫目錄內）
timeforge start "開發 API 介面" --project "backend" --git

# 停止時自動記錄當前 commit hash
timeforge stop

# 查看帶 Git 資訊的日誌
timeforge log --git

# 產生包含 Git 資訊的報告
timeforge report --format html --output report.html --git
```

### 配置管理

```bash
# 查看當前配置
timeforge config

# 設定預設專案
timeforge config set default_project "my-project"

# 設定番茄鐘預設工作時長
timeforge config set pomodoro_work 50

# 設定資料儲存路徑
timeforge config set data_dir "/path/to/custom/dir"

# 重設配置
timeforge config reset
```

---

## 💡 設計思路與迭代規劃

### 設計理念

| 理念 | 說明 |
|------|------|
| **簡潔高效** | 每個命令都經過精心設計，最少按鍵完成最多操作 |
| **資料自主** | 所有資料本地儲存，不依賴任何雲端服務，隱私完全可控 |
| **開發者友善** | 終端原生體驗，與 Git 等開發工具無縫整合 |

### 技術選型原因

- **純 Python**：降低入門門檻，跨平台相容性好
- **零外部依賴**：安裝即用，不引入版本衝突風險
- **JSON 儲存**：人類可讀，便於備份和遷移
- **CLI 介面**：開發者最熟悉的工作環境，無需切換上下文

### 後續計畫

| 階段 | 計畫內容 | 狀態 |
|------|----------|------|
| v1.0 | 核心時間追蹤 + 番茄鐘 + 報告 | ✅ 已完成 |
| v1.1 | Git 整合 + 生產力分析 | ✅ 已完成 |
| v2.0 | Web 儀表板（本地視覺化面板） | 🔄 規劃中 |
| v2.1 | 團隊協作（共享專案時間統計） | 📋 計畫中 |
| v2.5 | 資料匯入匯出（支援 Toggl/Clockify 格式） | 📋 計畫中 |
| v3.0 | 外掛系統（支援自訂擴充） | 💡 構想中 |

---

## 📦 安裝與部署指南

### 從 PyPI 安裝（推薦）

```bash
pip install timeforge
```

### 從原始碼安裝

```bash
# 複製倉庫
git clone https://github.com/gitstq/TimeForge.git
cd TimeForge

# 安裝
pip install .
```

### 開發模式安裝

```bash
# 複製倉庫
git clone https://github.com/gitstq/TimeForge.git
cd TimeForge

# 以開發模式安裝（修改原始碼後立即生效）
pip install -e .
```

### 驗證安裝

```bash
timeforge --version
timeforge --help
```

---

## 🤝 貢獻指南

我們歡迎並感謝所有形式的貢獻！無論是提交 Bug、改進文件，還是提交程式碼。

### 提交 PR 規範

1. **Fork** 本倉庫
2. 建立特性分支：`git checkout -b feature/your-feature-name`
3. 提交變更：`git commit -m "feat: 新增你的功能描述"`
4. 推送分支：`git push origin feature/your-feature-name`
5. 提交 **Pull Request**

**Commit 訊息規範：**

| 類型 | 說明 |
|------|------|
| `feat:` | 新功能 |
| `fix:` | 修復 Bug |
| `docs:` | 文件更新 |
| `style:` | 程式碼格式調整（不影響邏輯） |
| `refactor:` | 程式碼重構 |
| `test:` | 測試相關 |
| `chore:` | 建置/工具鏈相關 |

### Issue 規則

- 提交 Bug 前，請先搜尋是否已有相同 Issue
- Bug 回報請包含：重現步驟、期望行為、實際行為、執行環境
- 功能建議請描述使用場景和預期效果

---

## 📄 開源授權

本專案基於 [MIT License](https://opensource.org/licenses/MIT) 開源。

```
MIT License

Copyright (c) 2025 TimeForge Contributors

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
```

---

<p align="center">
  用 <strong>TimeForge</strong> 鍛造你的時間，讓每一分鐘都有價值 ⏱️
</p>

---

<!-- lang:en -->

# English

<div id="english"></div>

<p align="center">
  <strong>TimeForge</strong> — Lightweight Terminal Time Tracking & Productivity Analysis Tool
</p>

<p align="center">
  <img src="https://img.shields.io/badge/Python-3.8+-blue.svg" alt="Python 3.8+">
  <img src="https://img.shields.io/badge/License-MIT-green.svg" alt="MIT License">
  <img src="https://img.shields.io/badge/Dependencies-0-red.svg" alt="Zero Dependencies">
</p>

---

## 🎉 Introduction

**TimeForge** is a lightweight terminal-based time tracking and productivity analysis CLI tool built for developers. Implemented in pure Python with **zero external dependencies**, it works right out of the box.

### Why TimeForge?

Have you ever faced these challenges in your daily development workflow?

- **Time Black Hole**: You reach the end of the day with no idea where your time went
- **Bloated Tools**: Existing time trackers are either too heavy, too expensive, or require an internet connection
- **Data Silos**: Your time data is disconnected from your code commits (Git), making correlation analysis impossible
- **Efficiency Blind Spots**: You lack quantitative insight into your work patterns and productivity

TimeForge was born to solve these pain points. Inspired by the pursuit of **efficient time management**, we believe a great time management tool should be like a scalpel, not a Swiss Army knife.

### What Sets Us Apart

| Feature | TimeForge | Other Tools |
|---------|-----------|-------------|
| External Dependencies | **Zero** | Usually requires Node.js, databases, etc. |
| Data Storage | **Local JSON** | Cloud storage with privacy risks |
| Pomodoro Timer | **Built-in** | Requires additional plugins |
| Git Integration | **Auto-link commits** | Not supported or manual only |
| Report Formats | **4 export formats** | Usually only 1-2 |
| Productivity Analysis | **Built-in smart analysis** | Requires paid upgrade |

---

## ✨ Core Features

### ⏱️ Precise Time Tracking

Full timer lifecycle management with start, stop, pause, resume, status, log, list, delete, and edit:

```bash
# Start tracking a task
timeforge start "Fix login page bug" --project "web-app"

# Pause the current task
timeforge pause

# Resume a paused task
timeforge resume

# Stop the current task
timeforge stop

# Check current status
timeforge status

# View today's log
timeforge log --today

# View all records
timeforge list

# Delete a record
timeforge delete <id>

# Edit a record
timeforge edit <id> --project "mobile-app" --description "Optimize homepage load speed"
```

### 🍅 Built-in Pomodoro Timer

Configurable work/break durations with real-time terminal progress bar:

```bash
# Start a 25-minute Pomodoro session (default)
timeforge pomodoro start

# Custom work duration of 50 minutes, 10-minute break
timeforge pomodoro start --work 50 --break 10

# Check Pomodoro status
timeforge pomodoro status

# Stop Pomodoro
timeforge pomodoro stop
```

### 📊 Multi-format Reports

Export in **JSON / CSV / HTML / Markdown** formats:

```bash
# Generate a JSON report
timeforge report --format json --output report.json

# Generate a CSV report
timeforge report --format csv --output report.csv

# Generate an HTML report (viewable in browser)
timeforge report --format html --output report.html

# Generate a Markdown report
timeforge report --format markdown --output report.md
```

### 🧠 Smart Productivity Analysis

Gain deep insights into your work patterns with efficiency scores, streaks, and smart suggestions:

```bash
# View productivity analysis report
timeforge analyze

# View analysis for a specific time range
timeforge analyze --from 2025-01-01 --to 2025-01-31

# View project time distribution
timeforge analyze --by project
```

Analysis includes:

- **Project Time Distribution**: Visual breakdown of time spent per project
- **Efficiency Score**: Composite score calculated from your work patterns
- **Streak Tracking**: Motivates you to maintain a daily logging habit
- **Smart Suggestions**: Automatically generated optimization tips based on your data

### 🔗 Git Integration

Automatically link Git commits to time records, giving you a clear picture of code changes alongside time investment:

```bash
# Start tracking in a Git repo (auto-links current branch and latest commit)
timeforge start "Develop new feature" --project "backend" --git

# View records with Git information
timeforge log --git
```

### 🎨 Beautiful Terminal UI

Rich terminal display capabilities that make the command line a pleasure to use:

- **ANSI Color Output**: Different states and projects distinguished by color
- **Table Display**: Records presented in clean, aligned tables
- **Progress Bars**: Real-time progress for Pomodoro timer and stopwatch
- **Bar Charts**: Analysis results visualized as terminal bar charts

### 📦 Zero External Dependencies

Pure Python 3.8+ implementation with no third-party libraries required:

```
pip install timeforge
# Done! No need to pip install anything else
```

### 💾 Local Data Storage

All data is stored locally in JSON format, keeping you in full control:

```
~/.timeforge/
├── records.json      # Time records
├── config.json       # User configuration
└── pomodoro.json     # Pomodoro state
```

---

## 🚀 Quick Start

### Requirements

- **Python 3.8** or later

### Installation

```bash
# Install from PyPI
pip install timeforge

# Or install the latest version from GitHub
pip install git+https://github.com/gitstq/TimeForge.git
```

### Quick Usage

```bash
# 1. Start tracking a task
timeforge start "Write project documentation" --project "docs"

# 2. Check current status
timeforge status

# 3. Stop the task
timeforge stop

# 4. View today's log
timeforge log --today

# 5. Generate an HTML report
timeforge report --format html --output weekly_report.html

# 6. View productivity analysis
timeforge analyze
```

Up and running in five minutes. Take control of your time.

---

## 📖 Detailed Usage Guide

### Advanced Time Tracking

```bash
# Track with tags
timeforge start "Code review" --project "review" --tags "urgent,frontend"

# Backdate a record (for tasks you forgot to log)
timeforge start "Emergency fix" --project "hotfix" --at "2025-01-15 09:30"

# View logs by date range
timeforge log --from 2025-01-01 --to 2025-01-31

# Filter logs by project
timeforge log --project "web-app"

# Filter logs by tag
timeforge log --tags "urgent"
```

### Pomodoro Timer

```bash
# Start a standard Pomodoro (25 min work / 5 min break)
timeforge pomodoro start

# Long break mode (25 min work / 15 min break)
timeforge pomodoro start --long-break

# Custom durations
timeforge pomodoro start --work 45 --break 10 --long-break-duration 20

# View today's Pomodoro stats
timeforge pomodoro stats

# Auto-chain mode (automatically starts the next round)
timeforge pomodoro start --auto
```

### Report Generation Examples

```bash
# Weekly report
timeforge report --format html --output week.html --period week

# Monthly report
timeforge report --format markdown --output month.md --period month

# Custom date range report
timeforge report --format csv --output q1.csv --from 2025-01-01 --to 2025-03-31

# Report grouped by project
timeforge report --format json --output summary.json --group-by project
```

### Analysis Features

```bash
# Comprehensive analysis (shows current week by default)
timeforge analyze

# Analyze by day
timeforge analyze --by day

# Analyze by project
timeforge analyze --by project

# Analyze by tag
timeforge analyze --by tag

# Specify time range
timeforge analyze --from 2025-01-01 --to 2025-12-31
```

**Sample Analysis Output:**

```
📊 Productivity Analysis Report
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
📅 Period: 2025-01-01 ~ 2025-01-31

⏱️ Total Time: 156h 30m
🔥 Streak: 22 days
📈 Efficiency Score: 87/100

📋 Project Distribution:
  web-app    ████████████████░░░░  65%  (101h 42m)
  backend    ██████░░░░░░░░░░░░░░  25%  (39h 08m)
  docs       ███░░░░░░░░░░░░░░░░░  10%  (15h 40m)

💡 Smart Suggestions:
  • You're most productive between 9:00-11:30 AM — schedule important tasks then
  • web-app takes up a disproportionate amount of time — consider rebalancing
  • Wednesday has the lowest output — consider using it for learning or cleanup
```

### Git Integration

```bash
# Auto-link (inside a Git repository directory)
timeforge start "Develop API endpoints" --project "backend" --git

# Automatically records the current commit hash on stop
timeforge stop

# View logs with Git information
timeforge log --git

# Generate a report with Git information
timeforge report --format html --output report.html --git
```

### Configuration Management

```bash
# View current configuration
timeforge config

# Set default project
timeforge config set default_project "my-project"

# Set default Pomodoro work duration
timeforge config set pomodoro_work 50

# Set custom data directory
timeforge config set data_dir "/path/to/custom/dir"

# Reset configuration
timeforge config reset
```

---

## 💡 Design Philosophy & Roadmap

### Design Principles

| Principle | Description |
|-----------|-------------|
| **Simple & Efficient** | Every command is carefully designed for maximum output with minimum keystrokes |
| **Data Sovereignty** | All data is stored locally with no cloud dependencies — your data, your control |
| **Developer-Friendly** | Native terminal experience with seamless integration into developer tools like Git |

### Technical Choices

- **Pure Python**: Low barrier to entry, excellent cross-platform compatibility
- **Zero Dependencies**: Install and run immediately, no version conflict risks
- **JSON Storage**: Human-readable, easy to back up and migrate
- **CLI Interface**: The environment developers are most comfortable with — no context switching

### Roadmap

| Phase | Planned Features | Status |
|-------|-----------------|--------|
| v1.0 | Core time tracking + Pomodoro + Reports | ✅ Done |
| v1.1 | Git integration + Productivity analysis | ✅ Done |
| v2.0 | Web dashboard (local visualization panel) | 🔄 Planned |
| v2.1 | Team collaboration (shared project time stats) | 📋 Proposed |
| v2.5 | Data import/export (Toggl/Clockify format support) | 📋 Proposed |
| v3.0 | Plugin system (custom extensions) | 💡 Concept |

---

## 📦 Installation & Deployment

### Install from PyPI (Recommended)

```bash
pip install timeforge
```

### Install from Source

```bash
# Clone the repository
git clone https://github.com/gitstq/TimeForge.git
cd TimeForge

# Install
pip install .
```

### Development Mode

```bash
# Clone the repository
git clone https://github.com/gitstq/TimeForge.git
cd TimeForge

# Install in editable mode (changes take effect immediately)
pip install -e .
```

### Verify Installation

```bash
timeforge --version
timeforge --help
```

---

## 🤝 Contributing

We welcome and appreciate contributions of all kinds — whether it's reporting bugs, improving documentation, or submitting code.

### Pull Request Guidelines

1. **Fork** this repository
2. Create a feature branch: `git checkout -b feature/your-feature-name`
3. Commit your changes: `git commit -m "feat: add your feature description"`
4. Push the branch: `git push origin feature/your-feature-name`
5. Submit a **Pull Request**

**Commit Message Convention:**

| Type | Description |
|------|-------------|
| `feat:` | New feature |
| `fix:` | Bug fix |
| `docs:` | Documentation update |
| `style:` | Code formatting (no logic changes) |
| `refactor:` | Code refactoring |
| `test:` | Test-related changes |
| `chore:` | Build/tooling changes |

### Issue Guidelines

- Search for existing issues before submitting a new one
- Bug reports should include: reproduction steps, expected behavior, actual behavior, and runtime environment
- Feature requests should describe the use case and expected outcome

---

## 📄 License

This project is licensed under the [MIT License](https://opensource.org/licenses/MIT).

```
MIT License

Copyright (c) 2025 TimeForge Contributors

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
```

---

<p align="center">
  Forge your time with <strong>TimeForge</strong> — make every minute count ⏱️
</p>

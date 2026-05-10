# Contributing to TimeForge

感谢你有兴趣为 TimeForge 做贡献！

## 开发环境设置

```bash
# 克隆仓库
git clone https://github.com/gitstq/TimeForge.git
cd TimeForge

# 创建虚拟环境
python -m venv venv
source venv/bin/activate  # Linux/macOS
# 或 venv\Scripts\activate  # Windows

# 安装开发依赖
pip install -e ".[dev]"
```

## 代码风格

- 使用 Black 格式化代码
- 使用 isort 排序导入
- 遵循 PEP 8 规范

```bash
# 格式化代码
black timeforge tests
isort timeforge tests

# 检查代码
flake8 timeforge tests
mypy timeforge
```

## 运行测试

```bash
# 运行所有测试
pytest

# 运行测试并生成覆盖率报告
pytest --cov=timeforge
```

## 提交规范

请使用以下提交格式：

- `feat:` 新功能
- `fix:` 修复问题
- `docs:` 文档更新
- `refactor:` 代码重构
- `test:` 测试相关
- `chore:` 构建/工具相关

示例：
```
feat: 添加自定义主题支持
fix: 修复倒计时暂停后无法恢复的问题
docs: 更新安装说明
```

## Pull Request 流程

1. Fork 本仓库
2. 创建功能分支
3. 编写代码和测试
4. 确保所有测试通过
5. 提交 Pull Request

## 问题反馈

如果你发现问题或有功能建议，请在 Issues 页面创建新问题。

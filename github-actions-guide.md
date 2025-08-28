# GitHub Actions 自动化发布指南

## 🚀 功能概述

我已为您的项目配置了完整的GitHub Actions自动化流程，包括：

### 1. 自动化Release构建 (`build.yml`)
- **触发条件**：推送版本标签（如 `v2.1.0`）
- **功能**：自动构建Windows exe文件并创建GitHub Release
- **输出**：带有详细发布说明的Release页面

### 2. 完整的CI/CD流程 (`release.yml`)
- **支持平台**：Windows, Linux, macOS
- **自动构建**：多平台可执行文件
- **发布管理**：自动创建Release并上传构建产物

### 3. 代码质量检查 (`test.yml`)
- **代码检查**：Python语法和风格检查
- **多版本测试**：Python 3.9, 3.10, 3.11
- **构建验证**：确保exe文件能正常构建

## 📁 文件结构

```
.github/
└── workflows/
    ├── build.yml      # 简化版自动发布（推荐）
    ├── release.yml    # 完整版多平台构建
    └── test.yml       # 代码检查和测试
```

## 🎯 使用方法

### 方法1：简化版发布（推荐）

1. **推送代码到GitHub**：
   ```bash
   git add .
   git commit -m "feat: ready for release"
   git push origin main
   ```

2. **创建版本标签**：
   ```bash
   git tag v2.1.0
   git push origin v2.1.0
   ```

3. **自动触发**：
   - GitHub Actions自动运行
   - 构建Windows exe文件
   - 创建Release页面
   - 上传exe文件到Release

### 方法2：手动触发

1. 访问GitHub仓库的Actions页面
2. 选择"Build and Release (简化版)"工作流
3. 点击"Run workflow"按钮
4. 手动触发构建

### 方法3：完整版多平台构建

使用 `release.yml` 可以构建：
- Windows: `节点转换工具-v2.1.0.exe`
- Linux: `node-config-converter-linux-v2.1.0`
- macOS: `node-config-converter-macos-v2.1.0`

## 🔧 配置说明

### Release命名规则
```yaml
标签格式: v2.1.0, v2.1.1, v3.0.0
Release名称: 节点配置转换工具 v2.1.0
exe文件名: 节点转换工具-v2.1.0.exe
```

### 自动生成的Release内容
- ✨ 功能特色说明
- 📦 下载指南
- 🔧 使用方法
- ⚠️ 免责声明
- 📝 更新日志链接

## 📝 版本发布流程

### 1. 准备发布
```bash
# 更新版本号（在相关文件中）
# 更新 CHANGELOG.md
git add .
git commit -m "chore: prepare for v2.1.1 release"
```

### 2. 创建标签
```bash
git tag v2.1.1
git push origin v2.1.1
```

### 3. 监控构建
- 访问GitHub Actions页面
- 查看构建状态
- 等待构建完成（约5-10分钟）

### 4. 发布完成
- 自动创建Release页面
- exe文件自动上传
- 用户可直接下载使用

## 🛠️ 高级功能

### 预发布版本
```bash
git tag v2.1.0-beta.1
git push origin v2.1.0-beta.1
```

### 修改Release内容
1. 编辑 `build.yml` 中的 `body` 部分
2. 自定义发布说明模板
3. 添加更多下载链接

### 添加其他构建产物
```yaml
files: |
  ./dist/节点转换工具-v2.1.exe
  ./README.md
  ./CHANGELOG.md
```

## 🚨 注意事项

### 1. 权限设置
- 确保仓库已启用GitHub Actions
- 检查GITHUB_TOKEN权限（默认已有）

### 2. 构建环境
- Windows构建器用于exe文件
- 支持Python 3.11环境
- 自动安装所有依赖

### 3. 标签命名
- 必须以 `v` 开头
- 遵循语义化版本规范
- 例：`v2.1.0`, `v2.1.1`, `v3.0.0`

### 4. 构建时间
- Windows exe构建：约5-8分钟
- 多平台构建：约15-20分钟
- 自动重试失败的构建

## 📊 监控和维护

### 查看构建状态
- 访问 `https://github.com/YOUR_USERNAME/YOUR_REPO/actions`
- 查看工作流运行历史
- 检查构建日志

### 故障排除
1. **构建失败**：检查Python依赖是否正确
2. **exe异常**：验证build_exe.py脚本
3. **上传失败**：检查文件路径是否正确

### 更新工作流
- 修改 `.github/workflows/*.yml` 文件
- 提交更改后自动生效
- 建议在测试分支先验证

## 🎉 完成效果

成功配置后，每次发布新版本时：

1. ✅ 自动构建Windows exe文件
2. ✅ 创建专业的Release页面
3. ✅ 提供详细的使用说明
4. ✅ 自动化版本管理
5. ✅ 用户友好的下载体验

这样您就拥有了一个完全自动化的开源项目发布流程！
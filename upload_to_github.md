# GitHub 上传指南

## 当前状态
✅ 代码已脱敏完成
✅ 文件已整理完毕
✅ Git 仓库已初始化
✅ 文件已添加到 Git

## 需要完成的步骤

### 1. 完成 Git 提交
由于 PowerShell 出现问题，请使用以下命令手动完成：

```bash
# 打开新的命令行窗口（cmd 或 PowerShell）
cd "C:\Users\vanke\Desktop\节点转换"

# 提交代码
git commit -m "feat: Node Config Converter v2.1.0"
```

### 2. 创建 GitHub 仓库

访问 https://github.com/new

- **仓库名称**: `node-config-converter`
- **描述**: `🚀 节点配置转换工具 - 支持 Clash YAML ⇄ V2rayN 链接 + V2Ray Config 多格式转换`
- **可见性**: Public
- **不要**初始化 README、.gitignore 或 LICENSE（因为我们已经有了）

### 3. 推送到 GitHub

创建仓库后，GitHub 会显示推送命令，类似：

```bash
git remote add origin https://github.com/YOUR_USERNAME/node-config-converter.git
git branch -M main
git push -u origin main
```

## 仓库结构

```
node-config-converter/
├── yaml_to_v2rayn.py          # 主程序文件
├── build_exe.py               # 打包脚本
├── requirements.txt           # Python 依赖
├── README.md                  # 项目说明
├── LICENSE                    # MIT 许可证
├── CHANGELOG.md               # 更新日志
└── .gitignore                 # Git 忽略文件
```

## 功能特色

- ✨ 三向转换支持：Clash YAML ⇄ V2rayN 链接 + V2Ray Config
- 🎨 现代化 GUI 界面，三种转换模式颜色区分
- 🛡️ 支持 VMess、VLESS、SS、Trojan、Hysteria2 协议
- 🧠 智能格式自动检测
- 📦 提供独立 exe 文件

## 版本信息
- 当前版本：v2.1.0
- 最后更新：2025-08-28
- 协议支持：MIT License

完成上传后，您的开源项目就可以在 GitHub 上公开访问了！
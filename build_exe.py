#!/usr/bin/env python3
# -*- coding: utf-8 -*-

'''
封装 yaml_to_v2rayn.py 为 EXE 文件
'''

import os
import subprocess

def build_exe():
    '''
    使用 PyInstaller 构建 EXE 文件
    '''
    # 确保 PyInstaller 已安装
    try:
        import PyInstaller
        print("PyInstaller 已安装，版本：", PyInstaller.__version__)
    except ImportError:
        print("正在安装 PyInstaller...")
        subprocess.call(["pip", "install", "pyinstaller"])
        print("PyInstaller 安装完成")

    # 构建命令行参数
    cmd = [
        "pyinstaller",
        "--name=节点转换工具-v2.1",      # 程序名称
        "--windowed",                  # 无控制台窗口
        "--onefile",                   # 单文件模式
        "--icon=icon.ico" if os.path.exists("icon.ico") else "",  # 图标
        "--add-data=README.md;.",      # 添加额外文件
        "--clean",                     # 打包前清理
        "--distpath=dist",             # 输出目录
        "--workpath=build",            # 工作目录
        "yaml_to_v2rayn.py"            # 主脚本
    ]

    # 移除空参数
    cmd = [arg for arg in cmd if arg]

    # 执行打包命令
    print("开始构建 EXE 文件...")
    print("命令:", " ".join(cmd))
    
    # 在GitHub Actions中使用UTF-8编码
    import locale
    if os.getenv('GITHUB_ACTIONS'):
        # GitHub Actions环境
        result = subprocess.run(cmd, capture_output=True, text=True, encoding='utf-8')
        if result.returncode != 0:
            print("构建失败:")
            print(result.stderr)
            sys.exit(1)
    else:
        # 本地环境
        subprocess.call(cmd)
        
    print("构建完成！")
    print("EXE 文件已生成在 dist 目录下")

if __name__ == "__main__":
    build_exe()

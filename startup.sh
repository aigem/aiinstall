#!/bin/bash

# 检查是否为 root 用户
check_root() {
    if [ "$EUID" -ne 0 ]; then
        echo "请使用 root 权限运行此脚本"
        exit 1
    fi
}

# 检测操作系统类型
detect_os() {
    if [ -f /etc/os-release ]; then
        . /etc/os-release
        OS=$NAME
    else
        OS=$(uname -s)
    fi
}

# 检查 Python 是否安装
check_python() {
    if ! command -v python3 &> /dev/null; then
        echo "Python3 未安装，开始安装..."
        install_python
    else
        PYTHON_VERSION=$(python3 --version 2>&1 | awk '{print $2}')
        echo "检测到 Python 版本: $PYTHON_VERSION"
    fi
}

# 安装 Python
install_python() {
    detect_os
    case $OS in
        "Ubuntu"|"Debian GNU/Linux")
            apt-get update
            apt-get install -y python3 python3-pip
            ;;
        "CentOS Linux"|"Red Hat Enterprise Linux")
            yum install -y python3 python3-pip
            ;;
        "Alpine Linux")
            apk add --no-cache python3 py3-pip
            ;;
        *)
            echo "不支持的操作系统: $OS"
            exit 1
            ;;
    esac

    if [ $? -eq 0 ]; then
        echo "Python3 安装成功"
    else
        echo "Python3 安装失败"
        exit 1
    fi
}

# 创建 Python 软链接
setup_python_links() {
    # 检查 python 命令是否存在
    if ! command -v python &> /dev/null; then
        echo "创建 python 软链接..."
        # 检查 /usr/bin/python3 是否存在
        if [ -f /usr/bin/python3 ]; then
            ln -sf /usr/bin/python3 /usr/bin/python
            echo "已创建 python -> python3 软链接"
        else
            # 查找 python3 的实际位置
            PYTHON3_PATH=$(which python3)
            if [ -n "$PYTHON3_PATH" ]; then
                ln -sf "$PYTHON3_PATH" /usr/bin/python
                echo "已创建 python -> $PYTHON3_PATH 软链接"
            else
                echo "错误：无法找到 python3"
                exit 1
            fi
        fi
    else
        echo "python 命令已存在"
    fi

    # 检查 pip 命令是否存在
    if ! command -v pip &> /dev/null; then
        echo "创建 pip 软链接..."
        if [ -f /usr/bin/pip3 ]; then
            ln -sf /usr/bin/pip3 /usr/bin/pip
            echo "已创建 pip -> pip3 软链接"
        else
            PIP3_PATH=$(which pip3)
            if [ -n "$PIP3_PATH" ]; then
                ln -sf "$PIP3_PATH" /usr/bin/pip
                echo "已创建 pip -> $PIP3_PATH 软链接"
            else
                echo "错误：无法找到 pip3"
                exit 1
            fi
        fi
    else
        echo "pip 命令已存在"
    fi
}

# 安装依赖
install_requirements() {
    echo "检查依赖安装..."
    if [ -f "requirements.txt" ]; then
        echo "找到 requirements.txt，开始安装依赖..."
        if python3 -m pip install -r requirements.txt --break-system-packages; then
            echo "依赖安装成功"
        else
            echo "依赖安装失败"
            exit 1
        fi
    else
        echo "未找到 requirements.txt 文件"
    fi
}

# 主函数
main() {
    # 如果是需要 sudo 的操作系统，先检查权限
    if [ "$OS" != "Alpine Linux" ]; then
        check_root
    fi
    
    # 检查并安装 Python
    check_python
    
    # 设置 Python 软链接
    setup_python_links
    
    # 验证安装
    echo "验证 Python 安装："
    echo "python3 版本："
    python3 --version
    echo "python 版本："
    python --version
    echo "pip3 版本："
    pip3 --version
    echo "pip 版本："
    pip --version

    # 安装依赖
    install_requirements
}

# 执行主函数
main

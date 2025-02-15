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

# 主函数
main() {
    # 如果是需要 sudo 的操作系统，先检查权限
    if [ "$OS" != "Alpine Linux" ]; then
        check_root
    fi
    
    # 检查并安装 Python
    check_python
    
    # 验证安装
    python3 --version
    pip3 --version
}

# 执行主函数
main

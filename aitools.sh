#!/bin/bash

# 获取当前目录的绝对路径
BASE_DIR=$(pwd)

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
        echo "Python3 未安装，请使用系统包管理器安装 Python3..."
        echo "Ubuntu/Debian: sudo apt-get install python3 python3-pip"
        echo "CentOS/RHEL: sudo yum install python3 python3-pip"
        echo "Alpine: apk add --no-cache python3 py3-pip"
        exit 1
    else
        PYTHON_VERSION=$(python3 --version 2>&1 | awk '{print $2}')
        echo "检测到 Python 版本: $PYTHON_VERSION"
    fi
}

# 创建 Python 软链接
setup_python_links() {
    mkdir -p "$HOME/.local/bin"
    
    # 检查 python 命令是否存在
    if ! command -v python &> /dev/null; then
        echo "创建用户级 python 软链接..."
        PYTHON3_PATH=$(which python3)
        if [ -n "$PYTHON3_PATH" ]; then
            ln -sf "$PYTHON3_PATH" "$HOME/.local/bin/python"
            echo "已创建 python -> $PYTHON3_PATH 软链接"
        else
            echo "错误：无法找到 python3"
            exit 1
        fi
    else
        echo "python 命令已存在"
    fi

    # 检查 pip 命令是否存在
    if ! command -v pip &> /dev/null; then
        echo "创建用户级 pip 软链接..."
        PIP3_PATH=$(which pip3)
        if [ -n "$PIP3_PATH" ]; then
            ln -sf "$PIP3_PATH" "$HOME/.local/bin/pip"
            echo "已创建 pip -> $PIP3_PATH 软链接"
        else
            echo "错误：无法找到 pip3"
            exit 1
        fi
    else
        echo "pip 命令已存在"
    fi

    # 添加用户 bin 目录到 PATH
    if [[ ":$PATH:" != *":$HOME/.local/bin:"* ]]; then
        echo 'export PATH="$HOME/.local/bin:$PATH"' >> "$HOME/.bashrc"
        echo "已添加 $HOME/.local/bin 到 PATH"
        export PATH="$HOME/.local/bin:$PATH"
    fi
}

# 安装依赖
install_requirements() {
    echo "检查依赖安装..."
    if [ -f "requirements.txt" ]; then
        echo "找到 requirements.txt，开始安装依赖..."
        if python3 -m pip install --user -r requirements.txt; then
            echo "依赖安装成功"
        else
            echo "================================================================"
            echo "依赖安装失败"
            echo "请检查网络连接是否正常"
            echo "请检查 Python 版本是否正确安装"
            echo "请查看：https://fuliai-ai2u.hf.space/ 获取最新的相关说明及命令"
            echo "================================================================"
            exit 1
        fi
    else
        echo "未找到 requirements.txt 文件，当前目录: $(pwd)"
        ls -la
        exit 1
    fi
}

# 检查并安装 Git LFS
setup_git_lfs() {
    echo "检查 Git LFS..."
    if ! command -v git-lfs &> /dev/null; then
        echo "Git LFS 未安装，开始安装..."
        if [ "$OS" = "Ubuntu" ] || [ "$OS" = "Debian GNU/Linux" ]; then
            curl -s https://packagecloud.io/install/repositories/github/git-lfs/script.deb.sh | sudo bash
            sudo apt-get install git-lfs
        elif [ "$OS" = "CentOS Linux" ] || [ "$OS" = "Red Hat Enterprise Linux" ]; then
            sudo yum install git-lfs
        elif [ "$OS" = "Alpine Linux" ]; then
            apk add --no-cache git-lfs
        else
            echo "不支持的操作系统: $OS"
            echo "请手动安装 Git LFS: https://git-lfs.com"
            exit 1
        fi
    else
        echo "Git LFS 已安装"
    fi

    # 初始化 Git LFS
    echo "初始化 Git LFS..."
    git lfs install --skip-repo
    if [ $? -eq 0 ]; then
        echo "Git LFS 初始化成功"
    else
        echo "Git LFS 初始化失败"
        exit 1
    fi
}

# 部署 KSA 内网穿透
setup_ksa() {
    echo "开始部署 KSA 内网穿透..."
    
    # KSA 仓库地址
    KSA_REPO="https://gitee.com/fuliai/ai2u.git"
    
    
    # 保存当前目录
    CURRENT_DIR=$(pwd)
    
    # 创建目录并下载
    mkdir -p "$BASE_DIR/ksa"
    cd "$BASE_DIR"
    
    if [ -d "ai2u" ]; then
        echo "更新 KSA 仓库..."
        cd ai2u
        git pull
    else
        echo "克隆 KSA 仓库..."
        git clone "$KSA_REPO"
        cd ai2u
    fi
    
    # 解压并设置权限
    echo "解压 KSA 文件..."
    unzip -o ksa.zip -d "$BASE_DIR/"
    chmod +x "$BASE_DIR/ksa/ksa_x64"
    
    # 清理旧文件并运行
    rm -f "$BASE_DIR/ksa_ID_Token.txt"
    echo "正在启动 KSA..."
    "$BASE_DIR/ksa/ksa_x64" > "$BASE_DIR/ksa_ID_Token.txt" 2>&1
    rm -rf "ai2u"
    
    # 检查运行状态
    if grep -q "KSA ID" "$BASE_DIR/ksa_ID_Token.txt"; then
        echo "KSA 运行成功"
        echo "KSA ID 和 Token 已保存到: $BASE_DIR/ksa_ID_Token.txt"
    else
        echo "KSA 首次运行失败，尝试重新运行..."
        "$BASE_DIR/ksa/ksa_x64" > "$BASE_DIR/ksa_ID_Token.txt" 2>&1
        if grep -q "KSA ID" "$BASE_DIR/ksa_ID_Token.txt"; then
            echo "KSA 重试运行成功"
        else
            echo "KSA 运行失败，请检查日志: $BASE_DIR/ksa_ID_Token.txt"
        fi
    fi
    
    # 返回原始目录
    cd "$CURRENT_DIR"
}

# 提示说明
info() {
    echo "================================================"
    echo ""
    echo "     请查看【说明文件】进行下一步的安装"
    echo "     或查看：https://fuliai-ai2u.hf.space/"
    echo "     获取最新的相关说明及命令"
    echo ""
    echo "================================================"
}

# 主函数
main() {
    # 检查并验证 Python
    check_python
    
    # 设置 Python 软链接
    setup_python_links
    
    # 安装依赖
    install_requirements
    
    # 设置 Git LFS
    setup_git_lfs
    
    # 部署 KSA
    setup_ksa
    
    # 验证安装
    echo "验证安装环境："
    echo "工作目录："
    echo "$BASE_DIR"
    echo ""
    echo "Python 环境："
    echo "python3 版本："
    python3 --version
    echo "python 版本："
    python --version
    echo "pip3 版本："
    pip3 --version
    echo "pip 版本："
    pip --version
    echo "Git LFS 版本："
    git lfs version
    
    # 显示信息
    info
}

# 执行主函数
main

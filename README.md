# AI 应用一键安装系统

一个为 AI 应用量身定制的 Linux 环境安装解决方案，通过 YAML 配置文件实现一键式自动化部署。本系统支持在不同的 Linux 环境（如不同版本的 Ubuntu）下安装 AI 应用，主要处理不同环境下的路径差异和权限需求。

## 特性

- 🔧 **配置驱动**: 通过 YAML 配置文件定义安装流程，无需编写脚本
- 🐧 **Linux 环境支持**: 预设多个 Ubuntu 环境配置，处理路径和权限差异
- 📦 **模块化安装**: 标准化的四阶段安装流程，确保安装过程可控
- 📝 **详细日志**: 完整的日志记录，包括命令执行和安装过程
- ⚡ **简单易用**: 简洁的命令行接口，支持配置验证和变量覆盖

## 安装

1. 克隆仓库：
   ```bash
   git clone https://github.com/aigem/aiinstall.git
   cd aiinstall
   ```

2. 安装依赖：
   ```bash
   pip install -r requirements.txt
   ```

## 使用方法

### 基本命令

1. 查看帮助：
   ```bash
   python -m installer --help
   ```

2. 使用预设环境安装应用：
   ```bash
   python -m installer install comfyui --env ubuntu-a
   ```

3. 使用自定义配置文件：
   ```bash
   python -m installer install --config my_config.yml --env ubuntu-b
   ```

4. 验证配置文件：
   ```bash
   python -m installer validate my_config.yml
   ```

5. 生成应用配置模板：
   ```bash
   # 基本用法
   python -m installer generate-config myapp

   # 完整参数
   python -m installer generate-config comfyui \
       --description "应用描述" \
       --repo-url "https://github.com/user/repo.git" \
       --version "latest" \
       --port 8188 \
       --docs-url "https://docs.example.com"
   ```

### 环境配置

环境配置集中在 `configs/environments.yml` 文件中：

```yaml
# 预设环境配置
environments:
  # 基础环境配置
  base: &env-base
    python_cmd: "python3"
    pip_index: "https://pypi.org/simple"
    pip_timeout: 60
    pip_retries: 3

  # 非sudo环境
  ubuntu-a: &ubuntu-a
    <<: *env-base
    base_dir: "/home/{user}/ai_apps/{name}"
    use_sudo: false
    env_vars:
      PYTHONPATH: "{base_dir}/src"

  # sudo环境
  ubuntu-b: &ubuntu-b
    <<: *env-base
    base_dir: "/opt/ai/{name}"
    use_sudo: true
    env_vars:
      PYTHONPATH: "{base_dir}/src"

  # 中国区环境
  ubuntu-a-cn:
    <<: *ubuntu-a
    pip_index: "https://pypi.tuna.tsinghua.edu.cn/simple"
```

### 配置文件示例

### 配置模板生成

系统提供了配置模板生成器，可以快速创建新的应用配置文件：

1. **生成配置**：使用 `generate-config` 命令生成基础配置
2. **查看说明**：参考 `configs/variables.md` 了解可用变量
3. **修改配置**：根据应用需求修改生成的配置文件

配置模板包含：
- 基础信息（名称、描述、版本）
- 环境选择
- 标准安装步骤
- 启动配置
- 安装完成提示

### 变量和命令模板

`configs/variables.md` 提供了详细的变量说明和常用命令模板：

1. **可用变量**：
   - 基础变量（应用信息）
   - 环境变量（路径、权限）
   - Python/pip相关
   - 虚拟环境

2. **命令模板**：
   - 目录操作
   - 权限设置
   - Python环境配置
   - Git操作
   - 依赖安装

3. **使用技巧**：
   - 条件执行
   - 变量组合
   - 多行命令
   - 环境检查

```yaml
version: "1.0"
name: "comfyui"
description: "Stable Diffusion 可视化工作流环境"

# 使用预设环境
environment: "ubuntu-a"

# 安装步骤
steps:
  - name: "prepare"
    description: "准备环境"
    common:
      - "cd {base_dir}"
      - "{python_cmd} -m venv venv"
      - "venv/bin/pip install --upgrade pip -i {pip_index}"
```

### 环境变量

| 变量名 | 说明 | 示例 |
|--------|------|------|
| {name} | 应用名称 | "comfyui" |
| {base_dir} | 安装目录 | "/home/user/ai_apps/comfyui" |
| {python_cmd} | Python 命令 | "python3" |
| {use_sudo} | 是否使用 sudo | "true" |
| {pip_index} | pip镜像源 | "https://pypi.org/simple" |
| {pip_timeout} | pip超时时间 | 60 |
| {pip_retries} | pip重试次数 | 3 |

### 自定义安装

使用 `--set` 参数覆盖配置变量：
```bash
python -m installer install comfyui --env ubuntu-a --set base_dir=/custom/path
```

## 日志系统

安装过程的日志文件位于 `logs` 目录：

- `{app_name}_install.log`: 安装过程日志
- `{app_name}_commands.log`: 命令执行日志
- `{app_name}_installer.log`: 安装器详细日志

## 错误处理

1. 配置错误：
   ```
   错误: 配置文件必须包含 version 和 name 字段
   ```

2. 环境错误：
   ```
   错误: 环境 ubuntu-c 未在配置文件中定义
   ```

3. 命令执行错误：
   ```
   错误: 安装失败: 命令执行失败: Permission denied
   命令: mkdir -p /opt/ai/test
   ```

## 开发指南

### 项目结构

```
installer/
├── __init__.py
├── cli.py                # 命令行入口
├── core/
│   ├── config.py         # 配置加载和验证
│   ├── installer.py      # 安装流程控制
│   ├── executor.py       # 命令执行器
│   └── logger.py         # 日志管理
└── templates/            # 配置模板
```

### 添加新功能

1. 在 `core` 目录下创建新模块
2. 在 `cli.py` 中添加新命令
3. 更新测试和文档

### 测试

使用最小化测试配置验证功能：
```bash
python -m installer install --config configs/demo.yml --env ubuntu-a
```

## 常见问题

1. **安装失败如何继续？**
   - 检查日志文件了解失败原因
   - 修复问题后重新运行安装命令

2. **如何在新环境中使用？**
   - 在配置文件的 `environments` 部分添加新环境
   - 确保设置正确的路径和权限

3. **支持哪些 Python 版本？**
   - 建议使用 Python 3.8 或更高版本
   - 具体版本要求请参考应用配置文件

## 贡献指南

1. Fork 项目
2. 创建功能分支
3. 提交更改
4. 发起 Pull Request

## 许可证

[MIT License](LICENSE)

## 联系方式

如有问题或建议，请提交 Issue 或联系维护者。 
# AI 应用一键安装系统

一个为 AI 应用量身定制的 Linux 环境安装解决方案，通过 YAML 配置文件实现一键式自动化部署。本系统支持在不同的 Linux 环境（包括 Ubuntu、CentOS 等）下安装 AI 应用，主要处理不同环境下的路径差异和权限需求。

## 特性

- 🔧 **配置驱动**: 通过 YAML 配置文件定义安装流程，无需编写脚本
- 🐧 **多环境支持**: 支持 Ubuntu、CentOS、Alpine 等主流 Linux 发行版
- 📦 **模块化安装**: 标准化的安装流程步骤控制
- 📝 **详细日志**: 完整的日志记录，包括命令执行和安装过程
- ⚡ **环境自检**: 自动检测并安装 Python 运行环境

## 安装

克隆仓库及安装依赖：
   ```bash
   git clone https://cnb.cool/fuliai/aitools.git
   cd aitools && bash aitools.sh
   ```

将获取到的配置文件复制到 aitools/configs 目录下，然后使用以下命令安装：


## 使用方法

### 基本命令
1. 使用预设环境安装应用：

查找 configs 目录下的配置文件，使用预设环境安装应用：
   ```bash
   # 安装comfyui 使用base环境
   python -m installer install comfyui --env base

   ```

2. 使用自定义配置文件：
   ```bash
   # 安装指定配置文件 使用github环境
   python -m installer install --config configs/demo.yml -e github
   ```

3.安装comfyui插件：
安装comfyui-sonic 使用base环境
   ```bash
   python -m installer install comfyui-sonic --env base
   ```

### 配置文件示例

### 配置继承

系统支持配置文件继承机制，可以通过 `parent` 字段指定父配置文件：

```yaml
version: "1.0"
name: "comfyui-sonic"
description: "安装 ComfyUI Sonic 插件及工作流"
parent: "comfyui"  # 指定父配置文件
install:
  environments:
    base:
      # 只需要定义插件特定的配置
      repo_name: "ComfyUI_Sonic"
      plugin_repo: "https://github.com/smthemex/ComfyUI_Sonic.git"
```

#### 配置继承特性

1. **父配置引用**
   - 使用 `parent` 字段指定父配置文件
   - 父配置文件必须在同一目录下
   - 自动继承父配置的所有设置

2. **变量引用语法**
   - 使用 `{parent.xxx}` 语法引用父配置的值
   - 支持多层级引用，如 `{parent.environments.base.venv_dir}`
   - 引用的路径必须存在于父配置中

3. **配置合并规则**
   - 子配置可以覆盖父配置的值
   - 对象类型配置进行深度合并
   - 非对象类型配置直接覆盖

#### 使用示例

1. **基础配置** (comfyui.yml):
```yaml
version: "1.0"
name: "comfyui"
install:
  environments:
    base:
      base_dir: "/workspace"
      venv_dir: "venv_confyui"
      repo_name: "ComfyUI"
```

2. **插件配置** (comfyui-sonic.yml):
```yaml
version: "1.0"
name: "comfyui-sonic"
parent: "comfyui"
install:
  environments:
    base:
      repo_name: "ComfyUI_Sonic"  # 覆盖特定配置
  steps:
    - name: "安装插件"
      common:
        - |
          cd {parent.environments.base.base_dir}/{parent.environments.base.repo_name}  # 引用父配置路径
```

#### 最佳实践

1. **配置分层**
   - 基础应用使用独立配置
   - 插件和扩展通过继承复用配置
   - 只在子配置中定义特定的配置项

2. **路径管理**
   - 使用父配置中的路径配置
   - 保持路径一致性
   - 避免重复定义基础路径

3. **环境配置**
   - 继承父配置的环境设置
   - 根据需要覆盖特定环境变量
   - 保持环境配置的一致性

### 配置模板生成

使用独立配置文件生成程序来生成配置文件：

1. **查看说明**：参考 `configs/variables.md` 了解可用变量
2. **修改配置**：根据应用需求修改生成的配置文件

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
      - "uv venv {venv_dir} --python={python_ver}"
      - ". {venv_dir}/bin/activate"
      - "uv pip install --upgrade pip -i {pip_index}"
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
| {venv_dir} | 虚拟环境目录 | "venv_confyui" |
| {python_ver} | Python 版本 | "3.12.9" |
| {app_repo} | 应用仓库地址 | "https://openi.pcl.ac.cn/niubi/ComfyUI.git" |
| {repo_name} | 仓库目录名 | "ComfyUI" |
| {parent.xxx} | 父配置引用 | "{parent.environments.base.venv_dir}" |

### 自定义安装

使用 `--set` 参数覆盖配置变量：
```bash
# 基础应用安装
python -m installer install comfyui --env ubuntu-a --set base_dir=/custom/path

# 插件安装（会自动继承父配置的设置）
python -m installer install comfyui-sonic --env ubuntu-a
```

## 日志系统

安装过程的日志文件位于 `logs` 目录：

- `{app_name}_install.log`: 安装过程日志
- `{app_name}_commands.log`: 所有执行命令的详细日志
- `{app_name}_installer.log`: 安装器运行日志

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
# 配置文件变量说明

## 基础变量
| 变量名 | 说明 | 来源 | 示例 |
|--------|------|------|------|
| {name} | 应用名称 | 配置文件 | "comfyui" |
| {description} | 应用描述 | 配置文件 | "ComfyUI - Stable Diffusion WebUI" |
| {version} | 应用版本 | 配置文件 | "latest" |

## 环境变量
| 变量名 | 说明 | 默认值 | 示例 |
|--------|------|--------|------|
| {base_dir} | 安装根目录 | 环境配置 | "/opt/ai/comfyui" |
| {user} | 当前用户名 | 系统环境 | "ubuntu" |
| {use_sudo} | 是否使用sudo | false | "false" |
| {python_cmd} | Python命令 | "python3" | "python3" |

## Python/pip相关
| 变量名 | 说明 | 默认值 | 示例 |
|--------|------|--------|------|
| {pip_index} | pip镜像源 | "https://pypi.org/simple" | "https://pypi.tuna.tsinghua.edu.cn/simple" |
| {pip_timeout} | pip超时时间(秒) | 60 | 120 |
| {pip_retries} | pip重试次数 | 3 | 5 |

## 虚拟环境
| 变量名 | 说明 | 默认值 | 示例 |
|--------|------|--------|------|
| {venv_dir} | 虚拟环境目录 | "venv" | ".venv" |
| {venv_python} | 虚拟环境Python | "venv/bin/python" | ".venv/bin/python" |
| {venv_pip} | 虚拟环境pip | "venv/bin/pip" | ".venv/bin/pip" |

## 常用命令模板

### 1. 基础目录操作
```yaml
steps:
  - name: "prepare"
    description: "准备目录"
    common:
      - "mkdir -p {base_dir}"
      - "cd {base_dir}"
```

### 2. Git仓库操作
```yaml
steps:
  - name: "download"
    description: "下载源码"
    common:
      - "git clone {repo_url} {base_dir}"
      - "cd {base_dir}"
      - "git checkout {version}"
```

### 3. Python依赖安装
```yaml
steps:
  - name: "install"
    description: "安装依赖"
    common:
      - "{python_cmd} -m pip install --upgrade pip"
      - "{python_cmd} -m pip install -r requirements.txt"
```

### 4. 权限设置（需要sudo）
```yaml
steps:
  - name: "permissions"
    description: "设置权限"
    common:
      - "chown -R {user}:{user} {base_dir}"
      - "chmod -R 755 {base_dir}"
```

## 配置文件结构
```yaml
version: "1.0"
name: "{name}"
description: "{description}"

install:
  # 环境配置
  environments:
    ubuntu-a:
      base_dir: "/opt/ai/{name}"
      python_cmd: "python3"
      use_sudo: false
      pip_index: "https://pypi.org/simple"
      pip_timeout: 60
      pip_retries: 3
    github:
      base_dir: "/workspace/{name}"
      python_cmd: "python"
      use_sudo: false
      pip_index: "https://pypi.org/simple"
      pip_timeout: 60
      pip_retries: 3

  # 安装步骤
  steps:
    - name: "step-name"
      description: "步骤描述"
      common:
        - "命令1"
        - "命令2"
```

## 使用说明

1. 安装命令格式：
```bash
python -m installer install <app_name> --env <environment>
```

2. 使用配置文件：
```bash
python -m installer install --config configs/app.yml --env github
```

3. 覆盖变量：
```bash
python -m installer install app --env github --set base_dir=/custom/path --set python_cmd=python3.8
```

## 注意事项

1. 所有变量都使用 `{var_name}` 格式引用
2. 环境配置中的变量会自动替换到步骤命令中
3. 可以使用 `--set` 参数覆盖任何配置变量
4. 配置文件必须包含 `install.environments` 和 `install.steps` 两个部分

## 使用技巧

1. **条件执行**
   ```yaml
   - "if [ {use_sudo} = true ]; then sudo mkdir -p {base_dir}; else mkdir -p {base_dir}; fi"
   ```

2. **变量组合**
   ```yaml
   - "export PYTHONPATH={base_dir}/src:$PYTHONPATH"
   ```

3. **多行命令**
   ```yaml
   - |
     cd {base_dir} && \
     {venv_pip} install -r requirements.txt -i {pip_index} && \
     {venv_python} setup.py install
   ```

4. **环境检查**
   ```yaml
   - "{python_cmd} -c 'import sys; assert sys.version_info >= (3, 8)'"
   ```
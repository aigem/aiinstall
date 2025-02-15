# 配置文件变量说明

## 基础变量
| 变量名 | 说明 | 来源 | 示例 |
|--------|------|------|------|
| {name} | 应用名称 | 配置文件 | "comfyui" |
| {version} | 应用版本 | 配置文件 | "latest" |

## 环境变量
| 变量名 | 说明 | 默认值 | 示例 |
|--------|------|--------|------|
| {base_dir} | 安装根目录 | 环境配置 | "/home/user/ai_apps/comfyui" |
| {user} | 当前用户名 | 系统环境 | "ubuntu" |
| {use_sudo} | 是否使用sudo | 环境配置 | "true" |
| {python_cmd} | Python命令 | "python3" | "python3.10" |

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

### 1. 创建目录
```yaml
- "mkdir -p {base_dir}"
- "cd {base_dir}"
```

### 2. 权限设置
```yaml
- "sudo chown -R {user}:{user} {base_dir}"
- "chmod -R 755 {base_dir}"
```

### 3. Python环境
```yaml
- "{python_cmd} -m venv {venv_dir}"
- "{venv_pip} install --upgrade pip -i {pip_index}"
- "{venv_pip} install -r requirements.txt -i {pip_index}"
```

### 4. Git操作
```yaml
- "git clone https://github.com/user/repo.git src"
- "cd src && git checkout {version}"
```

### 5. 常见依赖安装
```yaml
- "{venv_pip} install torch torchvision --index-url {pip_index}"
- "{venv_pip} install -r src/requirements.txt -i {pip_index}"
```

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

## 注意事项

1. 所有变量都使用 `{var_name}` 格式引用
2. 可以在命令中使用shell特性（如 &&、||、|）
3. 对于长命令，可以使用YAML的 `|` 或 `>` 语法
4. 需要注意路径中的引号和转义字符 
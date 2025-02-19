"""配置加载和验证模块"""
from typing import Dict, Any, Optional
import yaml
from pathlib import Path

class ConfigError(Exception):
    """配置相关错误"""
    pass

def deep_merge(base: Dict, override: Dict) -> Dict:
    """深度合并两个字典，override的值会覆盖base的值"""
    result = base.copy()
    for key, value in override.items():
        if key in result and isinstance(result[key], dict) and isinstance(value, dict):
            result[key] = deep_merge(result[key], value)
        else:
            result[key] = value
    return result

def resolve_parent_refs(data: Dict[str, Any], parent_data: Dict[str, Any]) -> Dict[str, Any]:
    """解析配置中的父配置引用，支持 {parent.xxx} 语法"""
    def _get_value_from_path(path_parts: list, data: dict) -> Any:
        """从嵌套字典中获取值"""
        current = data
        for part in path_parts:
            if not isinstance(current, dict):
                raise ConfigError(f"无法访问路径 '{'.'.join(path_parts)}'，'{part}' 的父节点不是字典")
            if part not in current:
                available = list(current.keys())
                raise ConfigError(f"键 '{part}' 不存在，可用的键: {available}")
            current = current[part]
        return current

    def _resolve_value(value):
        if isinstance(value, str):
            # 处理包含父配置引用的字符串
            while "{parent." in value:
                start = value.find("{parent.")
                end = value.find("}", start)
                if end == -1:
                    raise ConfigError(f"无效的父配置引用格式: {value}")
                    
                ref = value[start:end+1]
                ref_path = ref.strip("{}").split(".")[1:]  # 移除 'parent' 前缀
                
                try:
                    # 获取父配置值
                    current = _get_value_from_path(ref_path, parent_data)
                    
                    # 将引用替换为实际值
                    if isinstance(current, (dict, list)):
                        current = str(current)
                    elif current is None:
                        raise ConfigError(f"父配置引用 '{ref}' 的值为 None")
                    value = value.replace(ref, str(current))
                except ConfigError as e:
                    raise ConfigError(f"解析父配置引用 '{ref}' 时出错: {str(e)}")
            return value
        elif isinstance(value, dict):
            return {k: _resolve_value(v) for k, v in value.items()}
        elif isinstance(value, list):
            return [_resolve_value(item) for item in value]
        return value
    
    return _resolve_value(data)

class Config:
    """配置类"""
    def __init__(self, data: Dict[str, Any], env: str, parent: Optional['Config'] = None):
        # 基础验证
        if not isinstance(data, dict):
            raise ConfigError("配置数据必须是字典类型")
            
        self.raw_data = data
        self.env = env
        self.version = data.get('version')
        self.name = data.get('name')
        self.description = data.get('description')
        
        # 验证基本字段
        if not all([self.version, self.name]):
            raise ConfigError("配置文件必须包含 version 和 name 字段")
            
        # 处理父配置
        if parent:
            try:
                # 确保父配置数据正确
                if not isinstance(parent.raw_data, dict):
                    raise ConfigError(f"父配置数据无效: {type(parent.raw_data)}")
                
                # 先解析父配置引用
                resolved_data = resolve_parent_refs(data, parent.raw_data)
                
                # 然后合并配置
                self.data = deep_merge(parent.raw_data, resolved_data)
            except ConfigError as e:
                # 添加调试信息
                debug_info = (
                    f"\n父配置结构:\n{parent.raw_data}\n"
                    f"当前配置结构:\n{data}\n"
                    f"环境: {env}"
                )
                raise ConfigError(f"处理父配置时出错: {str(e)}{debug_info}")
        else:
            self.data = data
            
        # 处理环境配置
        self.environments = self.data.get('install', {}).get('environments', {})
        if not self.environments:
            raise ConfigError("配置文件必须包含环境配置")
            
        if env not in self.environments:
            raise ConfigError(f"环境 {env} 未在配置文件中定义")
            
        self.current_env = self.environments[env]
        self.steps = self.data.get('install', {}).get('steps', [])
        
    def get_merged_env(self) -> Dict[str, Any]:
        """获取合并后的环境配置"""
        base_env = self.environments.get('base', {})
        if self.env != 'base':
            return deep_merge(base_env, self.current_env)
        return base_env

def load_config(config_path: str, env: str = 'base') -> Config:
    """加载并验证配置文件"""
    path = Path(config_path)
    if not path.exists():
        raise ConfigError(f"配置文件 {config_path} 不存在")
        
    try:
        with path.open('r', encoding='utf-8') as f:
            data = yaml.safe_load(f)
    except yaml.YAMLError as e:
        raise ConfigError(f"配置文件格式错误: {e}")
        
    # 处理父配置
    parent_config = None
    if 'parent' in data:
        parent_name = data['parent']
        parent_path = path.parent / f"{parent_name}.yml"
        if not parent_path.exists():
            raise ConfigError(f"父配置文件 {parent_path} 不存在")
        parent_config = load_config(str(parent_path), env)
    
    # 验证版本
    validate_version(data.get('version'))
        
    return Config(data, env, parent_config)

def validate_version(version: str) -> bool:
    """验证配置文件版本"""
    SUPPORTED_VERSIONS = ['1.0']
    if version not in SUPPORTED_VERSIONS:
        raise ConfigError(f"不支持的配置文件版本 {version}，支持的版本: {SUPPORTED_VERSIONS}")
    return True 
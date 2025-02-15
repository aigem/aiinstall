"""配置加载和验证模块"""
from typing import Dict, Any
import yaml
from pathlib import Path

class ConfigError(Exception):
    """配置相关错误"""
    pass

class Config:
    """配置类"""
    def __init__(self, data: Dict[str, Any], env: str):
        self.data = data
        self.env = env
        self.version = data.get('version')
        self.name = data.get('name')
        self.description = data.get('description')
        
        if not all([self.version, self.name]):
            raise ConfigError("配置文件必须包含 version 和 name 字段")
            
        self.environments = data.get('install', {}).get('environments', {})
        if not self.environments:
            raise ConfigError("配置文件必须包含环境配置")
            
        if env not in self.environments:
            raise ConfigError(f"环境 {env} 未在配置文件中定义")
            
        self.current_env = self.environments[env]
        self.steps = data.get('install', {}).get('steps', [])

def load_config(config_path: str, env: str) -> Config:
    """加载并验证配置文件"""
    path = Path(config_path)
    if not path.exists():
        raise ConfigError(f"配置文件 {config_path} 不存在")
        
    try:
        with path.open('r', encoding='utf-8') as f:
            data = yaml.safe_load(f)
    except yaml.YAMLError as e:
        raise ConfigError(f"配置文件格式错误: {e}")
        
    return Config(data, env)

def validate_version(version: str) -> bool:
    """验证配置文件版本"""
    SUPPORTED_VERSIONS = ['1.0']
    if version not in SUPPORTED_VERSIONS:
        raise ConfigError(f"不支持的配置文件版本 {version}，支持的版本: {SUPPORTED_VERSIONS}")
    return True 
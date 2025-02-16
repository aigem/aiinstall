"""安装流程控制模块"""
import os
import logging
from typing import Dict, Any
from pathlib import Path
from .config import Config
from .executor import CommandExecutor, ExecutionError

class InstallError(Exception):
    """安装错误"""
    pass

class Installer:
    """安装器"""
    def __init__(self, config: Config):
        self.config = config
        self.logger = logging.getLogger('installer')
        self.executor = CommandExecutor()
        
    def install(self):
        """执行安装流程"""
        self.logger.info(f"开始安装 {self.config.name}")
        self.logger.info(f"环境: {self.config.env}")
        
        # 准备变量
        variables = self._prepare_variables()
        
        # 设置工作目录
        base_dir = variables['base_dir']
        self.executor.working_dir = base_dir
        
        try:
            # 执行安装步骤
            for step in self.config.steps:
                self._execute_step(step, variables)
                
            # 显示完成信息
            self._show_completion_message(variables)
            
        except ExecutionError as e:
            raise InstallError(f"安装失败: {e.message}\n命令: {e.command}")
            
    def _prepare_variables(self) -> Dict[str, str]:
        """准备变量字典"""
        variables = {
            'name': self.config.name,
            'env_name': self.config.env,
            'base_dir': self.config.current_env['base_dir'],
            'python_cmd': self.config.current_env['python_cmd'],
            'use_sudo': str(self.config.current_env['use_sudo']).lower(),
        }
        
        # 添加所有环境变量
        variables.update(self.config.current_env)
        
        # 添加额外环境变量
        env_vars = self.config.current_env.get('env_vars', {})
        variables.update(env_vars)
        
        return variables
        
    def _execute_step(self, step: Dict[str, Any], variables: Dict[str, str]):
        """执行单个安装步骤"""
        # 步骤开始提示
        self.logger.info(f"\n▶▶ 开始步骤: {step['name']}")
        if step.get('description'):
            self.logger.info(f"  说明: {step['description']}")
        
        # 执行步骤
        self.executor.execute_step(step, self.config.env, variables)
        
        # 步骤完成提示
        self.logger.info(f"✓✓ 完成步骤: {step['name']}\n{'-'*40}")
        
    def _show_completion_message(self, variables: Dict[str, str]):
        """显示安装完成信息"""
        if 'startup' in self.config.data:
            startup = self.config.data['startup']
            if 'post_install_message' in startup:
                message = startup['post_install_message']
                # 替换变量
                for key, value in variables.items():
                    message = message.replace(f"{{{key}}}", str(value))
                print("\n" + message) 
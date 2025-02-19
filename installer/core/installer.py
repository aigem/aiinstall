"""安装流程控制模块"""
import os
import logging
from typing import Dict, Any
from pathlib import Path
from .config import Config
from .executor import CommandExecutor, ExecutionError
import textwrap

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
        # 显示安装前提示
        print("\033[1;36m" + "="*50 + "\033[0m")
        print("\033[1;32m📢 安装前重要提示\033[0m")
        print("\033[1;36m" + "-"*50 + "\033[0m")
        print(textwrap.dedent("""
        \033[33m1. 请配合视频教程使用本安装程序
        https://www.bilibili.com/video/BV13UBRYVEmX/
        2. 安装过程中如无报错，耐心等待直到安装完成\033[0m
        """))
        print("\033[1;36m" + "="*50 + "\033[0m")
        
        # 等待用户确认
        confirm = input("\033[1;31m是否开始安装？(Y/n) \033[0m").strip().lower()
        if confirm not in ('y', ''):
            print("\033[33m安装已取消\033[0m")
            return

        # 原有安装流程
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
            'app_name': self.config.name,
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
        try:
            # 清屏操作
            print("\033c", end="")  # ANSI 转义码清屏，兼容更多终端
            
            # 检查说明文件是否存在
            manual_path = Path(variables.get('base_dir', '')) / f"{variables.get('repo_name', '')}使用说明.txt"
            
            # 构建提示信息
            msg_parts = []
            
            # 如果说明文件存在，添加说明文件提示
            if manual_path.exists():
                msg_parts.append(f"""
                \033[33m使用说明文件：\033[0m
                {manual_path}""")
            
            # 添加日志路径提示
            log_path = Path(variables.get('base_dir', '')) / 'aitools/logs'
            msg_parts.append(f"""
                \033[33m安装日志位置：\033[0m
                {log_path}
                运行以下命令查看详细日志：
                \033[36mcat {log_path}/{variables.get('app_name', '*')}_install.log\033[0m   # 安装过程日志
                \033[36mcat {log_path}/{variables.get('app_name', '*')}_commands.log\033[0m  # 命令执行日志
                \033[36mcat {log_path}/{variables.get('app_name', '*')}_installer.log\033[0m # 安装器日志""")
            
            # 添加在线文档链接
            if variables.get('info_url'):
                msg_parts.append(f"""
                \033[33m最新使用说明请访问：\033[0m
                \033[4;34m{variables.get('info_url')}\033[0m""")
            
            # 合并所有提示信息
            msg = "\n".join(msg_parts)
            
            # 显示完成信息
            print("\033[1;36m" + "="*50 + "\033[0m")
            print("\033[1;32m📢 安装完成！✅\033[0m")
            print("\033[1;36m" + "-"*50 + "\033[0m")
            print(textwrap.dedent(msg))
            print("\033[1;36m" + "="*50 + "\033[0m")
            
        except Exception as e:
            self.logger.error(f"生成完成提示失败: {str(e)}") 
        
        
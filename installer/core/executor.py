"""命令执行器模块"""
import subprocess
import logging
from typing import List, Dict, Any
from pathlib import Path

class ExecutionError(Exception):
    """命令执行错误"""
    def __init__(self, message: str, command: str, return_code: int = None):
        self.message = message
        self.command = command
        self.return_code = return_code
        super().__init__(message)

class CommandExecutor:
    """命令执行器"""
    def __init__(self, working_dir: str = None):
        self.working_dir = working_dir
        self.logger = logging.getLogger('command')
        
    def execute(self, command: str, env: Dict[str, str] = None) -> str:
        """执行单个命令（支持多行）并实时输出"""
        self.logger.info(f"执行命令: {command}")
        
        try:
            process = subprocess.Popen(
                command,
                shell=True,
                cwd=self.working_dir,
                env=env,
                executable='/bin/bash',
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                text=True
            )

            # 实时输出并记录日志
            full_output = []
            for line in iter(process.stdout.readline, ''):
                self.logger.info(line.strip())
                full_output.append(line)
                print(line, end='')  # 实时打印到控制台

            process.wait()
            
            if process.returncode != 0:
                raise ExecutionError(
                    f"命令执行失败: {''.join(full_output)}",
                    command,
                    process.returncode
                )
                
            return ''.join(full_output).strip()
            
        except subprocess.SubprocessError as e:
            raise ExecutionError(f"命令执行异常: {str(e)}", command)
            
    def execute_step(self, step: Dict[str, Any], env_name: str, variables: Dict[str, str]):
        """执行安装步骤"""
        # 执行通用命令
        common_commands = step.get('common', [])
        for cmd in common_commands:
            self.execute(self._replace_variables(cmd, variables))
            
        # 执行环境特定命令
        env_commands = step.get(env_name, [])
        for cmd in env_commands:
            self.execute(self._replace_variables(cmd, variables))
            
    def _replace_variables(self, command: str, variables: Dict[str, str]) -> str:
        """替换命令中的变量"""
        result = command
        for key, value in variables.items():
            result = result.replace(f"{{{key}}}", str(value))
        return result 
"""命令行入口模块"""
import click
from pathlib import Path
from typing import Dict
from .core.config import load_config, ConfigError
from .core.installer import Installer, InstallError
from .core.logger import setup_logging

@click.group()
def cli():
    """AI应用安装工具"""
    pass

@cli.command()
@click.argument('app_name', required=False)
@click.option('--config', '-c', help='配置文件路径')
@click.option('--env', '-e', required=True, help='目标环境')
@click.option('--set', multiple=True, help='覆盖配置变量，格式: key=value')
def install(app_name: str, config: str, env: str, set: tuple):
    """安装应用"""
    try:
        # 处理配置文件路径
        if config:
            config_path = config
        elif app_name:
            config_path = f"configs/{app_name}.yml"
        else:
            raise click.UsageError("必须指定应用名称或配置文件路径")
            
        # 设置日志
        app_name = app_name or Path(config_path).stem
        setup_logging(app_name)
        
        # 加载配置
        config = load_config(config_path, env)
        
        # 处理变量覆盖
        overrides = {}
        for item in set:
            if '=' not in item:
                raise click.UsageError(f"变量设置格式错误: {item}")
            key, value = item.split('=', 1)
            overrides[key] = value
            
        # 执行安装
        installer = Installer(config)
        installer.install()
        
    except (ConfigError, InstallError) as e:
        click.echo(f"错误: {str(e)}", err=True)
        raise click.Abort()
        
@cli.command()
@click.argument('config_file')
def validate(config_file: str):
    """验证配置文件"""
    try:
        # 加载并验证配置文件
        config = load_config(config_file, 'ubuntu-a')  # 使用默认环境验证
        click.echo(f"配置文件 {config_file} 验证通过")
        
    except ConfigError as e:
        click.echo(f"配置文件验证失败: {str(e)}", err=True)
        raise click.Abort()

@cli.command()
@click.argument('name')
@click.option('--description', '-d', help='应用描述')
@click.option('--repo-url', '-r', help='Git仓库地址')
@click.option('--version', '-v', default='latest', help='应用版本')
@click.option('--port', '-p', type=int, help='应用端口号')
@click.option('--docs-url', help='文档URL')
def generate_config(name: str, description: str, repo_url: str, version: str,
                   port: int, docs_url: str):
    """生成应用配置模板"""
    try:
        # 读取模板
        template_path = Path(__file__).parent / 'templates' / 'app_template.yml'
        with template_path.open('r', encoding='utf-8') as f:
            template = f.read()
            
        # 替换变量
        config = template.format(
            name=name,
            description=description or f"{name}应用",
            repo_url=repo_url or "https://github.com/user/repo.git",
            version=version,
            port=port or 8188,
            docs_url=docs_url or "#"
        )
        
        # 写入配置文件
        config_path = Path('configs') / f"{name}.yml"
        config_path.parent.mkdir(exist_ok=True)
        with config_path.open('w', encoding='utf-8') as f:
            f.write(config)
            
        click.echo(f"配置模板已生成: {config_path}")
        click.echo("请根据实际需求修改配置文件。")
        click.echo(f"可参考 configs/variables.md 了解可用变量。")
        
    except Exception as e:
        click.echo(f"生成配置模板失败: {str(e)}", err=True)
        raise click.Abort()

if __name__ == '__main__':
    cli() 
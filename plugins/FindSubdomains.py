# plugins\FindSubdomains.py
import os  
import sys  
import shutil  
import concurrent.futures  
import logging  
import subprocess  
from .PluginRegistry import Plugin, register_plugin

@register_plugin('findsubdomain')  
class FindSubdomains(Plugin):  
    """  
    子域名发现插件：使用多种工具并行查找子域名  
    """  

    def __init__(self):  
        """  
        初始化插件，定义要使用的工具列表  
        """  
        self.tools = ["amass", "assetfinder", "subfinder", "theHarvester"]

    def execute(self, domain, output):
        """
        执行子域名发现的主要逻辑

        参数:
        domain (str): 要查找子域名的主域名
        output (str): 输出结果的文件路径
        """
        # 检查所有必要工具是否安装
        for tool in self.tools:
            self.check_tool(tool)

            # 创建临时目录存储各工具的输出
        temp_dir = f"temp_{domain}"
        os.makedirs(temp_dir, exist_ok=True)

        # 定义每个工具的命令
        commands = {
            "amass": f"amass enum --passive -d {domain}",
            "assetfinder": f"assetfinder --subs-only {domain}",
            "subfinder": f"subfinder -d {domain}",
            "theHarvester": f"theHarvester -b all -d {domain} --dns-lookup --dns-brute"
        }

        # 使用线程池并行执行所有工具
        with concurrent.futures.ThreadPoolExecutor() as executor:
            futures = [executor.submit(self.run_tool, name, command, domain, temp_dir)
                       for name, command in commands.items()]
            for future in concurrent.futures.as_completed(futures):
                future.result()

                # 合并结果并去重
        unique_domains = self.merge_results(temp_dir, domain)
        # 将结果写入输出文件
        self.write_results(unique_domains, output)

        # 清理临时目录
        shutil.rmtree(temp_dir)
        logging.info(f"发现的唯一子域名数量: {len(unique_domains)}")
        logging.info(f"完成！结果保存在 {output}")
    def check_tool(self, tool_name):  
        """  
        检查指定的工具是否已安装  

        参数:  
        tool_name (str): 要检查的工具名称  
        """  
        if shutil.which(tool_name) is None:  
            logging.error(f"工具 {tool_name} 未安装，请先安装它。")  
            sys.exit(1)  

    def run_tool(self, name, command, domain, temp_dir):  
        """  
        运行单个子域名发现工具  

        参数:  
        name (str): 工具名称  
        command (str): 要执行的命令  
        domain (str): 目标域名  
        temp_dir (str): 临时输出目录  
        """  
        logging.info(f"运行 {name}...")  
        try:  
            result = subprocess.run(command, shell=True, capture_output=True, text=True, check=True)  
            with open(f"{temp_dir}/{name}.txt", "w") as f:  
                for line in result.stdout.splitlines():  
                    cleaned_line = self.clean_subdomain(line.strip(), domain)  
                    if cleaned_line:  
                        f.write(cleaned_line + "\n")  
        except subprocess.CalledProcessError as e:  
            logging.error(f"{name} 执行失败，请检查工具配置。错误信息: {e}")  

    def clean_subdomain(self, subdomain, domain):  
        """  
        清理和验证子域名  

        参数:  
        subdomain (str): 待清理的子域名  
        domain (str): 主域名  

        返回:  
        str: 清理后的子域名，如果无效则返回None  
        """  
        if subdomain.startswith("*."):  
            subdomain = subdomain[2:]  
        if subdomain.endswith(":"):  
            subdomain = subdomain[:-1]  
        return subdomain if domain in subdomain else None  

    def merge_results(self, temp_dir, domain):  
        """  
        合并所有工具的结果并去重  

        参数:  
        temp_dir (str): 临时文件目录  
        domain (str): 主域名  

        返回:  
        list: 排序后的唯一子域名列表  
        """  
        unique_domains = set()  
        for filename in os.listdir(temp_dir):  
            with open(os.path.join(temp_dir, filename), "r") as infile:  
                for line in infile:  
                    cleaned_line = self.clean_subdomain(line.strip(), domain)  
                    if cleaned_line:  
                        unique_domains.add(cleaned_line)  
        return sorted(unique_domains)  

    def write_results(self, domains, output_file):  
        """  
        将结果写入输出文件  

        参数:  
        domains (list): 子域名列表  
        output_file (str): 输出文件路径  
        """  
        with open(output_file, "w") as outfile:  
            for domain in domains:  
                outfile.write(domain + "\n")

    @classmethod
    def add_arguments(cls, parser):
        parser.add_argument('-d', '--domain', required=True, help='要查找子域名的主域名')
        parser.add_argument('-o', '--output', required=True, help='输出结果的文件路径')

    @classmethod
    def print_usage(cls):
        print("""  
    FindSubdomains 插件使用说明  

    描述:  
    FindSubdomains 插件使用多种工具并行查找给定域名的子域名。  

    用法:  
    python3 main.py findsubdomain -d <domain> -o <output_file>  

    参数:  
    -d, --domain: 要查找子域名的主域名（必需）  
    -o, --output: 输出结果的文件路径（必需）  

    示例:  
    python3 main.py findsubdomain -d example.com -o subdomains.txt  

    工具依赖:  
    此插件依赖以下外部工具，请确保它们已安装并可在系统路径中访问：  
    - amass  
    - assetfinder  
    - subfinder  
    - theHarvester  

    注意事项:  
    1. 确保您有足够的权限运行这些工具和写入输出文件。  
    2. 该过程可能需要一些时间，具体取决于目标域名的规模。  
    3. 请遵守相关法律法规和目标网站的使用政策。  

    输出:  
    插件将在指定的输出文件中生成一个唯一子域名的列表，每行一个子域名。  

    错误处理:  
    如果任何必需的工具未安装，插件将报错并退出。请检查错误消息并安装缺失的工具。  
        """)
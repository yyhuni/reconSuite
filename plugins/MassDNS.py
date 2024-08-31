

import json
import subprocess
import logging
import os
import requests
from .PluginRegistry import Plugin, register_plugin

# 定义解析器文件的路径
RESOLVERS_PATH = '/usr/lib/python3/dist-packages/theHarvester/lib/resolvers.txt'
RESOLVERS_URL = 'https://raw.githubusercontent.com/laramies/theHarvester/6059f78c52901b0a925c486793c252f011a3fe9b/theHarvester/lib/resolvers.txt'

@register_plugin('massdns')
class MassDNS(Plugin):
    """
    MassDNS插件：用于批量DNS解析和子域名枚举
    """

    def execute(self, domain_list, output_file, output_format='full'):
        """
        执行MassDNS插件的主要逻辑

        参数:
        domain_list (str): 包含域名列表的文件路径
        output_file (str): 输出结果的文件路径
        output_format (str): 输出格式，可选 'full', 'domain', 或 'ip'
        """
        # 确保resolvers.txt文件存在
        self.ensure_resolvers_file()

        # 从文件读取域名列表
        domains = self.read_domains_from_file(domain_list)
        if not domains:
            logging.error("No domains to process.")
            return

        # 执行MassDNS命令并获取输出
        lines = self.execute_massdns(domains)
        # 解析MassDNS输出
        results = self.parse_massdns_output(lines)
        # 将结果写入文件
        self.write_results_to_file(results, output_file, output_format)

    def ensure_resolvers_file(self):
        """
        确保resolvers.txt文件存在，如果不存在则从GitHub下载
        """
        if not os.path.exists(RESOLVERS_PATH):
            logging.info(f"Resolvers file not found. Downloading from {RESOLVERS_URL}")
            try:
                response = requests.get(RESOLVERS_URL)
                response.raise_for_status()
                with open(RESOLVERS_PATH, 'w') as file:
                    file.write(response.text)
                logging.info(f"Resolvers file downloaded and saved to {RESOLVERS_PATH}")
            except requests.RequestException as e:
                logging.error(f"Failed to download resolvers file: {e}")
                raise

    def execute_massdns(self, domains):
        """
        执行MassDNS命令

        参数:
        domains (list): 要解析的域名列表

        返回:
        list: MassDNS命令的输出行列表
        """
        massdns_cmd = [
            'massdns',
            '-s', '15000',  # 每秒最大解析数
            '-t', 'A',      # 查询类型为A记录
            '-o', 'J',      # 输出格式为JSON
            '-r', RESOLVERS_PATH,  # 使用指定的解析器文件
            '--flush'       # 立即刷新输出
        ]
        try:
            # 将域名列表转换为字符串并编码
            domains_str = '\n'.join(domains).encode('utf-8')
            # 使用subprocess执行MassDNS命令
            proc = subprocess.Popen(massdns_cmd, stdout=subprocess.PIPE, stderr=subprocess.DEVNULL, stdin=subprocess.PIPE)
            stdout, _ = proc.communicate(input=domains_str)
            # 返回解码后的输出行
            return [line.decode('utf-8').strip() for line in stdout.splitlines()]
        except Exception as e:
            logging.error(f"Error executing massdns: {e}")
            return []

    def parse_massdns_output(self, lines):
        """
        解析MassDNS的JSON输出

        参数:
        lines (list): MassDNS输出的行列表

        返回:
        list: 解析后的结果列表，每项为(域名, IP地址列表)的元组
        """
        processed = []
        for line in lines:
            if line:
                try:
                    json_data = json.loads(line)
                    if json_data.get('status') == 'NOERROR':
                        domain_name = json_data.get('name').rstrip('.')
                        answers = json_data.get('data', {}).get('answers', [])
                        a_records = [answer['data'] for answer in answers if answer.get('type') == 'A']
                        if a_records:
                            processed.append((domain_name, a_records))
                except json.JSONDecodeError:
                    logging.error(f"Error decoding JSON: {line}")
        return processed

    def read_domains_from_file(self, file_path):
        """
        从文件中读取域名列表

        参数:
        file_path (str): 域名列表文件的路径

        返回:
        list: 读取到的域名列表
        """
        try:
            with open(file_path, 'r', encoding='utf-8') as file:
                return [line.strip() for line in file if line.strip()]
        except FileNotFoundError:
            logging.error(f"File not found: {file_path}")
            return []
        except IOError as e:
            logging.error(f"IO error: {e}")
            return []

    def write_results_to_file(self, results, output_file, output_format):
        """
        将结果写入输出文件

        参数:
        results (list): 解析结果列表
        output_file (str): 输出文件路径
        output_format (str): 输出格式
        """
        with open(output_file, 'w', encoding='utf-8') as f:
            for domain, ips in results:
                if output_format == 'domain':
                    f.write(f"{domain}\n")
                elif output_format == 'ip':
                    for ip in ips:
                        f.write(f"{ip}\n")
                else:  # full format
                    ips_str = ", ".join(ips)
                    f.write(f'domain: {domain} | ip: {ips_str}\n')

    @classmethod
    def add_arguments(cls, parser):
        parser.add_argument('-l', '--domain-list', required=True, help='包含域名列表的文件路径')
        parser.add_argument('-o', '--output', required=True, help='输出结果的文件路径')
        parser.add_argument('--output-format', choices=['full', 'domain', 'ip'], default='full',
                            help='输出格式: full (默认), domain, 或 ip')

    @classmethod
    def print_usage(cls):
        print("""
    MassDNS 插件使用说明

    描述:
    MassDNS 插件用于批量 DNS 解析和子域名枚举。它利用 MassDNS 工具的高性能特性，能够快速处理大量域名。

    用法:
    python3 main.py massdns -l <domain_list> -o <output_file> [--output-format FORMAT]

    参数:
    -l, --domain-list   必需，包含待解析域名列表的文件路径
    -o, --output        必需，解析结果的输出文件路径
    --output-format     可选，输出格式，默认为 'full'
                        可选值: full, domain, ip

    输出格式说明:
    full:   显示完整信息，格式为 'domain: <域名> | ip: <IP地址列表>'
    domain: 仅显示解析成功的域名
    ip:     仅显示解析得到的 IP 地址

    示例:
    1. 使用默认输出格式:
       python3 main.py massdns -l domains.txt -o results.txt

    2. 指定输出格式为仅域名:
       python3 main.py massdns -l domains.txt -o results.txt --output-format domain

    3. 指定输出格式为仅 IP:
       python3 main.py massdns -l domains.txt -o results.txt --output-format ip

    注意事项:
    - 确保 MassDNS 已正确安装并可在命令行中使用。
    - 插件会自动下载并使用最新的 resolvers.txt 文件。
    - 大量域名解析可能需要较长时间，请耐心等待。
    - 输出文件将会覆盖已存在的同名文件。
    - 插件使用 JSON 格式解析 MassDNS 的输出，仅处理状态为 'NOERROR' 的记录。
    - 每秒最大解析数设置为 15000，可以根据需要在代码中调整。

    错误处理:
    - 如果输入文件不存在或无法读取，插件将记录错误并返回空列表。
    - JSON 解析错误会被记录，但不会中断整个处理过程。

    依赖:
    - MassDNS 工具
    - Python 3
    - subprocess 模块
    - json 模块
    - requests 模块（用于下载 resolvers.txt）
        """)


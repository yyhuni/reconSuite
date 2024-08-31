

import os
import importlib
import sys
import logging
import argparse

def print_basic_usage(plugins):
    print("\nReconSuite - 一个侦察工具包")
    print("\n可用插件:")
    for name in plugins:
        print(f"  {name}")
    print("\n使用方法:")
    print("  python3 main.py <command> [arguments]")
    print("  要查看特定插件的详细用法，请使用:")
    print("  python3 main.py <command> --help")
    print("\n示例:")
    print("  python3 main.py findsubdomain [arguments]")
    print("\n全局选项:")
    print("  -h, --help     显示此帮助信息")
    print("  -v, --verbose  显示详细的调试信息")

def load_plugins():
    plugins = {}
    plugin_dir = './plugins'
    logging.debug(f"正在搜索插件目录: {plugin_dir}")
    for filename in os.listdir(plugin_dir):
        if filename.endswith('.py') and not filename.startswith('__'):
            module_name = filename[:-3]
            logging.debug(f"尝试导入模块: {module_name}")
            try:
                module = importlib.import_module(f'plugins.{module_name}')
                for attr_name in dir(module):
                    attr = getattr(module, attr_name)
                    if isinstance(attr, type) and getattr(attr, '_is_plugin', False):
                        plugins[attr._plugin_name] = attr
                        logging.debug(f"找到插件: {attr._plugin_name}")
            except Exception as e:
                logging.error(f"加载模块 {module_name} 时出错: {str(e)}")
    logging.debug(f"已加载 {len(plugins)} 个插件: {list(plugins.keys())}")
    return plugins

def main():
    parser = argparse.ArgumentParser(add_help=False)
    parser.add_argument('-v', '--verbose', action='store_true', help='显示详细的调试信息')
    parser.add_argument('command', nargs='?', help='要执行的插件命令')
    args, unknown = parser.parse_known_args()

    log_level = logging.DEBUG if args.verbose else logging.INFO
    logging.basicConfig(level=log_level, format='%(levelname)s: %(message)s')

    plugins = load_plugins()

    if args.command is None or args.command in ['-h', '--help']:
        print_basic_usage(plugins)
        return

    if args.command not in plugins:
        print(f"错误: 未知命令 '{args.command}'")
        print_basic_usage(plugins)
        return

    plugin_class = plugins[args.command]
    plugin_instance = plugin_class()

    # 检查插件特定的帮助参数
    if '-h' in unknown or '--help' in unknown:
        plugin_instance.print_usage()
        return

    try:
        # 执行插件
        plugin_instance.execute(unknown)
    except TypeError as e:
        logging.error(f"执行插件 '{args.command}' 时参数错误: {str(e)}")
        print(f"\n错误: 运行 '{args.command}' 插件时可能缺少必要的参数或参数类型不正确。")
        print("请检查您的输入并重试。使用以下命令查看该插件的帮助信息：")
        print(f"python3 main.py {args.command} --help\n")
        plugin_instance.print_usage()
    except Exception as e:
        logging.error(f"执行插件 '{args.command}' 时出错: {str(e)}")
        print(f"\n错误: 运行插件时发生未预期的错误。请检查您的输入并重试。")
        print("如果问题持续存在，请使用 -v 或 --verbose 选项运行命令以获取更多调试信息。")
        print("或者联系支持团队寻求帮助。\n")

if __name__ == "__main__":
    main()


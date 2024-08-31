# plugins\example_plugin.py
import logging  
from .PluginRegistry import register_plugin, Plugin  

# 使用装饰器注册插件到插件注册表中，插件名称为 'wordcount'  
#@register_plugin('wordcount')
class example_plugin(Plugin):  
    # 执行插件的主要功能  
    def execute(self, file_path):  
        """  
        读取指定文件并统计其中的单词数量。  

        参数:  
        file_path (str): 要读取的文件路径。  

        功能:  
        - 打开并读取文件内容。  
        - 计算文本中的单词数量。  
        - 将结果记录到日志中。  

        错误处理:  
        - 如果文件未找到，记录错误信息。  
        - 如果读取文件时发生IO错误，记录错误信息。  
        """  
        try:  
            # 尝试打开指定的文件并读取内容  
            with open(file_path, 'r', encoding='utf-8') as file:  
                text = file.read()  
                # 计算文件中的单词数量  
                word_count = self.count_words(text)  
                # 记录单词数量到日志  
                logging.info(f"文件 {file_path} 中的单词数量: {word_count}")  
        except FileNotFoundError:  
            # 如果文件未找到，记录错误信息  
            logging.error(f"文件未找到: {file_path}")  
        except IOError as e:  
            # 如果读取文件时发生IO错误，记录错误信息  
            logging.error(f"读取文件时出错: {e}")  

    # 辅助方法，用于计算文本中的单词数量  
    def count_words(self, text):  
        """  
        计算给定文本中的单词数量。  

        参数:  
        text (str): 要计算的文本。  

        返回:  
        int: 文本中的单词数量。  
        """  
        # 将文本按空格分割为单词列表，并返回单词数量  
        words = text.split()  
        return len(words)  

    # 类方法，用于向命令行解析器添加插件特定的参数  
    @classmethod  
    def add_arguments(cls, parser):  
        """  
        为插件添加命令行参数。  

        参数:  
        parser (argparse.ArgumentParser): 命令行参数解析器。  

        添加的参数:  
        - file_path: 要统计单词数量的文件路径。  
        """  
        # 添加一个参数 'file_path'，用于指定要统计单词数量的文件路径  
        parser.add_argument('file_path', help='要统计单词数量的文件路径')
    @classmethod
    def print_usage(cls):
        print("示例输出")

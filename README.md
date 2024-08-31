
# ReconSuite

ReconSuite 是一个基于插件的网络侦察工具套件，用于自动化子域名发现和DNS解析等任务。

## 功能

- 动态插件加载系统
- 子域名发现（FindSubdomains插件）
- 批量DNS解析（MassDNS插件）
- Web界面用于易于操作

## 安装

1. 克隆仓库：
   ```
   git clone https://github.com/你的用户名/recon-suite.git
   cd recon-suite
   ```

2. 安装依赖：
   ```
   pip install -r requirements.txt
   ```

## 使用方法

1. 命令行界面：
   ```
   python main.py <plugin_name> <arguments>
   ```

2. Web界面：
   ```
   python web_interface.py
   ```
   然后在浏览器中访问 http://localhost:5000

## 贡献

欢迎提交问题和拉取请求。

## 许可

[MIT License](LICENSE)

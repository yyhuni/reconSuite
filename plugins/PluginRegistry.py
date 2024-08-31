# plugins/PluginRegistry.py

class PluginRegistry:
    def __init__(self):  
        self.plugins = {}  

    def register(self, name, plugin_cls):  
        if name in self.plugins:  
            raise ValueError(f"插件 {name} 已经注册")  
        self.plugins[name] = plugin_cls  

    def get_plugin(self, name):  
        return self.plugins.get(name)  

    def get_all_plugins(self):  
        return self.plugins  

plugin_registry = PluginRegistry()  

def register_plugin(name):
    def decorator(cls):
        cls._is_plugin = True
        cls._plugin_name = name
        return cls
    return decorator

class Plugin:  
    @classmethod  
    def add_arguments(cls, parser):  
        pass  

    @classmethod  
    def print_usage(cls):  
        pass  

    def execute(self, **kwargs):  
        raise NotImplementedError("插件必须实现 execute 方法")
# plugins\__init__.py
from .PluginRegistry import Plugin  

from .PluginRegistry import Plugin, register_plugin, plugin_registry

import os
import importlib
import logging

def load_plugins():
    plugins = {}
    plugin_dir = os.path.dirname(__file__)
    logging.debug(f"Searching for plugins in directory: {plugin_dir}")
    for filename in os.listdir(plugin_dir):
        if filename.endswith('.py') and not filename.startswith('__'):
            module_name = filename[:-3]
            logging.debug(f"Attempting to import module: {module_name}")
            try:
                module = importlib.import_module(f'.{module_name}', package='plugins')
                for attr_name in dir(module):
                    attr = getattr(module, attr_name)
                    if isinstance(attr, type) and hasattr(attr, '_is_plugin'):
                        logging.debug(f"Found plugin: {attr._plugin_name}")
                        plugins[attr._plugin_name] = attr
            except Exception as e:
                logging.error(f"Error loading module {module_name}: {str(e)}")
    logging.debug(f"Loaded {len(plugins)} plugins: {list(plugins.keys())}")
    return plugins


class Plugin:  
    @classmethod  
    def get_name(cls):  
        return cls.__name__.lower().replace('plugin', '')  

    @classmethod  
    def add_arguments(cls, parser):  
        pass  

def register_plugin(name):  
    def decorator(cls):  
        cls._is_plugin = True
        cls._plugin_name = name
        return cls
    return decorator
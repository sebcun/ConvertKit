import importlib
import os


def load_plugins():
    plugin_registry = []

    plugins_dir = "plugins"
    for folder in os.listdir(plugins_dir):
        full_path = os.path.join(plugins_dir, folder)

        if os.path.isdir(full_path):
            module_path = f"plugins.{folder}.plugin"
            module = importlib.import_module(module_path)

            plugin_registry.append(
                {
                    "name": module.title,
                    "input": module.input_format,
                    "output": module.output_format,
                    "module": module,
                }
            )

    return plugin_registry

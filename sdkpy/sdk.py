import os
import platform

import yaml


class SDKToolManager:
    def __init__(self, env_manager, base_dir, config_path):
        self.env_manager = env_manager
        self.base_dir = base_dir
        self.config_path = os.path.join(base_dir, config_path)
        self.sdk_configs = self.load_config()

    def load_config(self):
        try:
            with open(self.config_path, "r") as file:
                config = yaml.safe_load(file)
                for sdk, details in config.items():
                    if 'dir' not in details:
                        details['dir'] = sdk  # Default dir to SDK name if not provided
                print(f"Configuration loaded from {self.config_path}")
                return config
        except FileNotFoundError:
            print(f"Configuration file not found at {self.config_path}")
            return {}
        except yaml.YAMLError as exc:
            print(f"Error parsing the YAML file: {exc}")
            return {}

    def set_sdk(self, sdk_name, version):
        self.env_manager.backup("env_backup.json")

        try:
            if sdk_name not in self.sdk_configs:
                raise ValueError(f"SDK configuration for {sdk_name} is not available.")

            sdk_config = self.sdk_configs[sdk_name]
            sdk_dir = sdk_config["dir"]
            os_suffix = self.get_os_suffix()
            sdk_path = os.path.join(self.base_dir, sdk_dir, version)
            symlink_path = os.path.join(self.base_dir, sdk_dir, os_suffix)

            if not os.path.islink(symlink_path):
                os.symlink(sdk_path, symlink_path, target_is_directory=True)

            for item in sdk_config["env_vars"]:
                if isinstance(item, dict):
                    for var, value in item.items():
                        if var.lower() == "path":
                            if value:
                                self._update_path(os.path.join(symlink_path, value))
                            else:
                                self._update_path(symlink_path)
                        else:
                            full_path = (
                                os.path.join(symlink_path, value)
                                if not os.path.isabs(value)
                                else value
                            )
                            self.env_manager.set_var(var, full_path)
                elif isinstance(item, str):
                    if item.lower() == "path":
                        self._update_path(symlink_path)
                    else:
                        self.env_manager.set_var(item, symlink_path)

        except Exception as e:
            print(f"Error occurred: {e}")
            self.env_manager.restore("env_backup.json")
            raise

    def list_versions(self, sdk_name):
        if sdk_name not in self.sdk_configs:
            raise ValueError(f"Unsupported SDK/Tool: {sdk_name}")
        sdk_dir = os.path.join(self.base_dir, self.sdk_configs[sdk_name]["dir"])
        os_prefix = self.get_os_prefix()
        versions = [
            d
            for d in os.listdir(sdk_dir)
            if os.path.isdir(os.path.join(sdk_dir, d)) and d.startswith(os_prefix) and not d.endswith("_current")
        ]
        return versions
    
    def list_sdks(self):
        return list(self.sdk_configs.keys())
    
    def get_os_suffix(self):
        return self.get_os_prefix() + "_current"

    def get_os_prefix(self):
        os_type = platform.system().lower()
        if os_type == "windows":
            return "win"
        elif os_type == "linux":
            return "lin"
        elif os_type == "darwin":
            return "mac"
        else:
            raise ValueError("Unsupported operating system")

    def _update_path(self, new_path_segment):
        current_path = self.env_manager.get_var("Path")
        if current_path is None:
            current_path = ""

        path_parts = current_path.split(os.pathsep) if current_path else []

        # Append the new path segment if it's not already in the Path
        if new_path_segment not in path_parts:
            path_parts.append(new_path_segment)
            updated_path = os.pathsep.join(path_parts)
            self.env_manager.set_var("Path", updated_path)

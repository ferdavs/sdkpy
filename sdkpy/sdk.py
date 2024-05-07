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
                    if "dir" not in details:
                        details["dir"] = sdk  # Default dir to SDK name if not provided
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
                var_name = item["name"]
                var_value = item["value"]
                var_type = item["type"]

                if var_name.lower() == "path":
                    path_to_add = (
                        os.path.join(symlink_path, var_value)
                        if var_value
                        else symlink_path
                    )
                    self._update_path(path_to_add)
                elif var_type == "path":
                    full_path = (
                        os.path.join(symlink_path, var_value)
                        if var_value
                        else symlink_path
                    )
                    self.env_manager.set_var(var_name, full_path)
                elif var_type == "flag":
                    self.env_manager.set_var(var_name, var_value)

        except Exception as e:
            print(f"Error occurred: {e}")
            self.env_manager.restore("env_backup.json")
            raise

    def remove_sdk(self, sdk_name):
        if sdk_name not in self.sdk_configs:
            return
        self.env_manager.backup("env_backup.json")
        try:
            sdk_config = self.sdk_configs[sdk_name]
            sdk_dir = os.path.join(self.base_dir, sdk_config["dir"])
            path_var = self.env_manager.get_var("Path")

            # Filter out any path segments that include the SDK directory
            path_values = [
                path for path in path_var.split(os.pathsep) if sdk_dir not in path
            ]
            updated_path = os.pathsep.join(path_values)
            self.env_manager.set_var("Path", updated_path)

            # Remove other environment variables set by this SDK
            for item in sdk_config["env_vars"]:
                var_name = item["name"]
                if var_name.lower() != "path":  # We've already handled PATH separately
                    self.env_manager.remove_var(var_name)

        except Exception as e:
            print(f"Error occurred during SDK removal: {e}")
            self.env_manager.restore("env_backup.json")
            raise

    def _update_path(self, new_path_segment):
        current_path = self.env_manager.get_var("Path")
        if current_path is None:
            current_path = ""

        path_parts = current_path.split(os.pathsep) if current_path else []

        if new_path_segment not in path_parts:
            path_parts.append(new_path_segment)
            updated_path = os.pathsep.join(path_parts)
            self.env_manager.set_var("Path", updated_path)

    def _remove_path(self, path_segment):
        current_path = self.env_manager.get_var("Path")
        if current_path:
            path_parts = current_path.split(os.pathsep)
            path_parts = [path for path in path_parts if path != path_segment]
            updated_path = os.pathsep.join(path_parts)
            self.env_manager.set_var("Path", updated_path)

    def list_versions(self, sdk_name):
        if sdk_name not in self.sdk_configs:
            raise ValueError(f"Unsupported SDK/Tool: {sdk_name}")
        sdk_dir = os.path.join(self.base_dir, self.sdk_configs[sdk_name]["dir"])
        os_prefix = self.get_os_prefix()
        versions = [
            d
            for d in os.listdir(sdk_dir)
            if os.path.isdir(os.path.join(sdk_dir, d))
            and d.startswith(os_prefix)
            and not d.endswith("_current")
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

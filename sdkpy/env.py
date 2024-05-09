import json
import os
import winreg as reg
from abc import ABC, abstractmethod


class OSEnv(ABC):
    @abstractmethod
    def set_var(self, key, value):
        """Set an environment variable.

        Args:
            key (str): The name of the environment variable.
            value (str): The value of the environment variable.
        """
        pass

    @abstractmethod
    def get_var(self, key):
        """Get the value of an environment variable.

        Args:
            key (str): The name of the environment variable.

        Returns:
            str: The value of the environment variable.
        """
        pass

    @abstractmethod
    def remove_var(self, key):
        """Remove an environment variable.

        Args:
            key (str): The name of the environment variable.
        """
        pass

    @abstractmethod
    def backup(self, file_path):
        """Backup all environment variables to a file.

        Args:
            file_path (str): The path to the file to save the environment variables to.
        """
        pass

    @abstractmethod
    def restore(self, file_path):
        """Restore environment variables from a file.

        Args:
            file_path (str): The path to the file to restore the environment variables from.
        """
        pass

    @abstractmethod
    def list_vars(self):
        """List all environment variables.

        Returns:
            dict: A dictionary of environment variables.
        """
        pass


class WinEnv(OSEnv):
    """Use Windows registry to set, get and remove environment variables."""

    def set_var(self, name, value):
        key = reg.OpenKey(reg.HKEY_CURRENT_USER, r"Environment", 0, reg.KEY_ALL_ACCESS)
        reg.SetValueEx(key, name, 0, reg.REG_EXPAND_SZ, value)
        reg.CloseKey(key)
        # Notify the system about the change
        os.system('setx {} "{}"'.format(name, value))

    def get_var(self, name):
        try:
            key = reg.OpenKey(reg.HKEY_CURRENT_USER, r"Environment", 0, reg.KEY_READ)
            value, _ = reg.QueryValueEx(key, name)
            reg.CloseKey(key)
            return value
        except FileNotFoundError:
            return None

    def remove_var(self, name):
        key = reg.OpenKey(reg.HKEY_CURRENT_USER, r"Environment", 0, reg.KEY_ALL_ACCESS)
        reg.DeleteValue(key, name)
        reg.CloseKey(key)
        # Notify the system about the removal
        # os.system('setx {} ""'.format(name))

    def backup(self, file_path):
        env_vars = self.list_vars()
        with open(file_path, "w") as file:
            json.dump(env_vars, file, indent=4)

    def restore(self, file_path):
        try:
            with open(file_path, "r") as file:
                restored_vars = json.load(file)
            for key, value in restored_vars.items():
                self.set_var(key, value)
        except FileNotFoundError:
            print("Backup file not found. No environment variables were restored.")

    def list_vars(self):
        env_vars = {}
        key = reg.OpenKey(reg.HKEY_CURRENT_USER, r"Environment", 0, reg.KEY_READ)
        i = 0
        while True:
            try:
                name, value, _ = reg.EnumValue(key, i)
                env_vars[name] = value
                i += 1
            except WindowsError:
                break
        reg.CloseKey(key)
        return env_vars

class LinuxEnv(OSEnv):
    """Use Linux user sdk.profile to set, get and remove environment variables."""

    pass


def os_env() -> OSEnv:
    """
    Depending on os return OSEnv.

    """
    if os.name == "nt":
        return WinEnv()
    else:
        raise NotImplementedError("Only Windows is supported at the moment.")

import json
import os
import winreg as reg
from abc import ABC, abstractmethod


class OSEnv(ABC):
    @abstractmethod
    def set_var(self, key, value):
        pass

    @abstractmethod
    def get_var(self, key):
        pass

    @abstractmethod
    def remove_var(self, key):
        pass

    @abstractmethod
    def backup(self, file_path):
        pass

    @abstractmethod
    def restore(self, file_path):
        pass

    @abstractmethod
    def list_vars(self):
        pass


class WinEnv(OSEnv):
    def notify_system_environment_change(self):
        """Notify the system that environment variables have been updated."""
        import ctypes

        HWND_BROADCAST = 0xFFFF
        WM_SETTINGCHANGE = 0x1A
        SMTO_ABORTIFHUNG = 0x0002
        result = ctypes.c_long()
        ctypes.windll.user32.SendMessageTimeoutW(
            HWND_BROADCAST,
            WM_SETTINGCHANGE,
            0,
            "Environment",
            SMTO_ABORTIFHUNG,
            5000,
            ctypes.byref(result),
        )

    def set_var(self, name, value):
        key = reg.OpenKey(reg.HKEY_CURRENT_USER, r'Environment', 0, reg.KEY_ALL_ACCESS)
        reg.SetValueEx(key, name, 0, reg.REG_EXPAND_SZ, value)
        reg.CloseKey(key)
        # Notify the system about the change
        os.system('setx {} "{}"'.format(name, value))
        self.notify_system_environment_change()

    def get_var(self, name):
        try:
            key = reg.OpenKey(reg.HKEY_CURRENT_USER, r'Environment', 0, reg.KEY_READ)
            value, _ = reg.QueryValueEx(key, name)
            reg.CloseKey(key)
            return value
        except FileNotFoundError:
            return None

    def remove_var(self, name):
        key = reg.OpenKey(reg.HKEY_CURRENT_USER, r'Environment', 0, reg.KEY_ALL_ACCESS)
        reg.DeleteValue(key, name)
        reg.CloseKey(key)
        # Notify the system about the removal
        os.system('setx {} ""'.format(name))
        self.notify_system_environment_change()

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


def os_env()->OSEnv:
    """
    Depending on os return OSEnv.

    """
    if os.name == 'nt':
        return WinEnv()
    else:
        raise NotImplementedError("Only Windows is supported at the moment.")
    
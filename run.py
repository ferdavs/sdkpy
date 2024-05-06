from sdkpy.env import os_env
from sdkpy.sdk import SDKToolManager

env_manager = os_env()
sdk_manager = SDKToolManager(env_manager, "D:\\Sdk", "config.yml")

# List available versions of Java
versions = sdk_manager.list_versions("Node")
print("Available versions:", versions)

sdk_manager.set_sdk("Node", versions[0])

print(env_manager.list_vars())

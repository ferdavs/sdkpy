from sdkpy.env import os_env
from sdkpy.sdk import SDKToolManager

env_manager = os_env()
sdk_manager = SDKToolManager(env_manager, "D:\\Sdk", "config.yml")

sdk = "Flutter"

versions = sdk_manager.list_versions(sdk)
print("Available versions:", versions)

sdk_manager.set_sdk(sdk, versions[-1])

print(env_manager.list_vars())

sdk_manager.remove_sdk(sdk)

print(env_manager.list_vars())

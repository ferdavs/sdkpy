from argparse import ArgumentParser

from sdkpy.env import os_env
from sdkpy.sdk import SDKToolManager

env_manager = os_env()

# Create an argument parser
parser = ArgumentParser()
parser.add_argument("--sdk", help="The SDK to use")
parser.add_argument(
    "--version",
    help="The version of the SDK to use. If not set highest version will be used",
    default=None,
)
parser.add_argument("--path", help="The path to the SDK", default=None)
parser.add_argument("--list", help="List all available SDKs", action="store_true")
parser.add_argument(
    "--list-versions", help="List all available versions of an SDK", action="store_true"
)
parser.add_argument("--remove", help="Remove an SDK", action="store_true")
args = parser.parse_args()

sdk_manager = SDKToolManager(env_manager, args.path, "config.yml")


def main():
    if args.list:
        print("Available SDKs:", sdk_manager.list_sdks())
        exit()

    if args.list_versions:
        print("Available versions:", sdk_manager.list_versions(args.sdk))
        exit()

    if args.sdk:
        versions = sdk_manager.list_versions(args.sdk)
        if not versions:
            print(f"No versions found for {args.sdk}")
            exit()
        version = args.version
        if not version:
            version = versions[-1]
        sdk_manager.set_sdk(args.sdk, version)
        print(f"Using {args.sdk} version {version}")

    if args.remove:
        if args.sdk:
            sdk_manager.remove_sdk(args.sdk)
        else:
            print("Please provide a SDK to remove")

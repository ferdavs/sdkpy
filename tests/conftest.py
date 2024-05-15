import os
import shutil
import tempfile as tmp

import pytest

DIRS = [
    "Android/win/build-tools",
    "Android/win/platform-tools",
    "Android/win/tools/bin",
    "Git/win_2.44.0/bin",
    "Git/win_2.41.0/bin",
    "Gradle/win_7.2/bin",
    "Gradle/win_8.6/bin",
    "Maven/win_3.8.4/bin",
    "Java/win_jdk-17/bin",
    "Java/win_jdk-21/bin",
    "Node/win_16.11.1",
    "Rust/win",
    "VSCode/win/bin",
]

config = os.path.join(os.path.dirname(__file__), "config.yml")


@pytest.fixture
def sdk_dir():
    """Provide sdk dir in tmp folder."""

    with tmp.TemporaryDirectory(prefix="sdkpy_") as tmp_dir:
        shutil.copy(config, tmp_dir)
        for d in DIRS:
            os.makedirs(os.path.join(tmp_dir, d), exist_ok=True)
        yield tmp_dir


if __name__ == "__main__":
    print(next(sdk_dir()))

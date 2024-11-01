import subprocess
import sys

from usethis._console import console


def call_subprocess(args: list[str]) -> None:
    try:
        subprocess.run(
            args,
            check=True,
            capture_output=True,
        )
    except subprocess.CalledProcessError as e:
        msg = e.stderr.decode()
        console.print(f"✗ Failed to run uv subprocess:\n{msg}", style="red")
        sys.exit(e.returncode)

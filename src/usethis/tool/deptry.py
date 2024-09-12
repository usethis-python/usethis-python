import subprocess


def deptry() -> None:
    subprocess.run(["uv", "add", "--dev", "deptry"], check=True)

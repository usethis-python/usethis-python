import subprocess


def deptry() -> None:
    subprocess.run(["uv", "add", "--dev", "deptry"], check=True)
    print("✔ Adding deptry as a development dependency")

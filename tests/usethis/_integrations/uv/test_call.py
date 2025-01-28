import subprocess
import time
from contextlib import contextmanager
from pathlib import Path

import pytest

from usethis._integrations.uv.call import call_uv_subprocess
from usethis._integrations.uv.errors import UVSubprocessFailedError
from usethis._test import change_cwd


class TestCallUVSubprocess:
    def test_help_output_suppressed(self, capfd: pytest.CaptureFixture[str]):
        # Act
        call_uv_subprocess(["help"])

        # Assert
        assert capfd.readouterr().out == ""
        assert capfd.readouterr().err == ""

    def test_nonexistent_command(self):
        # Act and Assert
        match = ".*error: unrecognized subcommand 'does-not-exist'.*"
        with pytest.raises(UVSubprocessFailedError, match=match):
            call_uv_subprocess(["does-not-exist"])

    def test_can_call_ruff_subprocess_after_install(self, uv_init_dir: Path):
        # The main reason for this test is to ensure `run_ruff_subprocess` works
        # correctly.

        with change_cwd(uv_init_dir):
            call_uv_subprocess(["add", "ruff"])
            with run_ruff_subprocess():
                assert True

    def test_permissions_error(self, uv_init_dir: Path):
        # https://github.com/nathanjmcdougall/usethis-python/issues/45

        # Let's simulate a permissions issue by:
        # 1. Installing ruff with `uv add ruff`
        # 2. Start running the ruff executable in a subprocess
        # 3. Simultaneously, try to run `uv remove ruff` to trigger a permissions error
        #    It shouldn't happen ideally!

        with change_cwd(uv_init_dir):
            call_uv_subprocess(["add", "ruff"])

            with run_ruff_subprocess():
                # Should not raise an error
                call_uv_subprocess(["add", "ruff"])


# Create a subprocess that will run the ruff executable - do this via a custom
# context manager so we can manage setup and packdown
@contextmanager
def run_ruff_subprocess():
    # Run the ruff executable in the background - Popen won't need to complete
    # until the test is done
    proc = subprocess.Popen(
        ["ruff", "server"],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
    )

    # Yield control back to the test
    yield

    # Clean up
    retry_count = 0
    while proc.poll() is None:
        proc.kill()
        time.sleep(0.1)
        print(f"{retry_count=}")

        retry_count += 1
        if retry_count > 10:
            msg = "Failed to kill the ruff subprocess"
            print(msg)
    assert proc.poll() is not None
    assert proc.stdout is not None
    assert proc.stderr is not None
    proc.stdout.close()
    proc.stderr.close()

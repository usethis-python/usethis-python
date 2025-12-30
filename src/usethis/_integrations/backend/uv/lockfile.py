from usethis._config import usethis_config
from usethis._console import tick_print
from usethis._integrations.backend.uv.call import call_uv_subprocess


def ensure_uv_lock() -> None:
    if not (usethis_config.cpd() / "uv.lock").exists():
        tick_print("Writing 'uv.lock'.")
        call_uv_subprocess(["lock"], change_toml=False)

from collections.abc import Generator
from contextlib import contextmanager
from pathlib import Path

import pytest

import usethis._backend.uv.call
from _test import change_cwd
from usethis._backend.install import LazyInstallManager, lazy_install_packages
from usethis._backend.uv.call import call_uv_subprocess
from usethis._backend.uv.errors import UVSubprocessFailedError
from usethis._config import usethis_config
from usethis._config_file import files_manager
from usethis._deps import add_deps_to_group, get_deps_from_group
from usethis._subprocess import SubprocessFailedError, SubprocessResult
from usethis._types.backend import BackendEnum
from usethis._types.deps import Dependency


class TestLazyInstallPackages:
    @pytest.mark.usefixtures("_vary_network_conn")
    def test_uv_installs_on_exit(self, uv_env_dir: Path):
        with change_cwd(uv_env_dir), files_manager():
            # Act
            with lazy_install_packages():
                add_deps_to_group([Dependency(name="codespell")], "dev")

                # Assert
                # The dependency is declared...
                assert get_deps_from_group("dev") == [Dependency(name="codespell")]
                # ...but isn't installed yet
                with pytest.raises(UVSubprocessFailedError):
                    call_uv_subprocess(["sync", "--check"], change_toml=False)

            # Assert contd
            # Now it is installed
            call_uv_subprocess(["sync", "--check"], change_toml=False)

    @pytest.mark.usefixtures("_vary_network_conn")
    def test_group_which_is_not_a_default_group(self, uv_env_dir: Path):
        # Arrange
        # The user has chosen their default groups, and "dev" isn't one of them
        pyproject = uv_env_dir / "pyproject.toml"
        content = pyproject.read_text().replace(
            "environments = []", 'environments = []\ndefault-groups = ["test"]'
        )
        pyproject.write_text(content + "\n[dependency-groups]\ntest = []\n")

        # Act
        with change_cwd(uv_env_dir), files_manager(), lazy_install_packages():
            add_deps_to_group([Dependency(name="codespell")], "dev")

        # Assert
        # It is installed all the same, as when not installing lazily
        with change_cwd(uv_env_dir):
            call_uv_subprocess(
                ["run", "--no-sync", "python", "-c", "import codespell_lib"],
                change_toml=False,
            )

    @pytest.mark.usefixtures("_vary_network_conn")
    def test_other_packages_are_kept(self, uv_env_dir: Path):
        with change_cwd(uv_env_dir), files_manager():
            # Arrange
            # A package which isn't part of the project
            call_uv_subprocess(["venv"], change_toml=False)
            call_uv_subprocess(["pip", "install", "iniconfig"], change_toml=False)

            # Act
            with lazy_install_packages():
                add_deps_to_group([Dependency(name="codespell")], "dev")

            # Assert
            # It isn't removed, as when not installing lazily
            call_uv_subprocess(
                ["run", "--no-sync", "python", "-c", "import iniconfig"],
                change_toml=False,
            )

    def test_poetry_installs_as_usual(
        self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
    ):
        # Arrange
        (tmp_path / "pyproject.toml").write_text("""\
[dependency-groups]
test = []
""")

        calls: list[tuple[str, str]] = []

        def mock_add_dep(dep: object, group: str) -> None:
            calls.append((str(dep), group))

        monkeypatch.setattr("usethis._deps.add_dep_to_group_via_poetry", mock_add_dep)

        # Act
        with (
            usethis_config.set(backend=BackendEnum.poetry),
            change_cwd(tmp_path),
            files_manager(),
            lazy_install_packages(),
        ):
            add_deps_to_group([Dependency(name="pytest")], "test")

            # Assert
            # The dependency is added as usual, rather than lazily
            assert calls == [("pytest", "test")]

    def test_none_backend_as_usual(
        self, tmp_path: Path, capfd: pytest.CaptureFixture[str]
    ):
        # Arrange
        (tmp_path / "pyproject.toml").write_text("""\
[dependency-groups]
test = []
""")

        # Act
        with (
            usethis_config.set(backend=BackendEnum.none),
            change_cwd(tmp_path),
            files_manager(),
            lazy_install_packages(),
        ):
            add_deps_to_group([Dependency(name="pytest")], "test")

        # Assert
        out, err = capfd.readouterr()
        assert not err
        assert out == "☐ Add the test dependency 'pytest'.\n"

    @pytest.mark.usefixtures("bare_dir")
    class TestOnExit:
        def test_installs_once(self, install_calls: list[list[str]]):
            # Act
            with lazy_install_packages():
                LazyInstallManager().mark_pending("test")
                LazyInstallManager().mark_pending("dev")
                LazyInstallManager().mark_pending("dev")

                # Assert
                assert install_calls == []

            # Assert contd
            # Inexact, so that other packages aren't removed, and with the groups
            # explicitly, since they aren't necessarily installed by default
            assert install_calls == [
                [
                    "uv",
                    "sync",
                    "--no-progress",
                    "--group",
                    "dev",
                    "--group",
                    "test",
                    "--inexact",
                ]
            ]

        def test_nothing_owed(self, install_calls: list[list[str]]):
            # Act
            with lazy_install_packages():
                pass

            # Assert
            assert install_calls == []

        def test_nested(self, install_calls: list[list[str]]):
            # Act
            with lazy_install_packages():
                with lazy_install_packages():
                    LazyInstallManager().mark_pending("dev")

                # Assert
                # Only the outermost scope installs, and it is still open
                assert install_calls == []
                assert LazyInstallManager().is_active

            # Assert contd
            assert len(install_calls) == 1
            assert not LazyInstallManager().is_active

        def test_offline(self, install_calls: list[list[str]]):
            # Act
            with usethis_config.set(offline=True), lazy_install_packages():
                LazyInstallManager().mark_pending("dev")

            # Assert
            assert install_calls == [
                [
                    "uv",
                    "sync",
                    "--no-progress",
                    "--offline",
                    "--group",
                    "dev",
                    "--inexact",
                ]
            ]

        def test_in_original_project(
            self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
        ):
            # Arrange
            cwds: list[Path | None] = []

            def mock_call_subprocess(
                args: list[str], *, cwd: Path | None = None
            ) -> SubprocessResult:
                _ = args
                cwds.append(cwd)
                return SubprocessResult("", "")

            monkeypatch.setattr(
                usethis._backend.uv.call, "call_subprocess", mock_call_subprocess
            )
            other_dir = tmp_path / "other"
            other_dir.mkdir()

            # Act
            with (
                usethis_config.set(backend=BackendEnum.uv),
                lazy_install_packages(),
            ):
                LazyInstallManager().mark_pending("dev")
                monkeypatch.setattr(usethis_config, "project_dir", other_dir)

            # Assert
            # The installation is for the project that the scope was opened for
            assert cwds == [tmp_path.resolve()]

        def test_exception(
            self,
            install_calls: list[list[str]],
            capfd: pytest.CaptureFixture[str],
        ):
            # Arrange
            msg = "Something went wrong"

            def mark_pending_then_fail() -> None:
                with lazy_install_packages():
                    LazyInstallManager().mark_pending("test")
                    LazyInstallManager().mark_pending("dev")
                    raise RuntimeError(msg)

            # Act
            with pytest.raises(RuntimeError, match=msg):
                mark_pending_then_fail()

            # Assert
            assert install_calls == []
            out, err = capfd.readouterr()
            assert not err
            # The user is told what to install, rather than it being dropped
            assert (
                out
                == "☐ Install the dependencies which were added to the 'dev', 'test' dependency groups.\n"
            )

            # Assert contd
            # The state is reset: nothing is owed by a later scope
            with lazy_install_packages():
                pass
            assert install_calls == []
            assert not LazyInstallManager().is_active

        def test_nested_exception(
            self,
            install_calls: list[list[str]],
            capfd: pytest.CaptureFixture[str],
        ):
            # Arrange
            msg = "Something went wrong"

            def fail_in_nested_scope() -> None:
                with lazy_install_packages():
                    LazyInstallManager().mark_pending("dev")
                    with lazy_install_packages():
                        raise RuntimeError(msg)

            # Act
            with pytest.raises(RuntimeError, match=msg):
                fail_in_nested_scope()

            # Assert
            assert install_calls == []
            out, err = capfd.readouterr()
            assert not err
            # The user is only told once, by the scope which is responsible
            assert (
                out
                == "☐ Install the dependencies which were added to the 'dev' dependency group.\n"
            )
            assert not LazyInstallManager().is_active

        def test_exception_with_nothing_owed(self, capfd: pytest.CaptureFixture[str]):
            # Arrange
            msg = "Something went wrong"

            def fail() -> None:
                with lazy_install_packages():
                    raise RuntimeError(msg)

            # Act
            with pytest.raises(RuntimeError, match=msg):
                fail()

            # Assert
            out, err = capfd.readouterr()
            assert not out
            assert not err

        def test_installation_fails(self, monkeypatch: pytest.MonkeyPatch):
            # Arrange
            def mock_call_subprocess(
                args: list[str], *, cwd: Path | None = None
            ) -> SubprocessResult:
                _ = args, cwd
                msg = "boom"
                raise SubprocessFailedError(msg)

            monkeypatch.setattr(
                usethis._backend.uv.call, "call_subprocess", mock_call_subprocess
            )

            # Act, Assert
            # It's the installation that failed, rather than anything to do with a
            # dependency group
            with (
                usethis_config.set(backend=BackendEnum.uv),
                pytest.raises(UVSubprocessFailedError, match="boom"),
                lazy_install_packages(),
            ):
                LazyInstallManager().mark_pending("dev")

        @pytest.mark.parametrize("backend", [BackendEnum.poetry, BackendEnum.none])
        def test_backend_which_does_not_install_lazily(self, backend: BackendEnum):
            # Act, Assert
            # Only the uv backend adds dependencies lazily, so nothing else can owe an
            # installation. Failing loudly is better than dropping it silently.
            with (
                usethis_config.set(backend=backend),
                pytest.raises(
                    AssertionError,
                    match=f"The '{backend.value}' backend doesn't install lazily",
                ),
                lazy_install_packages(),
            ):
                LazyInstallManager().mark_pending("dev")

        @pytest.fixture
        def install_calls(
            self, monkeypatch: pytest.MonkeyPatch
        ) -> Generator[list[list[str]], None, None]:
            """The arguments of each installation, with the uv backend in use."""
            calls: list[list[str]] = []

            def mock_call_subprocess(
                args: list[str], *, cwd: Path | None = None
            ) -> SubprocessResult:
                _ = cwd
                calls.append(args)
                return SubprocessResult("", "")

            monkeypatch.setattr(
                usethis._backend.uv.call, "call_subprocess", mock_call_subprocess
            )

            with usethis_config.set(backend=BackendEnum.uv):
                yield calls


@pytest.mark.usefixtures("bare_dir")
class TestLazyInstallManager:
    class TestIsActive:
        def test_inside_scope(self):
            # Act
            with _open_scope():
                # Assert
                assert LazyInstallManager().is_active

        def test_outside_scope(self):
            # Act, Assert
            assert not LazyInstallManager().is_active

        def test_after_scope(self):
            # Act
            with _open_scope():
                pass

            # Assert
            assert not LazyInstallManager().is_active

        def test_other_project(self, tmp_path: Path):
            # Arrange
            other_dir = tmp_path / "other"
            other_dir.mkdir()

            # Act
            with _open_scope(), change_cwd(other_dir):
                # Assert
                # The scope was opened for a different project
                assert not LazyInstallManager().is_active

    class TestIsLazy:
        def test_active(self):
            # Act
            with _open_scope():
                # Assert
                assert LazyInstallManager().is_lazy

        def test_inactive(self):
            # Act, Assert
            assert not LazyInstallManager().is_lazy

        def test_frozen(self):
            # Act
            with usethis_config.set(frozen=True), _open_scope():
                # Assert
                # Nothing is installed when frozen, so there is nothing to be lazy about
                assert not LazyInstallManager().is_lazy

    class TestOwedGroups:
        def test_sorted_and_unique(self):
            # Act
            with _open_scope():
                LazyInstallManager().mark_pending("test")
                LazyInstallManager().mark_pending("dev")
                LazyInstallManager().mark_pending("test")

                # Assert
                assert LazyInstallManager().owed_groups == ["dev", "test"]

        def test_no_scope(self):
            # Act, Assert
            assert LazyInstallManager().owed_groups == []

        def test_reset_after_scope(self):
            # Act
            with _open_scope():
                LazyInstallManager().mark_pending("dev")

            with _open_scope():
                # Assert
                assert LazyInstallManager().owed_groups == []

    class TestEnter:
        def test_already_open(self):
            # Arrange
            with _open_scope():
                LazyInstallManager().mark_pending("dev")

                # Act
                LazyInstallManager().enter()

                # Assert
                # The groups which are owed an installation aren't discarded
                assert LazyInstallManager().owed_groups == ["dev"]

    class TestMarkPending:
        def test_no_scope(self):
            # Act, Assert
            with pytest.raises(KeyError):
                LazyInstallManager().mark_pending("dev")


@contextmanager
def _open_scope() -> Generator[None, None, None]:
    """Open a scope, without any of the handling that happens on leaving it."""
    manager = LazyInstallManager()
    manager.enter()
    try:
        yield
    finally:
        manager.leave()

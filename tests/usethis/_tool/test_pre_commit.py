from pathlib import Path

from usethis._config import usethis_config
from usethis._config_file import files_manager
from usethis._integrations.pre_commit import schema
from usethis._test import change_cwd
from usethis._tool.pre_commit import PreCommitConfig
from usethis._types.backend import BackendEnum


class TestFromSystemHook:
    def test_uv_backend_entry_prefix(self, tmp_path: Path):
        # Act
        with change_cwd(tmp_path), files_manager():
            config = PreCommitConfig.from_system_hook(
                hook_id="my-hook",
                entry="my-cmd",
            )

        # Assert
        assert len(config.repo_configs) == 1
        repo = config.repo_configs[0].repo
        assert isinstance(repo, schema.LocalRepo)
        assert repo.hooks is not None
        assert len(repo.hooks) == 1
        assert repo.hooks[0].entry == "uv run --frozen --offline my-cmd"

    def test_none_backend_entry_no_prefix(self, tmp_path: Path):
        # Act
        with (
            change_cwd(tmp_path),
            files_manager(),
            usethis_config.set(backend=BackendEnum.none),
        ):
            config = PreCommitConfig.from_system_hook(
                hook_id="my-hook",
                entry="my-cmd",
            )

        # Assert
        repo = config.repo_configs[0].repo
        assert isinstance(repo, schema.LocalRepo)
        assert repo.hooks is not None
        assert repo.hooks[0].entry == "my-cmd"

    def test_hook_id(self, tmp_path: Path):
        with change_cwd(tmp_path), files_manager():
            config = PreCommitConfig.from_system_hook(
                hook_id="test-hook",
                entry="test-cmd",
            )

        repo = config.repo_configs[0].repo
        assert isinstance(repo, schema.LocalRepo)
        assert repo.hooks is not None
        assert repo.hooks[0].id == "test-hook"

    def test_name_equals_hook_id(self, tmp_path: Path):
        with change_cwd(tmp_path), files_manager():
            config = PreCommitConfig.from_system_hook(
                hook_id="test-hook",
                entry="test-cmd",
            )

        repo = config.repo_configs[0].repo
        assert isinstance(repo, schema.LocalRepo)
        assert repo.hooks is not None
        assert repo.hooks[0].name == "test-hook"

    def test_requires_venv_is_true(self, tmp_path: Path):
        with change_cwd(tmp_path), files_manager():
            config = PreCommitConfig.from_system_hook(
                hook_id="test-hook",
                entry="test-cmd",
            )

        assert config.repo_configs[0].requires_venv is True

    def test_inform_how_to_use_on_migrate_is_false(self, tmp_path: Path):
        with change_cwd(tmp_path), files_manager():
            config = PreCommitConfig.from_system_hook(
                hook_id="test-hook",
                entry="test-cmd",
            )

        assert config.inform_how_to_use_on_migrate is False

    def test_pass_filenames_is_false(self, tmp_path: Path):
        with change_cwd(tmp_path), files_manager():
            config = PreCommitConfig.from_system_hook(
                hook_id="test-hook",
                entry="test-cmd",
            )

        repo = config.repo_configs[0].repo
        assert isinstance(repo, schema.LocalRepo)
        assert repo.hooks is not None
        assert repo.hooks[0].pass_filenames is False

    def test_always_run_is_true(self, tmp_path: Path):
        with change_cwd(tmp_path), files_manager():
            config = PreCommitConfig.from_system_hook(
                hook_id="test-hook",
                entry="test-cmd",
            )

        repo = config.repo_configs[0].repo
        assert isinstance(repo, schema.LocalRepo)
        assert repo.hooks is not None
        assert repo.hooks[0].always_run is True

    def test_system_language_set(self, tmp_path: Path):
        with change_cwd(tmp_path), files_manager():
            config = PreCommitConfig.from_system_hook(
                hook_id="test-hook",
                entry="test-cmd",
            )

        repo = config.repo_configs[0].repo
        assert isinstance(repo, schema.LocalRepo)
        assert repo.hooks is not None
        assert repo.hooks[0].language == schema.Language("system")

    def test_local_repo(self, tmp_path: Path):
        with change_cwd(tmp_path), files_manager():
            config = PreCommitConfig.from_system_hook(
                hook_id="test-hook",
                entry="test-cmd",
            )

        repo = config.repo_configs[0].repo
        assert isinstance(repo, schema.LocalRepo)
        assert repo.repo == "local"

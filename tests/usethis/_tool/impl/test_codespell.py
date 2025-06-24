from usethis._integrations.ci.github.tags import get_github_latest_tag
from usethis._integrations.pre_commit.schema import UriRepo
from usethis._tool.impl.codespell import CodespellTool


class TestCodespellTool:
    def test_latest_version(self):
        (config,) = CodespellTool().get_pre_commit_config().repo_configs
        repo = config.repo
        assert isinstance(repo, UriRepo)
        assert repo.rev == get_github_latest_tag(
            owner="codespell-project", repo="codespell"
        )

from usethis._integrations.pre_commit.schema import HookDefinition, LocalRepo


def test_multiple_per_repo():
    # There was a suspicion this wasn't possible, but it is.
    LocalRepo(
        repo="local",
        hooks=[
            HookDefinition(id="black"),
            HookDefinition(id="isort"),
        ],
    )

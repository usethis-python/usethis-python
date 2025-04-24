from usethis._tool.all_ import ALL_TOOLS


class TestAllTools:
    def test_sorted_alphabetically(self):
        names = [tool.name.lower() for tool in ALL_TOOLS]
        assert names == sorted(names)

from usethis._tool.rule import RuleConfig


class TestRepr:
    def test_empty(self):
        assert repr(RuleConfig()) == "RuleConfig()"

    def test_selected(self):
        assert repr(RuleConfig(selected=["A"])) == "RuleConfig(selected=['A'])"

    def test_ignored(self):
        assert repr(RuleConfig(ignored=["A"])) == "RuleConfig(ignored=['A'])"

    def test_unmanaged_selected(self):
        assert (
            repr(RuleConfig(unmanaged_selected=["A"]))
            == "RuleConfig(unmanaged_selected=['A'])"
        )

    def test_unmanaged_ignored(self):
        assert (
            repr(RuleConfig(unmanaged_ignored=["A"]))
            == "RuleConfig(unmanaged_ignored=['A'])"
        )

    def test_tests_ignored(self):
        assert (
            repr(RuleConfig(tests_ignored=["A"])) == "RuleConfig(tests_ignored=['A'])"
        )

    def test_nontests_ignored(self):
        assert (
            repr(RuleConfig(nontests_ignored=["A"]))
            == "RuleConfig(nontests_ignored=['A'])"
        )

    def test_tests_unmanaged_ignored(self):
        assert (
            repr(RuleConfig(tests_unmanaged_ignored=["A"]))
            == "RuleConfig(tests_unmanaged_ignored=['A'])"
        )

    def test_nontests_unmanaged_ignored(self):
        assert (
            repr(RuleConfig(nontests_unmanaged_ignored=["A"]))
            == "RuleConfig(nontests_unmanaged_ignored=['A'])"
        )

    def test_all_fields(self):
        rc = RuleConfig(
            selected=["A"],
            ignored=["B"],
            unmanaged_selected=["C"],
            unmanaged_ignored=["D"],
            tests_ignored=["E"],
            nontests_ignored=["F"],
            tests_unmanaged_ignored=["G"],
            nontests_unmanaged_ignored=["H"],
        )
        assert repr(rc) == (
            "RuleConfig("
            "selected=['A'], "
            "ignored=['B'], "
            "unmanaged_selected=['C'], "
            "unmanaged_ignored=['D'], "
            "tests_ignored=['E'], "
            "nontests_ignored=['F'], "
            "tests_unmanaged_ignored=['G'], "
            "nontests_unmanaged_ignored=['H']"
            ")"
        )

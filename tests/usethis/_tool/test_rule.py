from usethis._tool.rule import RuleConfig, is_rule_covered_by, reconcile_rules


class TestIsRuleCoveredBy:
    def test_same_rule(self):
        assert not is_rule_covered_by("TC", "TC")

    def test_all_covers_any(self):
        assert is_rule_covered_by("TC", "ALL")

    def test_all_covers_specific(self):
        assert is_rule_covered_by("TC001", "ALL")

    def test_group_covers_specific(self):
        assert is_rule_covered_by("TC001", "TC")

    def test_specific_does_not_cover_group(self):
        assert not is_rule_covered_by("TC", "TC001")

    def test_partial_prefix(self):
        assert is_rule_covered_by("TC00", "TC")

    def test_unrelated(self):
        assert not is_rule_covered_by("E501", "TC")

    def test_all_does_not_cover_itself(self):
        assert not is_rule_covered_by("ALL", "ALL")


class TestReconcileRules:
    def test_no_overlap(self):
        result = reconcile_rules(["A"], ["B"])
        assert result.to_add == ["B"]
        assert result.to_remove == []

    def test_exact_duplicate(self):
        result = reconcile_rules(["A"], ["A"])
        assert result.to_add == []
        assert result.to_remove == []

    def test_incoming_covered_by_existing(self):
        # "TC001" is covered by existing "TC"
        result = reconcile_rules(["TC"], ["TC001"])
        assert result.to_add == []
        assert result.to_remove == []

    def test_incoming_covered_by_all(self):
        result = reconcile_rules(["ALL"], ["TC001"])
        assert result.to_add == []
        assert result.to_remove == []

    def test_incoming_replaces_specific(self):
        # Adding "TC" should replace existing "TC001"
        result = reconcile_rules(["TC001"], ["TC"])
        assert result.to_add == ["TC"]
        assert result.to_remove == ["TC001"]

    def test_incoming_replaces_multiple_specific(self):
        # Adding "TC" should replace both "TC001" and "TC002"
        result = reconcile_rules(["TC001", "TC002"], ["TC"])
        assert result.to_add == ["TC"]
        assert result.to_remove == ["TC001", "TC002"]

    def test_all_replaces_everything(self):
        result = reconcile_rules(["A", "B", "TC001"], ["ALL"])
        assert result.to_add == ["ALL"]
        assert result.to_remove == ["A", "B", "TC001"]

    def test_incoming_dedup(self):
        # Both "TC" and "TC001" incoming; only "TC" should survive
        result = reconcile_rules([], ["TC", "TC001"])
        assert result.to_add == ["TC"]
        assert result.to_remove == []

    def test_empty_incoming(self):
        result = reconcile_rules(["A", "B"], [])
        assert result.to_add == []
        assert result.to_remove == []

    def test_empty_existing(self):
        result = reconcile_rules([], ["A", "B"])
        assert result.to_add == ["A", "B"]
        assert result.to_remove == []

    def test_mixed_scenario(self):
        # Mixed: group replaces specific while unrelated rules are preserved
        result = reconcile_rules(["E", "TC001", "D100"], ["TC", "F"])
        assert result.to_add == ["F", "TC"]
        assert result.to_remove == ["TC001"]

    def test_preserves_unrelated_existing(self):
        result = reconcile_rules(["A", "B"], ["C"])
        assert result.to_add == ["C"]
        assert result.to_remove == []

    def test_is_noop_when_no_changes(self):
        result = reconcile_rules(["A"], ["A"])
        assert result.is_noop

    def test_is_not_noop_when_adding(self):
        result = reconcile_rules(["A"], ["B"])
        assert not result.is_noop


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

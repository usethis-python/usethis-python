from usethis._types.deps import Dependency


class TestDependency:
    class TestToRequirementsString:
        def test_no_extras(self):
            dep = Dependency(name="requests")
            assert dep.to_requirement_string() == "requests"

        def test_single_extra(self):
            dep = Dependency(name="requests", extras=frozenset({"security"}))
            assert dep.to_requirement_string() == "requests[security]"

        def test_multiple_extras(self):
            dep = Dependency(name="requests", extras=frozenset({"security", "socks"}))
            assert dep.to_requirement_string() == "requests[security,socks]"

    class TestEquality:
        def test_is_identifying_ignored_in_equality(self):
            # is_identifying is metadata and does not affect dependency identity.
            assert Dependency(name="tomli", is_identifying=True) == Dependency(
                name="tomli", is_identifying=False
            )

        def test_is_identifying_ignored_in_hash(self):
            assert hash(Dependency(name="tomli", is_identifying=True)) == hash(
                Dependency(name="tomli", is_identifying=False)
            )

        def test_membership_ignores_is_identifying(self):
            deps = [Dependency(name="tomli", is_identifying=False)]
            assert Dependency(name="tomli") in deps

        def test_extras_affect_equality(self):
            assert Dependency(name="requests") != Dependency(
                name="requests", extras=frozenset({"security"})
            )

        def test_name_affects_equality(self):
            assert Dependency(name="requests") != Dependency(name="urllib3")

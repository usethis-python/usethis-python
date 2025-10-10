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

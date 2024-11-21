from usethis._integrations.bitbucket.dump import ORDER_BY_CLS


class TestOrderByCls:
    def test_attribute_consistency(self):
        for cls, fields in ORDER_BY_CLS.items():
            for field in fields:
                assert field in cls.model_fields

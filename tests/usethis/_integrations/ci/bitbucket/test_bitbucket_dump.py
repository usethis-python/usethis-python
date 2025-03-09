from usethis._integrations.ci.bitbucket.dump import (
    ORDER_BY_CLS,
    bitbucket_fancy_dump,
)
from usethis._integrations.ci.bitbucket.schema import (
    Cache,
    CachePath,
    Clone,
    Definitions,
    Image,
    ImageName,
    PipelinesConfiguration,
)


class TestOrderByCls:
    def test_attribute_consistency(self):
        for cls, fields in ORDER_BY_CLS.items():
            for field in fields:
                assert field in cls.model_fields


class TestBitbucketFancyDump:
    def test_order(self):
        # Arrange
        config = PipelinesConfiguration(
            image=Image(ImageName("python:3.8.1")),
            clone=Clone(depth="full"),
            definitions=Definitions(
                caches={
                    "pip": Cache(CachePath("pip")),
                },
            ),
        )

        # Act
        dump = bitbucket_fancy_dump(config, reference={})

        # Assert
        assert dump == {
            "image": "python:3.8.1",
            "clone": {
                "depth": "full",
            },
            "definitions": {
                "caches": {
                    "pip": "pip",
                },
            },
        }
        assert list(dump) == ["image", "clone", "definitions"]

from enum import Enum


class DevelopmentStatusEnum(Enum):
    planning = "planning"
    prealpha = "prealpha"
    alpha = "alpha"
    beta = "beta"
    production = "production"
    mature = "mature"
    inactive = "inactive"


class DevelopmentStatusCodeEnum(Enum):
    planning = 1
    prealpha = 2
    alpha = 3
    beta = 4
    production = 5
    mature = 6
    inactive = 7


def use_development_status(
    status: DevelopmentStatusEnum | DevelopmentStatusCodeEnum,
) -> None:
    raise NotImplementedError

from enum import IntEnum


class Cryostats(IntEnum):
    """
    Enum for the different devices
    Setup versions:
    0: attoDRY1100
    1: attoDRY2100
    2: attoDRY800
    """

    ATTODRY1100 = 0
    ATTODRY2100 = 1
    ATTODRY800 = 2

import warnings

from src.AttoDRY.Cryostats import Cryostats

try:
    from src.AttoDRY.PyAttoDRY import AttoDRY
except NameError:
    warnings.warn("Could not import AttoDRY")

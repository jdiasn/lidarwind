"""Top-level package for lidarSuit package"""

__author__ = "José Dias Neto"
__email__ = "jdiasn@gmail.com"
__affiliation__ = "Delft University of Technology"


from pkg_resources import get_distribution, DistributionNotFound

try:
    __version__ = get_distribution(__name__).version
except DistributionNotFound:
    try:
        from .version import version as __version__
    except ImportError:
        raise ImportError(
            "Failed to find (autogenerated) version.py. "
            "This might be because you are installing from GitHub's tarballs, "
            "use the PyPI ones."
        )


from .lst_config import *
from .lidar_code import *
from .wind_prop_retrieval import *
from .wind_prop_retrieval_6_beam import *
from .visualization import *
from .utilities import *
from .dataOperator import *
from .dataAttributesL1 import *
from .filters import *

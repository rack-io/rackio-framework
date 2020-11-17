"""
Automation, Control and IoT Framework for Python
==================================
Rackio is a Modern Python Framework for microboard 
automation and (non-critical) control applications development. 

It aims to provide simple and efficient solutions
to the most common software architectures found in 
the control and automation industry.

See https://rackio-framework.readthedocs.io/ for complete documentation.
"""

__version__ = '1.0.2'

from .core import Rackio
from .engine import CVTEngine as TagEngine
from .state import RackioStateMachine, State, TagBinding, GroupBinding
from .dbmodels import BaseModel as RackioModel
from .dbmodels import CharField, TextField
from .dbmodels import DateTimeField, IntegerField, FloatField
from .dbmodels import ForeignKeyField
from .dbmodels import BlobField

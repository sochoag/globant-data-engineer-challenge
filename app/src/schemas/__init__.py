from typing import List, Union
from .department import DepartmentCreate
from .job import JobCreate
from .employee import HiredEmployeeCreate

PostRequest = Union[dict, List[dict]]

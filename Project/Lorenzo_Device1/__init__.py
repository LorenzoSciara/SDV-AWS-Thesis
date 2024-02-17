from .airConditioning import AirConditioning
from .airbag import Airbag
from .heatedSeats import HeatedSeats
from .abs import ABS
from .engine import Engine
from .battery import Battery

subsystems = [Engine(), Battery(), AirConditioning(), Airbag(), HeatedSeats(), ABS()]
import time

from rackio import Rackio, TagEngine
from rackio.models import Model, FloatType, IntegerType, BooleanType


class Car(Model):

    engine_size = FloatType(default=1.8)
    seats = IntegerType(default=5)
    air_conditioning = BooleanType(default=True)
    mileage = FloatType(default=0.0)

    def drive(self):

        self.mileage += 0.5

new_car = Car(engine_size=2.2)

tag_engine = TagEngine()

# Tags definitions

tag_engine.set_tag("car1", Car)

tag_engine.write_tag("car1", new_car)

new_car.drive()

same_car = tag_engine.read_tag("car1")
same_car.seats = 6
same_car.commit()

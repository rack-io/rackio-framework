import time

from rackio import Rackio, TagEngine
from rackio.models import Model, FloatField, IntegerField, BooleanField


class Car(Model):

    engine_size = FloatField(default=1.8)
    seats = IntegerField(default=5)
    air_conditioning = BooleanField(default=True)

    def inc_seats(self):

        self.seats += 1

new_car = Car(engine_size=2.2)

tag_engine = TagEngine()

# Tags definitions

tag_engine.set_tag("car1", Car)

tag_engine.write_tag("car1", new_car)

new_car.inc_seats()

another_car = tag_engine.read_tag("car1")

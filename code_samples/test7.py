import time

from rackio import Rackio, TagEngine
from rackio.models import Model, FloatField, IntegerField, BooleanField

class Car(Model):

    engine_size = FloatField(default=1.8)
    seats = IntegerField(default=5)
    air_conditioning = BooleanField(default=True)

new_car = Car(engine_size=2.2)

tag_engine = TagEngine()

# Tags definitions

tag_engine.set_tag("car1", Car)

tag_engine.write_tag("car1", new_car)

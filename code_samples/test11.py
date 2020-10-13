import time

from rackio import Rackio, TagEngine
from rackio import RackioModel, TextField

app = Rackio()


@app.define_table
class Car(RackioModel):

    name = TextField()


@app.rackit(1)
def function():

    time.sleep(0.5)

    Car.create(name="Lamborghini Huracan")

# app.set_db(dbfile="tags.db")


if __name__ == "__main__":

    app.run()

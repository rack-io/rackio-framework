import time

from rackio import Rackio, TagEngine
from rackio.models import Tag
from rackio.controls import Action, Condition, Control

from random import random

app = Rackio()

tag_egine = TagEngine()

@app.rackit(1)
def writer1():

    while True:

        time.sleep(0.5)

        value = 24 + 2 * random()
        tag_egine.write_tag("RAND1", value)

@app.rackit(1)
def writer2():

    while True:

        time.sleep(0.5)

        value = 48 + 2 * random()
        tag_egine.write_tag("RAND2", value)

@app.rackit(1)
def reader():

    while True:

        time.sleep(1)

        rand1 = tag_egine.read_tag("RAND1")
        rand2 = tag_egine.read_tag("RAND2")
        
        print("")
        print(rand1)
        print(rand2)
        

if __name__ == "__main__":

    app.run()







import time

from rackio import Rackio, TagEngine
from rackio.models import Tag
from rackio.controls import ValueAction, Condition, Control

from random import random

app = Rackio()

tag_egine = TagEngine()

# Tags definitions

tag_egine.set_tag("RAND1", "float")
tag_egine.set_tag("RAND2", "float")
tag_egine.set_tag("T1", "float")
tag_egine.set_tag("T2", "float")
tag_egine.set_tag("T3", "float")

# Conditions definitions

cond1 = Condition("T1",">=", "T2")
cond2 = Condition("T1","<", "T2")

# Actions definitions

act1 = ValueAction("T3", 40)
act2 = ValueAction("T3", 80)

# Controls Definitions

control1 = Control("C1", cond1, act1)
control2 = Control("C2", cond2, act2)

app.append_control(control1)
app.append_control(control2)

@app.rackit(1)
def writer1():

    tag_egine.write_tag("T1", 15)
    tag_egine.write_tag("T2", 40)

    direction = 1

    while True:

        time.sleep(0.5)

        value = 24 + 2 * random()
        tag_egine.write_tag("RAND1", value)

        T1 = tag_egine.read_tag("T1")
        T1 += direction

        tag_egine.write_tag("T1", T1)

        if T1 >= 60:
            direction *= -1

        if T1 <= 5:
            direction *= -1

@app.rackit(1)
def writer2():

    while True:

        time.sleep(0.5)

        value = 48 + 2 * random()
        tag_egine.write_tag("RAND2", value)

@app.rackit_on(period=1)
def reader():

    rand1 = tag_egine.read_tag("RAND1")
    rand2 = tag_egine.read_tag("RAND2")
    T1 = tag_egine.read_tag("T1")
    T2 = tag_egine.read_tag("T2")
    T3 = tag_egine.read_tag("T3")
        
    print("")
    print("RAND1: {}".format(rand1))
    print("RAND2: {}".format(rand2))
    print("T1   : {}".format(T1))
    print("T2   : {}".format(T2))
    print("T3   : {}".format(T3))
        

if __name__ == "__main__":

    app.run()
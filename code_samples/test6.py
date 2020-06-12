import time

from rackio import Rackio, TagEngine
from rackio.controls import MathAction, Condition, Control
from rackio.alarms import HI, LO

from random import random
from math import sin

app = Rackio()

tag_egine = TagEngine()

# Tags definitions

tag_egine.set_tag("RAND1", "float")
tag_egine.set_tag("SINE_WAVE", "float")
tag_egine.set_tag("T1", "float")
tag_egine.set_tag("T2", "float")
tag_egine.set_tag("T3", "float")
tag_egine.set_tag("T4", "float")
tag_egine.set_tag("T5", "float")
tag_egine.set_tag("ALARM1", "bool")
tag_egine.set_tag("ALARM2", "bool")

tag_egine.set_tag("message", "str")

# Conditions definitions

cond1 = Condition("T1",">=", "T2")
cond2 = Condition("T1","<", "T2")

# Actions definitions

act1 = MathAction("T3", "T1 + T2")
act2 = MathAction("T3", "2 * T2 - T1")

# Controls Definitions

control1 = Control("C1", cond1, act1)
control2 = Control("C2", cond2, act2)

app.append_control(control1)
app.append_control(control2)

# Alarms definitions

from rackio.alarms import Alarm

alarm1 = Alarm("sine1", "SINE_WAVE", "Sine wave alarm")
alarm1.set_trigger(18.5, HI)
alarm1.set_tag_alarm("ALARM1")

alarm2 = Alarm("sine2", "SINE_WAVE", "Sine wave alarm")
alarm2.set_trigger(-18.20, LO)
alarm2.set_tag_alarm("ALARM2")

app.append_alarm(alarm1)
app.append_alarm(alarm2)

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
    x = 0
    while True:

        time.sleep(0.25)

        value = 20 * sin(x)
        tag_egine.write_tag("SINE_WAVE", value)

        x += 0.01

@app.rackit_on(period=1)
def reader():

    rand1 = tag_egine.read_tag("RAND1")
    sine_wave = tag_egine.read_tag("SINE_WAVE")
    T1 = tag_egine.read_tag("T1")
    T2 = tag_egine.read_tag("T2")
    T3 = tag_egine.read_tag("T3")
    T4 = tag_egine.read_tag("T4")
    T5 = tag_egine.read_tag("T5")
        
    print("")
    print("RAND1    : {}".format(rand1))
    print("sine_wave: {}".format(sine_wave))
    print("T1       : {}".format(T1))
    print("T2       : {}".format(T2))
    print("T3       : {}".format(T3))
    print("T4       : {}".format(T4))
    print("T5       : {}".format(T5))
        

if __name__ == "__main__":

    app.set_db("tags.db")
    app.set_log(file="app.log")
    app.set_dbtags(["RAND1", "RAND2", "T1", "T2", "T3"])
    app.run()


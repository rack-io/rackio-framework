# Rackio Framework
A modern Python Framework for microboard automation and control applications development.
[Github-Rackio Framework](https://github.com/rack-io/rackio-framework)

## Requirements

Python 3.6+
falcon 
pyBigParser

# Installation

```
pip install Rackio
```

# Examples

## Basic Setup

```python
from rackio import Rackio, TagEngine
from rackio.models import Tag

app = Rackio()
tag_egine = TagEngine()

# Tags definitions

tag_egine.set_tag("RAND1", "float")
tag_egine.set_tag("RAND2", "float")
tag_egine.set_tag("T1", "float")
tag_egine.set_tag("T2", "float")
tag_egine.set_tag("T3", "float")

if __name__ == "__main__":

    app.run()
```

Rackio comes with some built-in features that let you start creating rapid and fast coding prototypes.

## Adding some controls
```python
# Conditions definitions

cond1 = Condition("T1",">=", "T2")
cond2 = Condition("T1","<", "T2")

# Actions definitions

act1 = Action("T3", 40)
act2 = Action("T3", 80)

# Controls Definitions

control1 = Control("C1", cond1, act1)
control2 = Control("C2", cond2, act2)

app.append_control(control1)
app.append_control(control2)
```

Once Rackio is up and running, will trigger some actions if the associated condtions are met, by observing continously all the tags values for changes.

## Adding some continous tasks

Rackio can be extended to add custom continous tasks and operations

```python
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
```

You can register a defined function as a continous task to be perform by Rackio. You can also provide functions as tasks lists

```python
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
```

By specify its ```period```, you can keep control of the time execution for these tasks.

# Things to do

Rackio is work in progress framework, some features are still in development and they will be release soon for better applications, these features are listed below:

* RESTful API
* Web Based Monitoring and Admin
* Alarms definitions
* Modbus and MQTT protocols
* Automatic Datalogging
* Trends and Historical data
* Math evaluations in actions objects
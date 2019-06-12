# Rackio Framework
A modern Python Framework for microboard automation and control applications development.
[Github-Rackio Framework](https://github.com/rack-io/rackio-framework)

## Requirements

- Python 3.6+
- falcon 
- pyBigParser

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

# Adding controls

Controls are objects that interact with the tags, changing their values accordingly to a condition

### Value Actions

These actions only change tags values with a defined constant value.

```python
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
```

### Math Actions

These actions change tags values with a defined mathematical expression, and defined tags can be used inside these expressions.

```python
# Conditions definitions

cond1 = Condition("T1",">=", "T2")
cond2 = Condition("T1","<", "T2")

# Actions definitions

act1 = MathAction("T3", "T1 + T2")
act2 = MathAction("T3", "T2 - T1")

# Controls Definitions

control1 = Control("C1", cond1, act1)
control2 = Control("C2", cond2, act2)

app.append_control(control1)
app.append_control(control2)
```

Once Rackio is up and running, will trigger some actions if the associated condtions are met, by observing continously all the tags values for changes.

## Supported functions within expressions

You can define your mathematical expression following the same arithmetic rules that python can handle, but only a set of math functions and constants are supported.

*  ```cos```
*  ```sin```
*  ```abs```
*  ```log10```
*  ```log```
*  ```exp``` 
*  ```tan```
*  ```pi```
*  ```e```

## Adding continous tasks

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

# Testing the RESTful API

Once your application is up and running, it will deploy a RESTful API with ```falcon```, and the ```json``` format is the standard supported by this API.

## Reading tags with httpie

Once your application is up and running you can access through the API, if you want to try with ```httpie```, you can install it with the following command:

```
pip install httpie
```

Now execute the next command in your terminal

```
http localhost:8000/api/tags
```

you will get the following

```http
HTTP/1.0 200 OK
Date: Tue, 11 Jun 2019 23:54:55 GMT
Server: WSGIServer/0.2 CPython/3.7.1
content-length: 177
content-type: application/json
```
```json
[
    {
        "tag": "RAND1",
        "value": 25.597755601381692
    },
    {
        "tag": "RAND2",
        "value": 49.12890172456638
    },
    {
        "tag": "T1",
        "value": 57
    },
    {
        "tag": "T2",
        "value": 40
    },
    {
        "tag": "T3",
        "value": 97
    }
]
```

if you want to access an specific tag, for example tag ```T2```

```
http localhost:8000/api/tags/T2
```

you will get the following

```http
HTTP/1.0 200 OK
Date: Tue, 11 Jun 2019 23:58:40 GMT
Server: WSGIServer/0.2 CPython/3.7.1
content-length: 26
content-type: application/json
```
```json
{
    "tag": "T2",
    "value": 40
}
```

## Writing tags with httpie
You can change this tag value by executing

```
http POST localhost:8000/api/tags/T2 value=50
```

And you will get the following

```http
HTTP/1.0 200 OK
Date: Wed, 12 Jun 2019 00:01:21 GMT
Server: WSGIServer/0.2 CPython/3.7.1
content-length: 16
content-type: application/json
```
```json
{
    "result": true
}
```

This way you can create your custom HMTL and Javascript Views to perform ```AJAX``` requests on Rackio.

# Things to do

Rackio is work in progress framework, some features are still in development and they will be release soon for better applications, these features are listed below:

* Finish RESTful API
* Capability for users to add custom HTML files for HMI
* Token Based Authentication for API access
* Web Based Monitoring and Admin
* Alarms definitions
* Modbus and MQTT protocols
* Automatic Datalogging
* Trends and Historical data
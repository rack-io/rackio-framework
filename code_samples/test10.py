# tag_binds.py
import logging

from rackio import Rackio, TagEngine

from rackio import RackioStateMachine, State, TagBinding

from rackio.models import Model, FloatField, IntegerField, BooleanField

from random import random

app = Rackio()

tag_egine = TagEngine()

# Tags definitions

tag_egine.set_tag("T1", "float")
tag_egine.set_tag("T2", "float")

class TwoStep(RackioStateMachine):

    # states

    state1  = State('State1', initial=True)
    state2  = State('State2')

    # transitions
    
    forward = state1.to(state2)
    back = state2.to(state1)

    # parameters

    count = 0

    engine_size = FloatField(default=1.8)
    seats = IntegerField(default=5)
    air_conditioning = BooleanField(default=True)

    # bindings

    T1 = TagBinding("T1")
    T2 = TagBinding("T2", direction="write")
    
    def on_back(self):

        self.count = 0

    def on_forward(self, *args):

        param = args[0]
        print("Forwarded : {}".format(param))

    def while_state1(self):

        self.count += 1
        
        logging.warning("{}: {}".format(self.name, self.count))
        if self.count == 5:
            self.forward("Flag")

    def while_state2(self):

        self.count += 1

        self.T2 = random()

        logging.warning("{}: {}".format(self.name, self.count))
        
        if self.count >= 10:
            self.tag_engine.write_tag("T1", random())
            self.back()

app = Rackio()

machine1 = TwoStep("machine 1")

app.append_machine(machine1, 1)

if __name__ == "__main__":

    app.set_log(file="app.log")
    app.run()

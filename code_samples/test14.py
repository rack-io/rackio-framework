import time
import logging

from rackio import Rackio, TagEngine
from rackio.controls import Condition
from rackio import RackioStateMachine, State

tag_engine = TagEngine()

tag_engine.set_tag("BASE", "str")
tag_engine.set_tag("TARGET1", "str")
tag_engine.set_tag("TARGET2", "str")

tag_engine.write_tag("BASE", "Default")
tag_engine.write_tag("TARGET1", "TransitionFordward")
tag_engine.write_tag("TARGET2", "TransitionBack")

condition1 = Condition("BASE", "==", "TARGET1")
condition2 = Condition("BASE", "==", "TARGET2")


class TwoStep(RackioStateMachine):

    # states

    state1  = State('State1', initial=True)
    state2  = State('State2')

    # transitions
    
    forward = state1.to(state2, trigger=condition1)
    back = state2.to(state1, trigger=condition2)

    # parameters

    count = 0

    def on_back(self):

        self.count = 0

    def while_state1(self):

        self.count += 1

        logging.warning("{}: {}".format(self.name, self.count))

    def while_state2(self):

        self.count -= 1

        logging.warning("{}: {}".format(self.name, self.count))

app = Rackio()

machine1 = TwoStep("machine 1")
machine2 = TwoStep("machine 2")

app.append_machine(machine1, 1, "async")
app.append_machine(machine2, 2, "async")

if __name__ == "__main__":

    app.set_log(file="app.log")
    app.run()


import time
import logging

from rackio import Rackio, TagEngine

from rackio import RackioStateMachine, State, TagBinding, GroupBinding

from rackio_swagger import RackioSwagger

input_tags = [
    ("T1", "float"),
    ("T2", "float")
]

output_tags = [
    ("T3", "float"),
    ("T4", "float")
]

tag_engine = TagEngine()

tag_engine.set_group("input", input_tags)
tag_engine.set_group("output", output_tags)


class TwoStep(RackioStateMachine):

    # states

    state1  = State('State1', initial=True)
    state2  = State('State2')

    # transitions
    
    forward = state1.to(state2)
    back = state2.to(state1)

    # parameters

    count = 0

    # Bindings

    begin = GroupBinding("input")
    end = GroupBinding("output", direction="write")

    def on_back(self):

        self.count = 0

    def while_state1(self):

        self.count += 1

        logging.warning("{}: {}".format(self.name, self.count))
        if self.count == 4:
            self.forward()

    def while_state2(self):

        self.count += 1

        T1 = self.begin.T1
        T2 = self.begin.T2

        self.end.T3 = T1 + T2
        self.end.T4 = T1 - T2

        logging.warning("{}: {}".format(self.name, self.count))
        if self.count >= 10:
            self.back()

app = Rackio()

RackioSwagger(app)

machine = TwoStep("machine")

app.append_machine(machine, 1)

if __name__ == "__main__":

    app.set_log(file="app.log")
    app.run()


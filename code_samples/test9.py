import time
import logging

from rackio import Rackio

from rackio import RackioStateMachine, State

class TwoStep(RackioStateMachine):

    # states

    state1  = State('State1', initial=True)
    state2  = State('State2')

    # transitions
    
    forward = state1.to(state2)
    back = state2.to(state1)

    # parameters

    count = 0

    def on_back(self):

        self.count = 0

    def while_state1(self):

        self.count += 1

        logging.warning("{}: {}".format(self.name, self.count))
        if self.count == 5:
            self.forward()

    def while_state2(self):

        self.count += 1

        logging.warning("{}: {}".format(self.name, self.count))
        if self.count >= 10:
            self.back()

app = Rackio()

machine1 = TwoStep("machine 1")
machine2 = TwoStep("machine 2")

app.append_machine(machine1, 1)
app.append_machine(machine2, 2)

if __name__ == "__main__":

    app.set_log(file="app.log")
    app.run()


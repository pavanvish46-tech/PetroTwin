from ml.digital_twin.twin_engine import DigitalTwin

class Simulator:
    def __init__(self,twin=None):
        self.twin=twin or DigitalTwin()

    def run(self,state,scenario):
        return self.twin.simulate(state,scenario)

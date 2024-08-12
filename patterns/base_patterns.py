class BasePattern:
    def __init__(self):
        pass

    def identify(self, candles):
        raise NotImplementedError("Subclasses must implement this method")
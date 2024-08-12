class BasePattern:
    def __init__(self, candles):
        self.candles = candles[-80:]  # Limitar a las últimas 80 velas

    def identify(self):
        raise NotImplementedError("Cada patrón debe implementar su propio método de identificación")

    def is_bullish(self):
        raise NotImplementedError("Cada patrón debe implementar este método")
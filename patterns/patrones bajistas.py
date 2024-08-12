from .base_pattern import BasePattern

class BearishEngulfing(BasePattern):
    def identify(self):
        last_candle = self.candles[0]
        previous_candle = self.candles[1]
        return (last_candle['close'] < previous_candle['open'] and 
                last_candle['open'] > previous_candle['close'] and
                last_candle['close'] < last_candle['open'])

    def is_bullish(self):
        return False

class EveningStar(BasePattern):
    def identify(self):
        if len(self.candles) < 3:
            return False
        
        first_candle = self.candles[2]
        second_candle = self.candles[1]
        third_candle = self.candles[0]
        
        return (first_candle['close'] > first_candle['open'] and
                abs(second_candle['close'] - second_candle['open']) < abs(first_candle['close'] - first_candle['open']) * 0.1 and
                third_candle['close'] < third_candle['open'] and
                third_candle['close'] < (first_candle['open'] + first_candle['close']) / 2)

    def is_bullish(self):
        return False
import logging
import time
from iqoptionapi.stable_api import IQ_Option
from config import USERNAME, PASSWORD, ACCOUNT_TYPE, LOT_SIZE
from utils.iq_option_utils import login_iq_option, get_available_pairs
from patterns.bullish_patterns import BullishHammer, BullishEngulfing, MorningStar
from patterns.bearish_patterns import BearishEngulfing, EveningStar

logging.basicConfig(level=logging.INFO, format='%(asctime)s %(message)s')

def trading_strategy(iq, pair, candles, lot_size):
    supports, resistances = identify_static_support_resistance(candles)
    dynamic_support, dynamic_resistance = identify_dynamic_support_resistance(candles)
    pattern = analyze_candle_patterns(candles)
    signal_confirmed = confirm_signal_with_volume(candles)
    line_trend = analyze_line_chart(iq, pair)
    wave_pattern = analyze_elliott_waves(candles)

    decision = None
    current_price = candles[0]['close']

    # Estrategia de Tendencia
    if line_trend == "up":
        if pattern in ["bullish_engulfing", "morning_star", "three_white_soldiers"]:
            decision = "call"
    elif line_trend == "down":
        if pattern in ["bearish_engulfing", "evening_star", "three_black_crows"]:
            decision = "put"

    # Estrategia de Soportes y Resistencias
    if pattern in ["bullish_hammer", "morning_star", "three_white_soldiers", "ascending_triangle"] and signal_confirmed:
        if current_price <= supports[-1]:
            decision = "call"
        elif current_price >= dynamic_support:
            decision = "call"
    elif pattern in ["bearish_engulfing", "evening_star", "three_black_crows", "descending_triangle"] and signal_confirmed:
        if current_price >= resistances[-1]:
            decision = "put"
        elif current_price <= dynamic_resistance:
            decision = "put"

    # Aplicar Precauciones y Evitar Errores Comunes
    decision = apply_precautions_and_avoid_errors(candles, decision, pattern, supports, resistances)

    if decision:
        logging.info(f"Se está analizando el par de divisas {pair}. En la siguiente vela se va a realizar una operación {decision}.")
        execute_trade(iq, pair, decision, lot_size)

def identify_static_support_resistance(candles):
    supports = []
    resistances = []

    for i in range(1, len(candles) - 1):
        current = candles[i]['close']
        previous = candles[i - 1]['close']
        next_candle = candles[i + 1]['close']

        if current < previous and current < next_candle:
            supports.append(current)
        
        if current > previous and current > next_candle:
            resistances.append(current)

    supports = sorted(list(set(supports)))
    resistances = sorted(list(set(resistances)), reverse=True)

    logging.info(f"Soportes identificados: {supports}")
    logging.info(f"Resistencias identificadas: {resistances}")
    
    return supports, resistances

def identify_dynamic_support_resistance(candles):
    dynamic_support = min(candle['close'] for candle in candles)
    dynamic_resistance = max(candle['close'] for candle in candles)
    
    logging.info(f"Soporte dinámico identificado: {dynamic_support}")
    logging.info(f"Resistencia dinámica identificada: {dynamic_resistance}")
    
    return dynamic_support, dynamic_resistance

def analyze_candle_patterns(candles):
    pattern = None
    last_candle = candles[0]
    previous_candle = candles[1]
    body_size = abs(last_candle['close'] - last_candle['open'])
    upper_shadow = last_candle['high'] - max(last_candle['close'], last_candle['open'])
    lower_shadow = min(last_candle['close'], last_candle['open']) - last_candle['low']

    if lower_shadow > body_size * 2 and upper_shadow < body_size * 0.5 and last_candle['close'] > last_candle['open']:
        pattern = "bullish_hammer"
    elif last_candle['close'] > previous_candle['open'] and last_candle['open'] < previous_candle['close']:
        pattern = "bullish_engulfing"
    elif last_candle['close'] < previous_candle['open'] and last_candle['open'] > previous_candle['close']:
        pattern = "bearish_engulfing"
    elif previous_candle['close'] < previous_candle['open'] and last_candle['close'] > last_candle['open'] and candles[2]['close'] < candles[2]['open']:
        pattern = "morning_star"
    elif previous_candle['close'] > previous_candle['open'] and last_candle['close'] < last_candle['open'] and candles[2]['close'] > candles[2]['open']:
        pattern = "evening_star"
    
    logging.info(f"Patrón de velas identificado: {pattern}")
    return pattern

def confirm_signal_with_volume(candles):
    last_candle = candles[0]
    previous_candle = candles[1]

    if last_candle['volume'] > previous_candle['volume']:
        logging.info("Señal confirmada por aumento de volumen")
        return True
    else:
        logging.info("No se confirmó la señal por volumen")
        return False

def analyze_line_chart(iq, pair):
    candles = iq.get_candles(pair, 1, 30, time.time())  # 30 velas de 1 segundo
    line_trend = "neutral"
    highs = [candle['high'] for candle in candles]
    lows = [candle['low'] for candle in candles]

    if highs[-1] > highs[0] and lows[-1] > lows[0]:
        line_trend = "up"
    elif highs[-1] < highs[0] and lows[-1] < lows[0]:
        line_trend = "down"
    
    logging.info(f"Tendencia en gráfico de líneas (1s): {line_trend}")
    return line_trend

def analyze_elliott_waves(candles):
    wave_pattern = None

    if len(candles) >= 5:
        if (candles[0]['close'] > candles[1]['close'] > candles[2]['close'] and
            candles[3]['close'] < candles[2]['close'] and
            candles[4]['close'] > candles[3]['close']):
            wave_pattern = "impulsive_wave"
        elif (candles[0]['close'] < candles[1]['close'] < candles[2]['close'] and
              candles[3]['close'] > candles[2]['close'] and
              candles[4]['close'] < candles[3]['close']):
            wave_pattern = "corrective_wave"

    logging.info(f"Patrón de ondas de Elliott identificado: {wave_pattern}")
    return wave_pattern

def apply_precautions_and_avoid_errors(candles, decision, pattern, supports, resistances):
    last_candle = candles[0]
    previous_candle = candles[1]
    overall_trend = analyze_overall_market_trend(candles)

    # 1. No Confirmar la Ruptura
    if decision == "call" and last_candle['close'] > resistances[0] and pattern in ["doji", "spinning_top"]:
        logging.warning("Evitar operación: Ruptura no confirmada con fuerza suficiente.")
        return None
    elif decision == "put" and last_candle['close'] < supports[0] and pattern in ["doji", "spinning_top"]:
        logging.warning("Evitar operación: Ruptura no confirmada con fuerza suficiente.")
        return None

    # 2. Ignorar el Contexto del Mercado
    if decision == "call" and overall_trend == "down":
        logging.warning("Evitar operación: Operando en contra de la tendencia general bajista.")
        return None
    elif decision == "put" and overall_trend == "up":
        logging.warning("Evitar operación: Operando en contra de la tendencia general alcista.")
        return None

    # 3. Operar en Niveles Débiles
    if decision == "call" and len(supports) < 2:
        logging.warning("Evitar operación: Soporte débil, ha sido tocado pocas veces.")
        return None
    elif decision == "put" and len(resistances) < 2:
        logging.warning("Evitar operación: Resistencia débil, ha sido tocada pocas veces.")
        return None

    return decision

def analyze_overall_market_trend(candles):
    trend = "neutral"
    if candles[-1]['close'] > candles[-5]['close']:
        trend = "up"
    elif candles[-1]['close'] < candles[-5]['close']:
        trend = "down"
    
    logging.info(f"Tendencia general del mercado: {trend}")
    return trend

def execute_trade(iq, pair, action, lot_size):
    duration = 1  # Expiración en minutos
    direction = "call" if action == "call" else "put"
    
    check, trade_id = iq.buy(lot_size, pair, direction, duration)
    if check:
        logging.info(f"Operación ejecutada: {action} en {pair} con monto de {lot_size} USD.")
    else:
        logging.error("Falló la ejecución de la operación")
def main():
    iq = login_iq_option(USERNAME, PASSWORD, ACCOUNT_TYPE)
    if iq is None:
        return
    
    pairs = get_available_pairs(iq)
    selected_pair = pairs[0]  # Selecciona el primer par disponible
    operation_count = 0
    consecutive_losses = 0
    while operation_count < 25 and consecutive_losses < 3:
        try:
            candles = iq.get_candles(selected_pair, 60, 15, time.time())
            trading_strategy(iq, selected_pair, candles, LOT_SIZE)
            operation_count += 1
            time.sleep(1)
        except KeyboardInterrupt:
            logging.info("Bot detenido por el usuario")
            break
    
    logging.info(f"Sesión terminada. Operaciones realizadas: {operation_count}, Pérdidas consecutivas: {consecutive_losses}")

if __name__ == "__main__":
    main()
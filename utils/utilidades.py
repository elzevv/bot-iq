import logging
from iqoptionapi.stable_api import IQ_Option

def login_iq_option(username, password, account_type="demo"):
    iq = IQ_Option(username, password)
    check, reason = iq.connect()
    if check:
        logging.info("Inicio de sesión exitoso")
        iq.change_balance(account_type)
        return iq
    else:
        logging.error(f"Falló la autenticación: {reason}")
        return None

def get_available_pairs(iq):
    pairs = iq.get_all_open_time()
    available_pairs = [pair for pair in pairs['turbo'] if pairs['turbo'][pair]['open']]
    logging.info(f"Pares disponibles: {available_pairs}")
    return available_pairs
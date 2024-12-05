from prettytable import PrettyTable
import logging
import colorlog


# Setup Logging mit colorlog (optional)
def setup_logging():
    handler = colorlog.StreamHandler()
    formatter = colorlog.ColoredFormatter(
        "%(log_color)s%(asctime)s - %(levelname)s - %(message)s",
        log_colors={
            "DEBUG": "cyan",
            "INFO": "green",
            "WARNING": "yellow",
            "ERROR": "red",
            "CRITICAL": "bold_red",
        },
        datefmt="%Y-%m-%d %H:%M:%S",
    )
    handler.setFormatter(formatter)
    root_logger = logging.getLogger()
    root_logger.setLevel(logging.DEBUG)
    root_logger.addHandler(handler)


# Funktion zur dynamischen Erstellung von PrettyTable
def render_dynamic_table(data):
    """
    Render a PrettyTable dynamically based on the input data.
    :param data: List of dictionaries or list of lists with headers as keys.
    """
    if not data:
        logging.warning("Keine Daten vorhanden, um eine Tabelle zu rendern.")
        return

    # Erstelle Tabelle
    table = PrettyTable()

    if isinstance(data[0], dict):
        # Verwende die Keys der ersten Zeile als Headers
        headers = list(data[0].keys())
        table.field_names = headers
        for row in data:
            table.add_row([row[header] for header in headers])
    elif isinstance(data[0], list):
        # Falls es bereits eine Liste von Listen ist, definiere explizit die Spaltennamen
        headers = data.pop(0)  # Erste Zeile als Header verwenden
        table.field_names = headers
        for row in data:
            table.add_row(row)
    else:
        logging.error("Ungültiges Datenformat. Unterstützt werden Listen von Dictionairies oder Listen von Listen.")
        return

    # Logge die dynamisch generierte Tabelle
    logging.info(f"\n{table}")


# Logging Setup
setup_logging()

# Dynamische Daten
data_dict = []

data_list = []

# Beispiele
render_dynamic_table(data_dict)  # Daten als Liste von Dictionaries
render_dynamic_table(data_list)  # Daten als Liste von Listen
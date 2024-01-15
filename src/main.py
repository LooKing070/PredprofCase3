import logging

logging.basicConfig(filename="game_logs",
                    filemode='w',
                    format='%(asctime)s %(filename)s: %(levelname)s "%(message)s" at line %(lineno)d',
                    datefmt='%H:%M:%S',
                    level=logging.DEBUG)

try:
    pass  # код запуска приложения
except Exception as e:
    logging.critical(e, exc_info=True)

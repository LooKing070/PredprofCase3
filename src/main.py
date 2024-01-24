import logging
import sys
from PyQt5.QtWidgets import QApplication
import window_manager

# self.settingsWindow.setWindowIcon(QIcon("../icons/AirBanIcon.jpg"))

logging.basicConfig(filename="logs",
                    filemode='w',
                    format='%(asctime)s %(filename)s: %(levelname)s "%(message)s" at line %(lineno)d',
                    datefmt='%H:%M:%S',
                    level=logging.DEBUG)


def main():
    app = QApplication(sys.argv)
    ex = window_manager.MyWidget()
    ex.show()
    sys.excepthook = except_hook
    sys.exit(app.exec_())


def except_hook(cls, exception, traceback):
    sys.__excepthook__(cls, exception, traceback)


if __name__ == "__main__":
    try:
        main()
        logging.info("Программа завершила работу")
    except Exception as e:
        logging.critical(e, exc_info=True)

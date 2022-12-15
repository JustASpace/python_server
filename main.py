from configparser import ConfigParser
from server import Server
import logging
import logging.handlers


def init_logger(name):
    logger = logging.getLogger(name)
    FORMAT = '%(asctime)s - %(name)s:%(lineno)s - %(levelname)s - %(message)s'
    logger.setLevel(logging.DEBUG)
    sh = logging.StreamHandler()
    sh.setFormatter(logging.Formatter(FORMAT))
    sh.setLevel(logging.DEBUG)
    fh = logging.handlers.RotatingFileHandler(filename="test.log")
    fh.setFormatter(logging.Formatter(FORMAT))
    fh.setLevel(logging.DEBUG)
    logger.addHandler(sh)
    logger.addHandler(fh)
    logger.debug("Logger was initialized")


init_logger("app")
logger = logging.getLogger("app.main")

if __name__ == '__main__':
    config = ConfigParser()
    config.read('config.ini')
    for name in config.sections():
        server = Server(config[name]['host'],
                        int(config[name]['port']),
                        config[name]['server_name'],
                        config[name]['directory'])
        server.start()

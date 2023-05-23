import logging


class Logger:
    loggers = {}

    def __init__(self, log_file):
        self.log_file = log_file
        self.logger = logging.getLogger("MyLogger")
        self.logger.setLevel(logging.INFO)
        self.file_handler = logging.FileHandler(log_file)
        self.file_handler.setLevel(logging.INFO)
        self.formatter = logging.Formatter(
            "%(asctime)s - %(levelname)s - %(message)s")
        self.file_handler.setFormatter(self.formatter)
        self.logger.addHandler(self.file_handler)

    @classmethod #my first classmethod :v idk
    def create_logger(cls, log_file, name):
        if name in cls.loggers:
            return cls.loggers[name]
        else:
            logger = logging.getLogger(name)
            logger.setLevel(logging.INFO)
            file_handler = logging.FileHandler(log_file)
            file_handler.setLevel(logging.INFO)
            formatter = logging.Formatter(
                "%(asctime)s - %(levelname)s - %(message)s")
            file_handler.setFormatter(formatter)
            logger.addHandler(file_handler)
            cls.loggers[name] = logger
            return logger

    def log_info(self, message):
        self.logger.info(message)

    def log_warning(self, message):
        self.logger.warning(message)

    def log_error(self, message):
        self.logger.error(message)

    def log_critical(self, message):
        self.logger.critical(message)

"""Artifi Logging Configuration"""
import faulthandler
import logging
import os
import sys


class Logger:
    """Logger configuration"""

    def __init__(self, name, log_file):
        """Logger configuration"""
        self._name = name
        self._log_path = os.path.join(os.getcwd(), log_file)
        faulthandler.enable(file=sys.stderr)
        logging.basicConfig(
            format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
            datefmt="%d-%b-%y %H:%M:%S",
            handlers=[
                logging.FileHandler(filename=self._log_path, encoding="utf-8"),
                logging.StreamHandler(),
            ],
            level=logging.INFO,
        )
        self._logger = logging.getLogger(name)

    @property
    def logger(self) -> logging.Logger:
        """
        logger function
        @return:
        """
        return self._logger

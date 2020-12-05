"""
    Namd Restarter - Automatically restart namd dynamics
    Copyright (C) 2020  Arthur Pereira da Fonseca

    This program is free software: you can redistribute it and/or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation, either version 3 of the License, or
    any later version.

    This program is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU General Public License for more details.

    You should have received a copy of the GNU General Public License
    along with this program.  If not, see <https://www.gnu.org/licenses/>.

    Mail: arthurpfonseca3k@gmail.com
"""

import logging


class CustomFormatter(logging.Formatter):
    """Logging Formatter to add colors and my format"""

    white = "\033[37m"
    cyan = "\033[34m"
    yellow = "\033[33m"
    red = "\033[31m"
    bold_red = "\033[31;1m"
    reset = "\033[0m"
    format = "[%(levelname)s] %(message)s"

    FORMATS = {
        logging.DEBUG: white + format + reset,
        logging.INFO: cyan + format + reset,
        logging.WARNING: yellow + format + reset,
        logging.ERROR: red + format + reset,
        logging.CRITICAL: bold_red + format + reset
    }

    def format(self, record):
        """Add my style to original logging"""

        log_fmt = self.FORMATS.get(record.levelno)
        formatter = logging.Formatter(log_fmt)
        return formatter.format(record)


# create logger
logger = logging.getLogger()
logger.setLevel(logging.DEBUG)

# create console handler with a higher log level
ch = logging.StreamHandler()
ch.setLevel(logging.DEBUG)
ch.setFormatter(CustomFormatter())
logger.addHandler(ch)


def log(log_type, message):
    """Log function to export"""

    if log_type == 'debug':
        logger.debug(message)
    elif log_type == 'info':
        logger.info(message)
    elif log_type == 'warning':
        logger.warning(message)
    elif log_type == 'error':
        logger.error(message)
    elif log_type == 'critical':
        logger.critical(message)

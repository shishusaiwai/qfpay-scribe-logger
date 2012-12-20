"""Scribe Logger Class

This class handles overwriting logging to send to a scribe instance.

"""
from qfpay_scribe_logger.writer import ScribeWriter
import logging
import logging.handlers


class ScribeLogHandler(logging.Handler, ScribeWriter):
    """"""
    def __init__(self, category=None, extra=None,
            backup_file="", host='127.0.0.1', port=1463):
        logging.Handler.__init__(self)

        if category:
            self.category = category

        if extra:
            self.extra = ' '.join(extra)
        else:
            self.extra = ''

        self.backup_file = backup_file
        if not self.backup_file:
            raise AttributeError("No backup file supplied.")

        ScribeWriter.__init__(self, host, port, self.category)

    def set_category(self, category):
        self._category = category

    def get_category(self):
        return getattr(self, '_category', 'default')

    category = property(get_category, set_category)

    def emit(self, msg):
        msg = "%s %s" % (self.extra, self.format(msg))

        try:
            self.write(self.category, msg)
        except (KeyboardInterrupt, SystemExit):
            raise
        except:
            self.handleError(msg)

    def flush(self):
        pass

    def handleError(self, msg):
        with open(self.backup_file, 'a') as f:
            msg = msg.strip()
            msg += "\n"
            f.write(msg)

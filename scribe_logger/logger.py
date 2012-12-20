"""Scribe Logger Class

This class handles overwriting logging to send to a scribe instance.

"""
from scribe_logger.writer import ScribeWriter
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

    def emit(self, record):
        record = "%s %s" % (self.extra, self.format(record))

        try:
            self.write(self.category, record)
        except (KeyboardInterrupt, SystemExit):
            raise
        except:
            self.handleError(record)

    def flush(self):
        pass

    def handleError(self, record):
        with open(self.backup_file, 'w') as f:
            msg = record.getMessage()
            if len(msg) >= 1:
                tail = msg[-1]
                if tail != "\n":
                    msg += "\n"
            f.write(msg)

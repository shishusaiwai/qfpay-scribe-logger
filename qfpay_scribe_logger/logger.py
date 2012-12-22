"""Scribe Logger Class

This class handles overwriting logging to send to a scribe instance.

"""
import functools
import logging
import logging.handlers
import threading
import time

from qfpay_scribe_logger.logbuffer import LogBuffer
from qfpay_scribe_logger.writer import ScribeWriter

DEFAULT_RETRY_INTERVAL = 5  # 5s


class ScribeLogHandler(logging.Handler):
    """"""
    def __init__(self, backup_file, category, extra=None,
             host='127.0.0.1', port=1463,
             retry_interval=DEFAULT_RETRY_INTERVAL):

        logging.Handler.__init__(self)
        self.category = category
        self.retry_interval = retry_interval
        self.log_buffer = LogBuffer(backup_file)
        self.writer = ScribeWriter(host, port, self.category)
        self.category_write = \
                functools.partial(self.writer.write, self.category)
        self.scribe_watcher = threading.Thread(target=self.handle_buffer)
        self.scribe_watcher.start()
        print "start the scribe_watcher"
        if extra:
            self.extra = ' '.join(extra)
        else:
            self.extra = ''

    def set_category(self, category):
        self._category = category

    def get_category(self):
        return getattr(self, '_category', 'default')

    category = property(get_category, set_category)

    def scribe_write(self, msg):
        if len(msg) >= 1 and msg[-1] != "\n":
            beautiful_msg = "%s\n" % msg
        try:
            self.category_write(beautiful_msg)
        except:
            return False
        return True

    def emit(self, record):
        msg = self.format(record)
        if self.extra:
            msg = "%s %s" % (self.extra, msg)
        if not self.scribe_write(msg):
            self.handleError(msg)

    def flush(self):
        pass

    def handleError(self, msg):
        self.log_buffer.add_log(msg)

    def handle_buffer(self):
        while True:
            if self.writer.is_scribe_ready() and self.log_buffer.has_log():
                self.log_buffer.clean_oldest_group(self.scribe_write)
            else:
                time.sleep(self.retry_interval)

import os
import re
import shutil
import threading

from qfpay_scribe_logger.utils import file_size, ensure_path


DEFAULT_MAX_FILE_SIZE = 1000000  # about 1M
FILENAME_REGEX_PATTERN = "^%s.([0-9]+)$"
LOG_START_REGEX = re.compile("^20[0-9]{2}")


def is_log_start(msg):
    return True if LOG_START_REGEX.match(msg) else False


def generate_log_array(raw_msg_arr):
    '''
    >>> generate_log_array(['a','d'])
    ['a\\nd']
    >>> generate_log_array(['a', '2012', 'c'])
    ['a', '2012\\nc']
    '''
    log_arr = []
    last_start_line_n = 0
    for line_n, msg in enumerate(raw_msg_arr):
        if line_n > 0 and is_log_start(msg):
            msg_parts = raw_msg_arr[last_start_line_n: line_n]
            current_msg = "\n".join(msg_parts)
            log_arr.append(current_msg)
            last_start_line_n = line_n
    msg_parts = raw_msg_arr[last_start_line_n:]
    last_log = "\n".join(msg_parts)
    log_arr.append(last_log)
    return log_arr


class LogBuffer(object):

    def __init__(self, abs_path, max_file_size=DEFAULT_MAX_FILE_SIZE):
        self.folder, self.filename = (os.path.dirname(abs_path),
                os.path.basename(abs_path))
        self.max_file_size = max_file_size
        self.filename_regex = \
                re.compile(FILENAME_REGEX_PATTERN % self.filename)
        self.handle_lock = threading.RLock()

    @property
    def current_log_file(self):
        abs_path = os.path.join(self.folder, self.filename)
        ensure_path(abs_path)
        return abs_path

    def _get_oldest_index(self):
        '''
        The smallest number is the oldest.
        When no file with suffix exists, return 0
        '''
        filenames = os.listdir(self.folder)
        indexes = [int(self.match(fn).group(1))
                for fn in filenames if self.filename_regex.match(fn)]
        if not indexes:
            # no file exists except file<abs_path>
            return 0
        return min(indexes)

    @property
    def oldest_group_file(self):
        index = self._get_oldest_index()
        fn = "%s.%s" % (self.filename, index) \
                if index != 0 else self.filename
        abs_path = os.path.join(self.folder, fn)
        return abs_path

    def _get_oldest_group(self):
        with open(self.oldest_group_file, 'r') as f:
            raw_lines = [line.strip() for line in f.readlines() if line]
            group = generate_log_array(raw_lines)
        return group

    def _rewrite_oldest_group(self, new_group):
        content = "\n".join(new_group)
        with open(self.oldest_group_file, 'w') as f:
            f.write(content)

    def _delete_oldest_group(self):
        os.remove(self.oldest_group_file)

    def _generate_next_filename(self):
        last_index = self._get_oldest_index()
        new_index = last_index + 1
        return "%s.%s" % (self.filename, new_index)

    def has_log(self):
        if self._get_oldest_index() > 0:
            return True
        else:
            # allow for a return, it's a little arbitrary.
            return True if file_size(self.current_log_file) > 1 \
                    else False

    def add_log(self, msg):
        '''
        Interface to write log.
        '''
        with self.handle_lock:
            if file_size(self.current_log_file) + len(msg) \
                    > self.max_file_size:
                new_backup_filename = self._generate_next_filename()
                shutil.move(self.current_log_file,
                        os.path.join(self.folder, new_backup_filename))
            with open(self.current_log_file, 'a') as f:
                f.write("%s\n" % msg)

    def clean_oldest_group(self, retry_func):
        '''
        Interface to clean buffer.
        '''
        with self.handle_lock:
            oldest_group = self._get_oldest_group()
            for log in oldest_group:
                if retry_func(log):
                    oldest_group.remove(log)
            if oldest_group:
                self._rewrite_oldest_group(oldest_group)
            else:
                self._delete_oldest_group()

if __name__ == "__main__":
    import doctest
    doctest.testmod()

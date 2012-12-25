import os


def touch(fname, times=None):
    '''
    stolen from http://darklaunch.com/2012/07/10/python-touch-file
    '''
    with file(fname, 'wa'):
        os.utime(fname, times)


def file_size(abs_path):
    f_stat = os.stat(abs_path)
    return f_stat.st_size


def ensure_path(abs_path):
    folder, filename = (os.path.dirname(abs_path),
            os.path.basename(abs_path))
    if not os.path.exists(folder):
        os.makedirs(folder)
    if not os.path.exists(abs_path):
        touch(abs_path)


if __name__ == "__main__":
    pass

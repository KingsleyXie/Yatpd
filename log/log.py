from sys import stdout
from datetime import datetime


class Log:
    def __init__(self, component, filename=None):
        self.component = component
        self._logger = open(filename, 'a', buffering=1) if filename else stdout

    def __del__(self):
        self._logger.close()

    def append(self, text, note=''):
        sep = '-' * 80
        self._logger.write(
            f'{sep}\n'
            + f'{datetime.now()} {self.component} {note}\n'
            + f'{text}\n\n'
        )
    def close(self):
        self._logger.close()


if __name__ == '__main__':
    log = Log('LogTest')
    log.append('Take Me Home, Country Roads')
    log.append('Almost heaven west virginia', 'LYRICS')
    log.append('Blue ridge mountains shenandoah river', 'LYRICS')
    log.append('Life is old there older than the trees', 'LYRICS')
    log.append('Younger than the mountains', 'LYRICS')
    log.append('Growin like a breeze', 'LYRICS')
    log.close()

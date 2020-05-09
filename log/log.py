from sys import stdout
from datetime import datetime


class Log:
    def __init__(self, component, filename=None):
        self.component = component
        self._logger = open(filename, 'a', buffering=1) if filename else stdout


    def __del__(self):
        self._logger.close()


    def append(self, text, note='', threshold=None, throw=True):
        if threshold and len(text) > threshold:
            text = f'(CONTENT TOO LONG) LENGTH: {len(text)}' \
                if throw else text[:threshold]

        line = '-' * 80 + '\n'
        info = f'{datetime.now()} {self.component} {note}\n'
        self._logger.write(f'{line}{info}{text.strip()}\n\n')


if __name__ == '__main__':
    log = Log('LogTest')
    log.append('Take Me Home, Country Roads')
    log.append('Almost heaven west virginia', 'LYRICS')
    log.append('Blue ridge mountains shenandoah river', 'LYRICS')
    log.append('Life is old there older than the trees', 'LYRICS')
    log.append('Younger than the mountains', 'LYRICS')
    log.append('Growin like a breeze', 'LYRICS')
    log.append('\r\nCountry roads\nTake me home\n', 'STRIP')
    log.append('\nTo the place\r\nI belong\r\n\r\n', 'STRIP')
    log.append('*' * 600, 'THROW', 300)
    log.append('*' * 600, 'TRIM', 300, False)

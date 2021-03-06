from sys import stdout
from datetime import datetime


class Log:
    def __init__(self, component, filename=None):
        self.component = component
        self._logger = open(filename, 'a', buffering=1) \
            if filename else stdout


    def __del__(self):
        self._logger.close()


    # Log text(string or bytes) with note(string)
    def append(self, text, note='', threshold=None, throw=True):
        textlen = len(text)
        if threshold and textlen > threshold:
            leninfo = f'LENGTH: {textlen}'
            if throw:
                text = f'(CONTENT TOO LONG) {leninfo}'
            else:
                text = f'(TRIMED | ORIGINAL {leninfo})\n{text[:threshold]}'

        line = '-' * 80 + '\n'
        info = f'{datetime.now()} {self.component} {note}\n'
        self._logger.write(f'{line}{info}{text.strip()}\n\n')


if __name__ == '__main__':
    payloads = [
        ('Take Me Home, Country Roads', ''),
        ('Almost heaven west virginia', 'LYRIC'),
        ('Blue ridge mountains shenandoah river', 'LYRIC'),
        ('Life is old there older than the trees', 'LYRIC'),
        ('Younger than the mountains', 'LYRIC'),
        ('Growin like a breeze', 'LYRIC'),
        ('\r\nCountry roads\nTake me home\n', 'STRIP'),
        ('\nTo the place\r\nI belong\r\n\r\n', 'STRIP'),
        ('x' * 100, 'TRIM', 60, False),
        ('x' * 100, 'THROW', 60),
    ]

    log = Log('LogTest')
    for argv in payloads:
        log.append(*argv)
        argv = (
            argv[0].encode('utf-8'),
            argv[1] + ' BIN',
            *tuple(list(argv[2:]))
        )
        log.append(*argv)

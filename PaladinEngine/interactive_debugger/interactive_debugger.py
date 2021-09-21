from cmd import Cmd
from typing import Callable, Iterable

from pygments import highlight
from pygments.formatters.terminal256 import TerminalTrueColorFormatter
from pygments.lexers.python import PythonLexer

from archive.archive import Archive
from source_provider import SourceProvider


class TerminalColor:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKCYAN = '\033[96m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'

    CLEAR = chr(27) + '[2J'


class InteractiveDebugger(Cmd):
    CODE_WINDOW_SIZE = 10
    FORMATTER = TerminalTrueColorFormatter(linenos=False, cssclass="source")
    LEXER = PythonLexer()

    def __init__(self, archive: Archive, error_line: str, line_no: int) -> None:
        # Call Super constructor.
        super().__init__(completekey='tab')

        # Init archive.
        self._archive = archive

        # Init line number.
        self._line_no = line_no

        # Init intro message.
        InteractiveDebugger.intro = InteractiveDebugger._intro_format(line_no, error_line,
                                                                      SourceProvider.get_line(line_no).lstrip())
        # Initiate the time of search in the archive.
        self._archive_time_of_search = archive.time

        # Initiate window size.
        self.window_size = 1

    @property
    def archive(self):
        return self._archive

    @property
    def line_no(self):
        return self._line_no

    class Keys(object):
        """
            Keys for the InteractiveDebugger.
        """
        WHY_KEY = 'why'

    @staticmethod
    def _intro_format(line_no, error_line, breaking_line):
        return f'{TerminalColor.OKBLUE}Welcome to {InteractiveDebugger.__name__}!{TerminalColor.ENDC}\n' \
               f'{TerminalColor.FAIL}{error_line}{TerminalColor.ENDC}\n' \
               f'{TerminalColor.OKBLUE}Breaking line ({line_no}): ' \
               f'{TerminalColor.OKCYAN}{breaking_line}{TerminalColor.ENDC}\n' \
               f'{TerminalColor.OKBLUE}Press {InteractiveDebugger.Keys.WHY_KEY} to figure out why.{TerminalColor.ENDC}'

    prompt = f'{TerminalColor.OKGREEN}(PaLaDiN {__name__}) >>{TerminalColor.ENDC} '

    def _create_code_window(self, expr_to_search: str):
        # Retrieve the record from the archive.

        record_values = self.archive.search(expr_to_search)

        # Get the last recorded values from time.
        record_value = record_values[0] if len(record_values) == 1 else \
            sorted(record_values, key=lambda rv: rv.time)[0]

        # Set the archive time of search to start from the time of the last value searched.
        self._archive_time_of_search = record_value.time

        # Create code window.
        code_window, bold_line_no = SourceProvider.get_window(record_value.line_no,
                                                              before=InteractiveDebugger.CODE_WINDOW_SIZE,
                                                              after=InteractiveDebugger.CODE_WINDOW_SIZE)

        return record_value.value, code_window, bold_line_no

    def do_why(self, arg):
        strings_to_print = []
        try:
            strings_to_print.append(f'{TerminalColor.OKBLUE}...{TerminalColor.ENDC}')
            # Create a code window.
            value, code_window, bold_line_no = self._create_code_window(arg)

            self.print_highlighted_code_window(code_window, bold_line_no,
                                               lambda line, no,
                                                      bold_line_no: f'{line} # >>> {arg} = {value}'
                                               if no == bold_line_no else line)
            print(f'{TerminalColor.OKBLUE}...{TerminalColor.ENDC}')

        except BaseException:
            print(f'{TerminalColor.FAIL}Can\'t find {TerminalColor.UNDERLINE}{arg}\n'
                  f'{TerminalColor.ENDC}{TerminalColor.FAIL} in archive.')

    def do_expand(self, size: int):
        try:
            self.window_size = int(size)
            code_window, bold_line_no = SourceProvider.get_window(self.line_no, self.window_size, self.window_size)
            self.print_highlighted_code_window(code_window, bold_line_no,
                                               lambda line, no, bold_line_no:
                                               f'{line} # BOLD' if no == bold_line_no else line)
        except ValueError:
            print(f'Can\'t expand, {size} is not an integer.')

    @staticmethod
    def highlight(code: str):
        return highlight(code, lexer=InteractiveDebugger.LEXER, formatter=InteractiveDebugger.FORMATTER)

    def print_highlighted_code_window(self, code_window: Iterable[str], bold_line_no: int,
                                      line_extender: Callable = lambda _: _) -> None:
        for (no, line) in enumerate(code_window):
            highlighted = InteractiveDebugger.highlight(line_extender(line, no, bold_line_no))
            print(highlighted.rstrip())

    def do_print_line(self, line_no):
        print(f'{SourceProvider.get_line(int(line_no)).strip()}')

    def postcmd(self, stop, line):
        return stop

    def do_exit(self, _):
        return True

    def help_print_line(self):
        print('Print a line from the code.')

    def help_why(self):
        print('Figure out why was a commitment broken.')


if __name__ == '__main__':
    archive = Archive()
    InteractiveDebugger(archive, '', 0).cmdloop()

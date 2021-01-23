from cmd import Cmd

from archive import archive
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
    def __init__(self, archive: archive.Archive, error_line: str, line_no: int) -> None:
        # Call Super constructor.
        super().__init__(completekey='tab')

        # Init archive.
        self._archive = archive

        # Init line number.
        self._line_no = line_no

        # Init intro message.
        InteractiveDebugger.intro = InteractiveDebugger._intro_format(line_no, error_line,
                                                                      SourceProvider.get_line(line_no).lstrip())

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

    def do_why(self, arg):
        print(f'{TerminalColor.OKBLUE}...{TerminalColor.ENDC}')
        line_nos = []
        # Search for arg in the archive.
        #for value, line_no in ((self.archive.retrieve(arg)[::-1])[0]):
            # if line_no in line_nos:
            #     continue
            # line_nos.append(line_no)
            # Fetch a code_window.
        all_values_of_arg = reversed(self.archive.retrieve(arg))
        value, line_no = all_values_of_arg.__next__()
        code_window, bold_line_no = SourceProvider.get_window(line_no, before=10, after=10)
        for line, no in zip(code_window, range(1, len(code_window))):
            if no == bold_line_no:
                print(f'{TerminalColor.OKBLUE}{line} {TerminalColor.OKCYAN}>>> {arg} = {str(value)}{TerminalColor.ENDC}')
            else:
                print(line)
        print(f'{TerminalColor.OKBLUE}...{TerminalColor.ENDC}')

    def do_print_line(self, line_no):
        print(f'{SourceProvider.get_line(int(line_no)).strip()}')

    def help_print_line(self):
        print('Print a line from the code.')

    def help_why(self):
        print('Figure out why was a commitment broken.')


if __name__ == '__main__':
    InteractiveDebugger().cmdloop()

class SourceProvider(object):
    _source_code = ''

    @staticmethod
    def set_code(code):
        SourceProvider._source_code = [''] + code.split('\n')

    @staticmethod
    def get_line(line_no):
        return SourceProvider._source_code[line_no]

    @staticmethod
    def first_line_no():
        return 1

    @staticmethod
    def last_line_no():
        return len(SourceProvider._source_code)

    @staticmethod
    def get_window(line_no, before, after):
        # Calculate the first line of the window.
        if line_no - before < 0:
            first_line = SourceProvider.first_line_no()
        else:
            first_line = line_no - before

        # Calculate the last line of the window.
        if line_no + after > SourceProvider.last_line_no():
            last_line = SourceProvider.last_line_no()
        else:
            last_line = line_no + after

        # Calculate the index of line_no in the window.
        line_no_in_window = before

        # Return the window.
        return SourceProvider._source_code[first_line: last_line], line_no_in_window + 1

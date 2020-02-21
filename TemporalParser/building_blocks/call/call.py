from TemporalParser.building_blocks.abstract.collectible import Collectible


class Call(Collectible):
    def __init__(self, *args):
        super().__init__()
        self.__inner_call = None

    def collect(self, stack: list):
        self.__inner_call = stack.pop()
        return stack


class FuncCall(Collectible):
    PARAMS_SEPARATOR = ','
    OPEN_BRACE = '('

    def __init__(self, *args):
        super().__init__()
        self.__name = args[0][1]
        self.__params = args[2][1]

    @property
    def func_name(self):
        return self.__name

    @func_name.setter
    def func_name(self, value):
        self.__name = value

    @property
    def params(self):
        return self.__params

    @params.setter
    def params(self, value):
        import copy
        copy.deepcopy()
        self.__params = value

    def collect(self, stack: list):
        # Pop closing brace.
        stack.pop()

        # Find open-brace index.
        open_brace_index = stack.index(FuncCall.OPEN_BRACE)

        # Extract params.
        params = stack.reverse()[0:open_brace_index]

        # Remove commas (if more than one param).
        if FuncCall.PARAMS_SEPARATOR in params:
            params.remove(FuncCall.PARAMS_SEPARATOR)

        # Pop params.
        stack = stack[open_brace_index:]

        # Pop open-brace.
        stack.pop()

        # Pop func name.
        self.func_name = stack.pop()

        return stack


class MethodCall(FuncCall):
    def __init__(self, *args):
        super().__init__(*MethodCall.extract_func_call(args))
        self.__target = args[0][1]

    @staticmethod
    def extract_func_call(args):
        """
            Extract call from MethodCall's args.
        :param args:
        :return:
        """
        # Extract func call args.
        func_call_args = args[2]

        # Remove rule.
        return func_call_args[1::]

    @property
    def target(self):
        return self.__target

    @target.setter
    def target(self, value):
        self.__target = value

class Paladin(object):
    @staticmethod
    def precond(func, *args, **kwargs):
        pass

    @staticmethod
    def postcond(func, *args, **kwargs):
        pass


def Paladinize(cls):
    pass

def PaladinPostCondition(condition):
    def decorator(func):
        return func
    return decorator

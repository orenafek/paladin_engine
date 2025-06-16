from stubs.stubs import archive


class Paladin(object):
    @staticmethod
    def precond(func, *args, **kwargs):
        pass

    @staticmethod
    def postcond(func, *args, **kwargs):
        pass

    @classmethod
    def pause_record(cls):
        archive.pause_record()

    @classmethod
    def resume_record(cls):
        archive.resume_record()

    @staticmethod
    def atomic(func):
        return func

def Paladinize(cls):
    pass

def PaladinPostCondition(condition):
    def decorator(func):
        return func
    return decorator

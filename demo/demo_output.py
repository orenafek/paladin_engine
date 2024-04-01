from stubs.stubs import __AC__, __ARG__, __AS__, __BMFCS__, __BREAK__, __DEF__, __EOLI__, __FC__, __FLI__, __FRAME__, __IS_STUBBED__, __PAUSE__, __PIS__, __PRINT__, __RESUME__, __SOL__, __SOLI__, __UNDEF__


import random
from abc import abstractmethod
from enum import Enum
from random import shuffle, choice
from typing import Optional

class Job(object):

    class Type(Enum):
        TEXT = 0
        __AS__('TEXT = 0', 'TEXT', locals=locals(), globals=globals(), frame=__FRAME__(), line_no=10)
        IMAGE = 1
        __AS__('IMAGE = 1', 'IMAGE', locals=locals(), globals=globals(), frame=__FRAME__(), line_no=11)
        AUDIO = 2
        __AS__('AUDIO = 2', 'AUDIO', locals=locals(), globals=globals(), frame=__FRAME__(), line_no=12)
        VIDEO = 3
        __AS__('VIDEO = 3', 'VIDEO', locals=locals(), globals=globals(), frame=__FRAME__(), line_no=13)

    def __init__(self, id: int, _type):
        __DEF__('__init__', line_no=15, frame=__FRAME__())
        __PIS__(self, 'self', line_no=15)
        __ARG__('__init__', __FRAME__(), 15, self=self, id=id, _type=_type)
        self.id = id
        __AS__('self.id = id', 'self.id', locals=locals(), globals=globals(), frame=__FRAME__(), line_no=16)
        self.type = _type._name_
        __AS__('self.type = _type._name_', 'self.type', locals=locals(), globals=globals(), frame=__FRAME__(), line_no=17)
        __UNDEF__('__init__', __FRAME__(), 17)
        return None

class Server(object):

    def __init__(self):
        __DEF__('Server.__init__', line_no=21, frame=__FRAME__())
        __ARG__('Server.__init__', __FRAME__(), 21, self=self)
        self.todo = []
        __AS__('self.todo = []', 'self.todo', locals=locals(), globals=globals(), frame=__FRAME__(), line_no=22)
        self.summaries = []
        __AS__('self.summaries = []', 'self.summaries', locals=locals(), globals=globals(), frame=__FRAME__(), line_no=23)
        __UNDEF__('Server.__init__', __FRAME__(), 23)
        return None

class Worker(object):

    def __init__(self, server: Server):
        __DEF__('Worker.__init__', line_no=27, frame=__FRAME__())
        __ARG__('Worker.__init__', __FRAME__(), 27, self=self, server=server)
        self.server = server
        __AS__('self.server = server', 'self.server', locals=locals(), globals=globals(), frame=__FRAME__(), line_no=28)
        self.ongoing: Optional[Job] = None
        __AS__('self.ongoing: Optional[Job] = None', 'self.ongoing', locals=locals(), globals=globals(), frame=__FRAME__(), line_no=29)
        __UNDEF__('Worker.__init__', __FRAME__(), 29)
        return None

    def consume(self):
        __DEF__('Worker.consume', line_no=31, frame=__FRAME__())
        __ARG__('Worker.consume', __FRAME__(), 31, self=self)
        if not self.server.todo:
            __UNDEF__('Worker.consume', __FRAME__(), 33)
            return
        self.ongoing: Job = __BMFCS__(__FC__('self.server.todo.pop()', self.server.todo.pop, locals(), globals(), __FRAME__(), 34), self.server.todo, 'self.server.todo', 'pop', 34, __FRAME__(), locals(), globals())
        __AS__('self.ongoing: Job = __BMFCS__(__FC__(@self.server.todo.pop()@, self.server.todo.pop, locals(), globals(), __FRAME__(), 34), self.server.todo, @self.server.todo@, @pop@, 34, __FRAME__(), locals(), globals())', 'self.ongoing', locals=locals(), globals=globals(), frame=__FRAME__(), line_no=34)
        __FC__('self.operate()', self.operate, locals(), globals(), __FRAME__(), 35)
        self.ongoing = None
        __AS__('self.ongoing = None', 'self.ongoing', locals=locals(), globals=globals(), frame=__FRAME__(), line_no=36)
        __UNDEF__('Worker.consume', __FRAME__(), 36)
        return None

    @abstractmethod
    def operate(self) -> None:
        __DEF__('Worker.operate', line_no=39, frame=__FRAME__())
        __ARG__('Worker.operate', __FRAME__(), 39, self=self)
        raise __FC__('NotImplementedError()', NotImplementedError, locals(), globals(), __FRAME__(), 40)
        __UNDEF__('Worker.operate', __FRAME__(), 40)
        return None

class TimelessWorker(Worker):

    def operate(self) -> None:
        __DEF__('TimelessWorker.operate', line_no=45, frame=__FRAME__())
        __ARG__('TimelessWorker.operate', __FRAME__(), 45, self=self)
        match Job.Type[self.ongoing.type]:
            case Job.Type.IMAGE | Job.Type.TEXT:
                __BMFCS__(__FC__('self.server.summaries.append(self.ongoing)', self.server.summaries.append, locals(), globals(), __FRAME__(), 48, self.ongoing), self.server.summaries, 'self.server.summaries', 'append', 48, __FRAME__(), locals(), globals(), self.ongoing)
            case Job.Type.AUDIO | Job.Type.VIDEO:
                __BMFCS__(__FC__('self.server.todo.append(self.ongoing)', self.server.todo.append, locals(), globals(), __FRAME__(), 50, self.ongoing), self.server.todo, 'self.server.todo', 'append', 50, __FRAME__(), locals(), globals(), self.ongoing)
        __UNDEF__('TimelessWorker.operate', __FRAME__(), 50)
        return None

class PlayableWorker(Worker):

    def operate(self) -> None:
        __DEF__('PlayableWorker.operate', line_no=55, frame=__FRAME__())
        __ARG__('PlayableWorker.operate', __FRAME__(), 55, self=self)
        match Job.Type[self.ongoing.type]:
            case Job.Type.AUDIO | Job.Type.VIDEO:
                __BMFCS__(__FC__('self.server.summaries.append(self.ongoing)', self.server.summaries.append, locals(), globals(), __FRAME__(), 58, self.ongoing), self.server.summaries, 'self.server.summaries', 'append', 58, __FRAME__(), locals(), globals(), self.ongoing)
            case Job.Type.IMAGE | Job.Type.TEXT:
                __BMFCS__(__FC__('self.server.todo.append(self.ongoing)', self.server.todo.append, locals(), globals(), __FRAME__(), 60, self.ongoing), self.server.todo, 'self.server.todo', 'append', 60, __FRAME__(), locals(), globals(), self.ongoing)
        __UNDEF__('PlayableWorker.operate', __FRAME__(), 60)
        return None

class VisualWorker(Worker):

    def operate(self) -> None:
        __DEF__('VisualWorker.operate', line_no=65, frame=__FRAME__())
        __ARG__('VisualWorker.operate', __FRAME__(), 65, self=self)
        match Job.Type[self.ongoing.type]:
            case Job.Type.IMAGE | Job.Type.VIDEO:
                __BMFCS__(__FC__('self.server.summaries.append(self.ongoing)', self.server.summaries.append, locals(), globals(), __FRAME__(), 68, self.ongoing), self.server.summaries, 'self.server.summaries', 'append', 68, __FRAME__(), locals(), globals(), self.ongoing)
            case Job.Type.TEXT:
                __BMFCS__(__FC__('self.server.todo.append(self.ongoing)', self.server.todo.append, locals(), globals(), __FRAME__(), 70, self.ongoing), self.server.todo, 'self.server.todo', 'append', 70, __FRAME__(), locals(), globals(), self.ongoing)
        __UNDEF__('VisualWorker.operate', __FRAME__(), 70)
        return None

class AllTypesWorker(Worker):

    def operate(self) -> None:
        __DEF__('AllTypesWorker.operate', line_no=75, frame=__FRAME__())
        __ARG__('AllTypesWorker.operate', __FRAME__(), 75, self=self)
        __BMFCS__(__FC__('self.server.summaries.append(self.ongoing)', self.server.summaries.append, locals(), globals(), __FRAME__(), 76, self.ongoing), self.server.summaries, 'self.server.summaries', 'append', 76, __FRAME__(), locals(), globals(), self.ongoing)
        __UNDEF__('AllTypesWorker.operate', __FRAME__(), 76)
        return None

def main():
    __DEF__('main', line_no=79, frame=__FRAME__())
    __ARG__('main', __FRAME__(), 79)
    __FC__('random.seed(2023)', random.seed, locals(), globals(), __FRAME__(), 80, 2023)
    server = __FC__('Server()', Server, locals(), globals(), __FRAME__(), 81)
    __AS__('server = __FC__(@Server()@, Server, locals(), globals(), __FRAME__(), 81)', 'server', locals=locals(), globals=globals(), frame=__FRAME__(), line_no=81)
    workers = [__FC__('worker_type(server)', worker_type, locals(), globals(), __FRAME__(), 82, server) for worker_type in __FC__('Worker.__subclasses__()', Worker.__subclasses__, locals(), globals(), __FRAME__(), 82)]
    __AS__('workers = [__FC__(@worker_type(server)@, worker_type, locals(), globals(), __FRAME__(), 82, server) for worker_type in __FC__(@Worker.__subclasses__()@, Worker.__subclasses__, locals(), globals(), __FRAME__(), 82)]', 'workers', locals=locals(), globals=globals(), frame=__FRAME__(), line_no=82)
    jobs = [__FC__("Job(i, choice(__FC__('list(Job.Type)', list, locals(), globals(), __FRAME__(), 83, Job.Type)))", Job, locals(), globals(), __FRAME__(), 83, i, choice(__FC__('list(Job.Type)', list, locals(), globals(), __FRAME__(), 83, Job.Type))) for i in __FC__('range(20)', range, locals(), globals(), __FRAME__(), 83, 20)]
    __AS__('jobs = [__FC__(@Job(i, choice(__FC__(@list(Job.Type)@, list, locals(), globals(), __FRAME__(), 83, Job.Type)))@, Job, locals(), globals(), __FRAME__(), 83, i, choice(__FC__(@list(Job.Type)@, list, locals(), globals(), __FRAME__(), 83, Job.Type))) for i in __FC__(@range(20)@, range, locals(), globals(), __FRAME__(), 83, 20)]', 'jobs', locals=locals(), globals=globals(), frame=__FRAME__(), line_no=83)
    __FC__('shuffle(jobs)', shuffle, locals(), globals(), __FRAME__(), 84, jobs)
    server.todo = __FC__('jobs.copy()', jobs.copy, locals(), globals(), __FRAME__(), 85)
    __AS__('server.todo = __FC__(@jobs.copy()@, jobs.copy, locals(), globals(), __FRAME__(), 85)', 'server.todo', locals=locals(), globals=globals(), frame=__FRAME__(), line_no=85)
    __SOL__(__FRAME__(), 87)
    while server.todo:
        __SOLI__(87, __FRAME__())
        __FC__('shuffle(workers)', shuffle, locals(), globals(), __FRAME__(), 88, workers)
        __SOL__(__FRAME__(), 89)
        for __iter_0 in workers:
            __SOLI__(89, __FRAME__())
            worker = __iter_0
            __AS__('worker = __iter_0', 'worker', locals=locals(), globals=globals(), frame=__FRAME__(), line_no=89)
            __FC__('worker.consume()', worker.consume, locals(), globals(), __FRAME__(), 90)
            __EOLI__(__FRAME__(), loop_start_line_no=89, loop_end_line_no=90)
        __EOLI__(__FRAME__(), loop_start_line_no=87, loop_end_line_no=90)
    if __FC__('len(jobs)', len, locals(), globals(), __FRAME__(), 92, jobs) != __FC__('len(server.summaries)', len, locals(), globals(), __FRAME__(), 92, server.summaries):
        raise __FC__("AssertionError('Mismatch between no. of summaries and jobs.')", AssertionError, locals(), globals(), __FRAME__(), 93, 'Mismatch between no. of summaries and jobs.')
    __UNDEF__('main', __FRAME__(), 93)
    return None
if __name__ == '__main__':
    __FC__('main()', main, locals(), globals(), __FRAME__(), 97)
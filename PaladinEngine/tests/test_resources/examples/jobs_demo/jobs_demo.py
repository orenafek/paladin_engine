import random
from abc import abstractmethod
from enum import Enum
from random import shuffle, choice
from typing import Optional


class Job(object):
    class Type(Enum):
        TEXT = 0
        IMAGE = 1
        AUDIO = 2
        VIDEO = 3

    def __init__(self, id: int, _type):
        self.id = id
        self.type = _type._name_


class Server(object):
    def __init__(self):
        self.todo = []
        self.summaries = []


class Worker(object):
    def __init__(self, server: Server):
        self.server = server
        self.ongoing: Optional[Job] = None

    def consume(self):
        if not self.server.todo:
            return
        self.ongoing: Job = self.server.todo.pop()
        self.operate()
        self.ongoing = None

    @abstractmethod
    def operate(self) -> None:
        raise NotImplementedError()


class TimelessWorker(Worker):

    def operate(self) -> None:
        match Job.Type[self.ongoing.type]:
            case Job.Type.IMAGE | Job.Type.TEXT:
                self.server.summaries.append(self.ongoing)
            case Job.Type.AUDIO | Job.Type.VIDEO:
                self.server.todo.append(self.ongoing)


class PlayableWorker(Worker):

    def operate(self) -> None:
        match Job.Type[self.ongoing.type]:
            case Job.Type.AUDIO | Job.Type.VIDEO:
                self.server.summaries.append(self.ongoing)
            case Job.Type.IMAGE | Job.Type.TEXT:
                self.server.todo.append(self.ongoing)


class VisualWorker(Worker):

    def operate(self) -> None:
        match Job.Type[self.ongoing.type]:
            case Job.Type.IMAGE | Job.Type.VIDEO:
                self.server.summaries.append(self.ongoing)
            case Job.Type.TEXT:
                self.server.todo.append(self.ongoing)


class EvenWorker(Worker):

    def __init__(self, server: Server):
        super(EvenWorker, self).__init__(server)
        self.counter = 0

    def operate(self) -> None:
        if self.counter % 2 == 0:
            self.server.summaries.append(self.ongoing)
        else:
            self.server.todo.append(self.ongoing)

        self.counter += 1


class OddWorker(Worker):

    def __init__(self, server: Server):
        super(OddWorker, self).__init__(server)
        self.counter = 0

    def operate(self) -> None:
        if self.counter % 2 == 1:
            self.server.summaries.append(self.ongoing)
        else:
            self.server.todo.append(self.ongoing)

        self.counter += 1


class AllTypesWorker(Worker):

    def operate(self) -> None:
        self.server.summaries.append(self.ongoing)


def main():
    random.seed(2023)
    server = Server()
    workers = [worker_type(server) for worker_type in Worker.__subclasses__()]
    jobs = [Job(i, choice(list(Job.Type))) for i in range(20)]
    shuffle(jobs)
    server.todo = jobs.copy()

    while server.todo:
        shuffle(workers)
        for worker in workers:
            worker.consume()

    if len(jobs) != len(server.summaries):
        raise AssertionError('Mismatch between no. of summaries and jobs.')


if __name__ == '__main__':
    main()

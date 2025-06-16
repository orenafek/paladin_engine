from abc import abstractmethod
from random import shuffle
from typing import Any, Optional

Job = Any
Summary = str


class Server(object):
    def __init__(self):
        self.todo = []
        self.summaries = []


class Worker(object):
    _ID = 0

    def __init__(self, server: Server):
        self.id = Worker._generate_id()
        self.server = server
        self.ongoing: Optional[Job] = None

    def consume(self):
        if not self.server.todo:
            return
        consumed_job: Job = self.server.todo.pop()
        self.ongoing = consumed_job
        self.operate(consumed_job)
        self.ongoing = None

    @classmethod
    def _generate_id(cls):
        Worker._ID += 1
        return Worker._ID

    @abstractmethod
    def operate(self, job: Job) -> None:
        raise NotImplementedError()


class WorkerOnlyEven(Worker):

    def operate(self, job: Job) -> None:
        if job % 2 == 0:
            self.server.summaries.append(job)


class WorkerOnlyPositive(Worker):

    def operate(self, job: Job) -> None:
        if job > 0:
            self.server.summaries.append(job)
        else:
            self.server.todo.append(job)


class WorkerAllInputs(Worker):

    def operate(self, job: Job) -> None:
        self.server.summaries.append(job)


def main():
    server = Server()
    workers = [WorkerOnlyEven(server), WorkerOnlyPositive(server), WorkerAllInputs(server)]
    jobs = list(range(20))
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

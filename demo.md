# Demo

## Script

### Description of Example Program

Hi, I’ve written a program in which there is a server that handles jobs from clients. The jobs can be of one of the four
types(text, image, audio and video).
There is a variety of workers which inherit from an abstract Worker type. Each worker is able to operate
On some (or all) of job types.
For each job in the server’s todo list, a worker, in its turn, takes a job and operates on it. if its able, is pushes a
summary for that job, and if not it pushes the job back to the server.
At the end the server verifies that there are as many summaries as there were jobs at the beginning.
Now when running the program. I can see that it failed due in that verify.
Let’s use Paladin to debug it.

## The Program

```python

import random
from abc import abstractmethod
from enum import Enum
from random import shuffle, choice, randbytes
from typing import Optional

Summary = str


class Job(object):
    class Type(Enum):
        TEXT = 0
        IMAGE = 1
        AUDIO = 2
        VIDEO = 3

    def __init__(self, job_id: int, _type: 'Job.Type', data: bytes):
        self.job_id = job_id
        self.type = _type._name_
        self.data = data


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
        self.ongoing: Job = self.server.todo.pop()
        self.operate()
        self.ongoing = None

    @classmethod
    def _generate_id(cls):
        Worker._ID += 1
        return Worker._ID

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


class AllTypesWorker(Worker):

    def operate(self) -> None:
        self.server.summaries.append(self.ongoing)


def main():
    random.seed(2023)
    server = Server()
    workers = [worker_type(server) for worker_type in Worker.__subclasses__()]
    jobs = [Job(i, choice(list(Job.Type)), randbytes(5)) for i in range(20)]
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

```

### The Debug-process

1. Observe the risen assertion error.
2. In order to see the two predicate's operator, run: `Union(len(server.summaries), len(jobs))`
3. The length differ due to missing summaries, to find the jobs that have no summaries,
   run: `set(jobs) - set(server.summaries)`
4. After reading the code and, one can understand that the normal lifetime of a job, is going through
   `jobs -> server.todo -> <Some worker>.ongonig -> <In Worker::operate>> -> server.summaries`.
   Each In order to see when was the first time that this lifetime has been broken for any of the jobs,
   run: `set(jobs) - (set(server.summaries + server.todo + [w.ongoing for w in workers]))`
5. The first time an object has appeared in this state and never disappeared (is in `server.summaries`), is the time
   that the job was mishandled in `Worker::operate`. Click on This time range to focus PaLaDiN on this time range.
6. To find which Worker has mishandled the job, find the type of the `self` variable in the specific time range. To do
   so run: `Where(Type(self), InFunction("operate"))`.
7. The result focuses on `VisualWorker`, in which in its `operate` function, an `Audio` typed job is neither handled nor
   being returned to the `todo` list: 
   ```python
   80:      case Job.Type.TEXT:
                self.server.todo.append(self.ongoing)
   ```


from abc import ABC
import math
from typing import List, Optional
from process import Process
import numpy as np


class Queue(ABC):
    def __init__(self, name: str) -> None:
        self._name = name
        self._queue: List[Process] = []
        self._queue_length_history = []
        self._quantum = None

    @staticmethod
    def policy(process: Process, clock) -> float:
        return process.get_arrival_time()

    def get_quantum(self):
        if self._quantum:
            return self._quantum
        return math.inf

    def get_next_process(self, clock: Optional[int] = None, k: Optional[int] = None):
        k = k or 1
        k = min(k, len(self._queue))

        sorted_queue = sorted(
            self._queue,
            key=lambda p: self.policy(p, clock),
        )

        return sorted_queue[:k]

    def is_empty(self):
        return len(self._queue) == 0

    def add(self, process: Process):
        self._queue.append(process)

    def delete(self, process: Process):
        self._queue.remove(process)

    def len(self):
        return len(self._queue)

    def record_queue_length(self):
        self._queue_length_history.append(len(self._queue))

    def get_mean_queue_len(self):
        return np.mean(self._queue_length_history)

    def __str__(self) -> str:
        return self._name


class PriorityQueue(Queue):
    @staticmethod
    def policy(process: Process, clock: int):
        waiting_time = process.calculate_waiting_time(clock)
        return -(process._priority.value[0] + 0.1 * waiting_time)


class Fifo(Queue):
    pass


class RoundRobin(Queue):
    def __init__(self, quantum: int, name: str) -> None:
        super().__init__(name)
        self._quantum = quantum

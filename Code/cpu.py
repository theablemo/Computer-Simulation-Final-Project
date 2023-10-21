from process import Process
from typing import Optional

from queues import Queue


class Cpu:
    def __init__(self) -> None:
        self._current_process: Optional[Process] = None
        self._remaining_time: Optional[int] = None
        self._next_queue: Optional[Queue] = None
        self._idle_time = 0

    def add_idle_time(self):
        self._idle_time += 1

    def is_busy(self):
        if not self._current_process:
            return False
        return True

    def serve(self, clock):
        self._current_process.get_service(clock)
        self._remaining_time -= 1

        if self._current_process.is_process_finished() or self._remaining_time == 0:
            if not self._current_process.is_process_finished():
                self._next_queue.add(self._current_process)
                self._current_process._change_queue(self._next_queue, clock)
            else:
                self._current_process.finish_process(clock + 1)
            self._current_process = None
            self._remaining_time = None
            self._next_queue = None

    def assign_process(self, process: Process, service_time: int, next_queue: Queue):
        self._current_process = process
        self._remaining_time = service_time
        self._next_queue = next_queue

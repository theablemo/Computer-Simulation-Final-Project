from typing import Optional
from priority import Priority


class Process:
    def __init__(
        self,
        interarrival_time: int,
        arrival_time: int,
        service_time: int,
        timeout_time: int,
        priority: Priority,
        name: str,
    ) -> None:
        self._name = name
        self._interarrival_time = interarrival_time
        self._arrival_time = arrival_time
        self._service_time = service_time
        self._timeout_time = timeout_time
        self._priority = priority
        self._served_times = []
        self._waiting_time = 0

        self._is_finished_successfully = False
        self._current_queue = None
        self._is_timeouted = False

        self._served_time: int = 0

        self._finished_time: Optional[int] = None

    @property
    def remaining_service_time(self):
        return self._service_time - self._served_time

    def is_process_finished(self):
        return self._served_time == self._service_time or self._is_timeouted

    def get_service(
        self,
        clock,
        duration=1,
    ):
        self._served_time += duration
        self._add_serve_time(clock)

    def _add_serve_time(self, clock):
        self._served_times.append(clock)

    def calculate_waiting_time(self, clock) -> int:
        finished_time = self._finished_time if self._finished_time else clock
        return (finished_time - self._arrival_time) - self._served_time

    def finish_process(self, clock):
        self._finished_time = clock
        self._is_finished_successfully = True

    def get_arrival_time(self):
        return self._arrival_time

    def timeout_process(self, clock):
        self.finish_process(clock)
        self._is_timeouted = True
        self._is_finished_successfully = False

    def _change_queue(self, queue, clock):
        self._current_queue = queue

    def __str__(self) -> str:
        return self._name

    def to_dict(self):
        return {
            "Priority": self._priority,
            "Interarrival Time": self._interarrival_time,
            "Arrival Time": self._arrival_time,
            "Service Time": self._service_time,
            "Waiting Time": self._waiting_time,
            "Served Time": self._served_time,
            "Finished Time": self._finished_time,
            "Remaining Service Time": self.remaining_service_time,
            "Finished Successfully": self._is_finished_successfully,
            "Timeout": self._timeout_time,
            "Timouted?": self._is_timeouted
        }

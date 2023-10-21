from typing import List
from cpu import Cpu
from priority import Priority
from queues import Fifo, PriorityQueue, Queue, RoundRobin
from process import Process

from random import expovariate, seed
from numpy.random import choice
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt


class CpuSimulation:
    INSERT_TO_SECOND_LEVEL_INTERVAL = 10
    INSERT_TO_SECOND_LEVEL_COUNT = 3
    FIRST_QUANTUM = 2
    SECOND_QUANTUM = 10

    USE_RANDOMNESS = False

    def __init__(
        self,
        simulation_time,
        process_counts,
        interarrival_rate,
        service_time_mean,
        timeout_mean,
    ) -> None:
        self._simulation_time = simulation_time
        self._process_counts = process_counts
        self._interarrival_rate = interarrival_rate
        self._service_time_rate = 1 / service_time_mean
        self._timeout_rate = 1 / timeout_mean

        self._generated_processes: List[Process] = []
        self._clock = 0

        self._priority_queue = PriorityQueue("Priority Queue")
        self._first_round_robin = RoundRobin(
            self.FIRST_QUANTUM, "RoundRobin T1")
        self._second_round_robin = RoundRobin(
            self.SECOND_QUANTUM, "RoundRobin T2")
        self._fifo = Fifo("FCFS")

        self._second_level_queues: List[Queue] = [
            self._first_round_robin,
            self._second_round_robin,
            self._fifo,
        ]

        self._cpu = Cpu()

    def _initialize(self):
        self._generated_processes: List[Process] = []
        self._clock = 0
        self._priority_queue = PriorityQueue("Priority Queue")
        self._first_round_robin = RoundRobin(
            self.FIRST_QUANTUM, "RoundRobin T1")
        self._second_round_robin = RoundRobin(
            self.SECOND_QUANTUM, "RoundRobin T2")
        self._fifo = Fifo("FCFS")

        self._second_level_queues: List[Queue] = [
            self._first_round_robin,
            self._second_round_robin,
            self._fifo,
        ]

        self._cpu = Cpu()

        self._generate_processes()
        self.processes = self._generated_processes[:]

    def _advance_time(self):
        self._clock += 1

    def _generate_processes(self):
        pervious_arrival_time = 0
        for i in range(self._process_counts):
            interarrival_time = (
                int(expovariate(self._interarrival_rate)) if i != 0 else 0
            )
            arrival_time = pervious_arrival_time + interarrival_time
            if arrival_time > self._simulation_time:
                self._process_counts = i
                break
            service_time = int(expovariate(self._service_time_rate))
            while service_time == 0:
                service_time = int(expovariate(self._service_time_rate))
            timeout_time = int(expovariate(self._timeout_rate))
            while timeout_time == 0:
                timeout_time = int(expovariate(self._timeout_rate))

            priority = Priority.get_sample_priority()

            self._generated_processes.append(
                Process(
                    name=str(i),
                    interarrival_time=interarrival_time,
                    arrival_time=arrival_time,
                    service_time=service_time,
                    timeout_time=timeout_time,
                    priority=priority,
                )
            )

            pervious_arrival_time = arrival_time

    def _add_arrived_processes_to_priority_queue(self):
        arrived_processes: List[Process] = []
        for process in self._generated_processes:
            if process._arrival_time <= self._clock:
                arrived_processes.append(process)

        for process in arrived_processes:
            self._generated_processes.remove(process)
            self._priority_queue.add(process)
            process._change_queue(self._priority_queue, self._clock)

    def _should_insert_processes_to_second_level_queue(self):
        second_level_processes_count = (
            self._first_round_robin.len()
            + self._second_round_robin.len()
            + self._fifo.len()
        )
        return (
            self._clock % self.INSERT_TO_SECOND_LEVEL_INTERVAL == 0
            and second_level_processes_count < self.INSERT_TO_SECOND_LEVEL_COUNT
        )

    def _add_processes_from_priority_to_first_round_robin(self):
        moved_processes = self._priority_queue.get_next_process(
            clock=self._clock, k=self.INSERT_TO_SECOND_LEVEL_COUNT
        )

        for process in moved_processes:
            self._priority_queue.delete(process)
            self._first_round_robin.add(process)
            process._change_queue(self._first_round_robin, self._clock)

    def _get_next_queue_from_current(self, current_queue):
        if current_queue == self._first_round_robin:
            return self._second_round_robin

        if current_queue == self._second_round_robin:
            return self._fifo

        return self._fifo

    def _dispatch(self):
        queues_probablities: List[float] = [0.8, 0.1, 0.1]
        queue = choice(self._second_level_queues, 1, p=queues_probablities)[0]

        if self.USE_RANDOMNESS and queue.len():
            process: Process = queue.get_next_process()[0]
            queue.delete(process)
            return process, queue

        else:
            for queue in self._second_level_queues:
                if queue.len():
                    process: Process = queue.get_next_process()[0]
                    queue.delete(process)
                    return process, queue

        return None, None

    def _collect_statistics(self):
        for queue in [self._priority_queue, *self._second_level_queues]:
            queue.record_queue_length()

    def _get_runtime(self):
        return max(process._finished_time for process in self.processes)

    def _all_waiting_times(self):
        for process in self.processes:
            process._waiting_time = process.calculate_waiting_time(self._clock)

    def _check_timouts(self):
        for process in self.processes:
            if (
                process.calculate_waiting_time(
                    self._clock) > process._timeout_time
                and not process.is_process_finished()
            ):
                process._current_queue.delete(process)
                process.timeout_process(self._clock)

    def _show_reports(self):
        pd.set_option('display.max_rows', 50)
        pd.set_option('display.max_columns', 100)
        pd.set_option('display.width', 1000)
        table = pd.DataFrame.from_records(
            [p.to_dict() for p in self.processes])
        print(table)
        print("********")

        print(f"T1 = {self.FIRST_QUANTUM}, T2 = {self.SECOND_QUANTUM}")
        print("1. Mean queue lengths:")
        for queue in [self._priority_queue, *self._second_level_queues]:
            print(queue, queue.get_mean_queue_len())

        waiting_times = list(table["Waiting Time"])
        mean_waiting_time = np.mean(waiting_times)

        print(
            f"3. Utilization: {(1- (self._cpu._idle_time/self._simulation_time) )*100}%"
        )

        timeouted_processes = len(
            list(filter(lambda x: x._is_timeouted, self.processes))
        )
        print(
            f"5. Percentage of timeouted processes: {100 * timeouted_processes / len(self.processes)}%"
        )

        print("2. Waiting Times:\n[PLOT SHOW]")
        plt.xlabel("Process")
        plt.ylabel("Waiting time")
        plt.scatter(
            range(0, self._process_counts),
            list(table["Waiting Time"]),
            c="blue",
            label="waiting time per process",
        )
        plt.plot(
            range(0, self._process_counts),
            list(table["Waiting Time"]),
            "green",
            label="waiting time per process",
        )
        plt.plot(
            range(0, self._process_counts),
            [mean_waiting_time] * self._process_counts,
            "-r",
            label="mean waiting time",
        )
        print(f"Mean Waiting Time for all processes: {mean_waiting_time}")

        plt.legend()
        plt.show()

    def simulate(self):
        seed(100)
        self._initialize()

        while self._clock < self._simulation_time:
            self._add_arrived_processes_to_priority_queue()

            if self._should_insert_processes_to_second_level_queue():
                self._add_processes_from_priority_to_first_round_robin()

            if self._cpu.is_busy():
                self._cpu.serve(self._clock)
            else:
                next_process, queue = self._dispatch()
                if next_process:
                    next_process._change_queue(None, self._clock)

                    service_time = min(
                        next_process.remaining_service_time, queue.get_quantum()
                    )
                    next_queue = self._get_next_queue_from_current(queue)
                    self._cpu.assign_process(
                        next_process, service_time, next_queue)

                    self._cpu.serve(self._clock)
                else:
                    self._cpu.add_idle_time()

            self._collect_statistics()
            self._check_timouts()
            self._advance_time()

        self._all_waiting_times()

        self._show_reports()
        return self.processes, self._simulation_time, self._cpu

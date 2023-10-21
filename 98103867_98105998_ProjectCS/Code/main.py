from enum import Enum
import pandas as pd
from cpu_simulation import CpuSimulation


class InputMethod(Enum):
    CLI = 1
    FILE = 2


def get_inputs():
    with open("input.txt") as file:
        lines = [line.rstrip() for line in file]
    print("How do you want to read inputs?\n1. CLI\n2. File")
    method = int(input())
    INPUT_METHOD = InputMethod.CLI if method == 1 else InputMethod.FILE
    if INPUT_METHOD == INPUT_METHOD.CLI:
        print("Simulation time:", end=" ")
        simulation_time = int(input())

        print("Process counts:", end=" ")
        process_counts = int(input())

        print("Interarrival rate(X):", end=" ")
        interarrival_rate = float(input())

        print("Service time mean(Y):", end=" ")
        service_time_mean = float(input())

        print("Timeout mean(Z):", end=" ")
        timeout_mean = float(input())
    else:
        simulation_time = int(lines[0])
        process_counts = int(lines[1])
        interarrival_rate = float(lines[2])
        service_time_mean = float(lines[3])
        timeout_mean = float(lines[4])

    simulation = CpuSimulation(
        simulation_time,
        process_counts,
        interarrival_rate,
        service_time_mean,
        timeout_mean,
    )

    return simulation


def start_simulation(simulation: CpuSimulation):
    processes, runtime, cpu = simulation.simulate()
    table = pd.DataFrame.from_records([p.to_dict() for p in processes])
    return table, runtime, cpu


if __name__ == "__main__":
    simulation = get_inputs()
    table, runtime, cpu = start_simulation(simulation)
    print(f"Runtime: {runtime}")
    print(f"IDLE Time: {cpu._idle_time}")

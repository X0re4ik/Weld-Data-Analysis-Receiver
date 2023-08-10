from RWSensorSimulator import RWSensorSimulator
from multiprocessing import Process

import time

def start_simulation(ID):
    RWSensorSimulator(ID).start_simulation(http_port=5001, ip="192.168.0.161")


if __name__ == '__main__':
    processes = []
    for i in range(20):
        processes.append(Process(target=start_simulation, args=[f"ReadWeld:{str(i)}"]))
        
    for process in processes:
        process.start()
        time.sleep(1)
        
    for process in processes:
        process.join()
# Press Shift+F10 to execute it or replace it with your code.
# Press Double Shift to search everywhere for classes, files, tool windows, actions, and settings.

from append_files import ManageStatistics
import sys
import matplotlib.pyplot as plt
import matplotlib.markers as mrk
import numpy as np
np.set_printoptions(threshold=sys.maxsize)


# Press the green button in the gutter to run the script.
if __name__ == '__main__':
    cold_start_file = "/home/greg/kernel/Distributed-Containers/testing/cold-starts/cold-starts.txt"

    cold_starts = np.loadtxt(cold_start_file)

    print("Mean: " + str(cold_starts.mean()))
    print("Median: " + str(np.median(cold_starts)))
    print("Stddev: " + str(cold_starts.std()))
    print("Variance: " + str(cold_starts.var()))



    cold_starts_sorted = np.sort(cold_starts)

    p_cold_starts = 1. * np.arange(len(cold_starts_sorted)) / (len(cold_starts_sorted) - 1)

    # fig, ax = plt.subplots(figsize=(5, 3))
    fig = plt.figure(figsize=(6, 3))
    ax1 = fig.add_subplot(111)
    ax1.plot(cold_starts_sorted, p_cold_starts, marker='+', markevery=20)


    ax1.set_xlabel('Per-Container Connection to Controller Overhead (ms)')
    ax1.set_ylabel('')
    plt.tight_layout()
    fig.show()

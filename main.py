# This is a sample Python script.

# Press Shift+F10 to execute it or replace it with your code.
# Press Double Shift to search everywhere for classes, files, tool windows, actions, and settings.
import matplotlib.pyplot as plt
import numpy as np
from append_files import append_files_into_one
import sys

def run():
    dc_relative_slack = np.loadtxt('dc-relative-slack.txt')
    static_relative_slack = np.loadtxt('static-relative-slack.txt')

    dc_absolute_slack = np.loadtxt('dc-absolute-slack.txt')
    static_absolute_slack = np.loadtxt('static-absolute-slack.txt')

    # print(dc_relative_slack)
    # create some randomly ddistributed data:

    # sort the data:
    data_sorted_dc_relative = np.sort(dc_relative_slack)# / 1000 #convert to ms
    data_sorted_static_relative = np.sort(static_relative_slack)
    data_sorted_dc_absolute = np.sort(dc_absolute_slack) / 100 #convert to cores
    data_sorted_static_absolute = np.sort(static_absolute_slack) / 100 #convert to cores

    # print(data_sorted_dc_relative)
    # print(data_sorted_static_relative)

    # calculate the proportional values of samples
    p_dc_relative = 1. * np.arange(len(dc_relative_slack)) / (len(dc_relative_slack) - 1)
    p_static_relative = 1. * np.arange(len(static_relative_slack)) / (len(static_relative_slack) - 1)
    p_dc_absolute = 1. * np.arange(len(dc_absolute_slack)) / (len(dc_absolute_slack) - 1)
    p_static_absolute = 1. * np.arange(len(static_absolute_slack)) / (len(static_absolute_slack) - 1)

    # plot the sorted data:
    fig = plt.figure()
    # fig, axs = plt.subplot(1, 2)
    # axs[0,0]

    ax1 = fig.add_subplot(211)
    ax1.plot(data_sorted_dc_absolute, p_dc_absolute, label="DC")
    ax1.plot(data_sorted_static_absolute, p_static_absolute, label="Static")
    ax1.set_xlabel('Absolute Slack')
    ax1.set_ylabel('')

    ax2 = fig.add_subplot(212)
    ax2.plot(data_sorted_dc_relative, p_dc_relative, label="DC")
    ax2.plot(data_sorted_static_relative, p_static_relative, label="Static")

    ax1.legend(bbox_to_anchor=(1.05, 1), loc='upper left', borderaxespad=0.)

    ax2.set_xlabel('Relative Slack')
    ax2.set_ylabel('')
    plt.tight_layout()
    fig.show()
    fig.savefig('test-absolute-and-relative-slack.png')

# Press the green button in the gutter to run the script.
if __name__ == '__main__':
    # if len(sys.argv) != 4:
    #     print("ERROR: Need type, ratio, num_files args")
    #     sys.exit(-1)
    # type = sys.argv[1]
    # ratio = sys.argv[2]
    # num_files = int(sys.argv[3])
    # filename_prefix = append_files_into_one(type, ratio, num_files)
    # run(filename_prefix, ratio)
    run()

# See PyCharm help at https://www.jetbrains.com/help/pycharm/

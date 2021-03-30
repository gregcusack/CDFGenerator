import matplotlib.pyplot as plt
import matplotlib.markers as mrk
import numpy as np

def run():

    dc_relative_slack = np.loadtxt('cloudlab/slacks/ml-based-comp/dc-relative-slack.txt')
    static_relative_slack = np.loadtxt('cloudlab/slacks/ml-based-comp/static-relative-slack.txt')

    # sort the data:
    data_sorted_dc_relative = np.sort(dc_relative_slack)# / 1000 #convert to ms
    data_sorted_static_relative = np.sort(static_relative_slack)

    # print(data_sorted_dc_relative)
    # print(data_sorted_static_relative)

    # calculate the proportional values of samples
    p_dc_relative = 1. * np.arange(len(dc_relative_slack)) / (len(dc_relative_slack) - 1)
    p_static_relative = 1. * np.arange(len(static_relative_slack)) / (len(static_relative_slack) - 1)

    plt.plot(data_sorted_dc_relative, p_dc_relative, label="DC", marker='+', markevery=20)
    plt.plot(data_sorted_static_relative, p_static_relative, label="Static", marker='x', markevery=20)

    plt.legend()
    plt.xlabel('Relative Slack')
    plt.ylabel('')
    plt.tight_layout()
    fig = plt.gcf()
    fig.set_size_inches(5,3.5)
    plt.show()
    plt.draw()
    # fig.savefig('ml-absolute-and-relative-slack.pdf')
    fig.savefig('relative-slack.pdf')


if __name__ == '__main__':
    run()


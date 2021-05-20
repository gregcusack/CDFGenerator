import os
from itertools import islice
import matplotlib.pyplot as plt
import matplotlib.markers as mrk
import numpy as np

def get_absolute_slack(limit, usage):
    return limit - usage


def get_relative_slack(limit, usage):
    if limit == 0:
        print("limit is 0!")
        return -1
    return (limit - usage) / limit

def ap_get_usage_limit(line, delimiter):
    stats = line.rstrip().split(delimiter)
    if delimiter == "\t":
        return float(stats[0]), float(stats[1])
    else:
        return float(stats[1]) / 10, float(stats[0])

def aggregate_1s(lines):
    limit_sum = usage_sum = 0
    count = 1
    for line in lines:
        stats = line.rstrip().split(",")
        limit_sum = limit_sum + int(stats[0])
        usage_sum = usage_sum + int(stats[1])
        count = count + 1
    limit_avg = limit_sum / count
    usage_avg = usage_sum / count
    return round(limit_avg, 2), round(usage_avg, 2)


def get_slacks_from_line(line, separator):
    stats = line.rstrip().split(separator)
    if separator == "\t":    #ap -> usage, limit
        limit = float(stats[1])
        usage = float(stats[0])
    else: #dc               #dc -> limit, usage
        limit = float(stats[0])
        usage = float(stats[1])

    # limit = float(stats[0])
    # usage = float(stats[1])
    # print(limit, usage)
    abs_slack = get_absolute_slack(limit, usage)
    if abs_slack < 0:
        print("[ERROR]: abs slack < 0")
        # abs_slack = get_absolute_slack(limit, usage / 10)

    rel_slack = get_relative_slack(limit, usage)
    if rel_slack < 0:
        print("[ERROR]: rel slack < 0")
        # rel_slack = get_relative_slack(limit, usage / 10)


    return abs_slack, rel_slack


def return_max_val(prev_max, new_val):
    if new_val > prev_max:
        return new_val
    return prev_max


class ManageStatistics:
    def __init__(self, measurement_, resource_, load_type, multiplier_=0):
        self.measurement = measurement_
        self.resource = resource_
        self.load_type = load_type
        self.multiplier = str(multiplier_)
        print("multiplier: " + self.multiplier)

        if self.multiplier != str(0):
            print("here")
            self.prefix_dc = "/home/greg/CDFGenerator/data/" + self.measurement + "/" + self.load_type + "/" + \
                             self.resource + "/dc-" + self.multiplier + "/"

            self.prefix_ap = "/home/greg/CDFGenerator/data/" + self.measurement + "/" + self.load_type + "/" + \
                             self.resource + "/static-" + self.multiplier + "/"

        else:
            self.prefix_dc = "/home/greg/CDFGenerator/data/" + self.measurement + "/" + self.load_type + "/" + \
                             self.resource + "/dc/"

            self.prefix_ap = "/home/greg/CDFGenerator/data/" + self.measurement + "/" + self.load_type + "/" + \
                             self.resource + "/ap/"


        
        self.abs_slack_file = "absolute-slacks.txt"
        self.rel_slack_file = "relative-slacks.txt"

    def aggregate_per_period_to_per_second(self):
        infolder = self.prefix_dc + "raw/"
        outfolder = infolder[:-1] + "-agg/"
        if not os.path.exists(outfolder):
            os.makedirs(outfolder)

        num_files_to_delete_low_usage = 0
        directory = os.fsencode(infolder)
        for file in os.listdir(directory):
            infile = os.fsdecode(file)
            infile_full_path = infolder + infile
            if infile_full_path.endswith(".txt"):
                outfile = outfolder + infile[:-4] + "-agg-1s.txt"
                max_usage = 0
                with open(outfile, "w+") as outf:
                    outf.write("1S LIMIT AGG (ns), 1S USAGE AGG (ns)\n")
                    with open(infile_full_path, "r") as inf:
                        while True:
                            lines_10 = list(islice(inf, 1))
                            if not lines_10:
                                break
                            limit_agg, usage_agg = aggregate_1s(lines_10)
                            outf.write(str(limit_agg) + "," + str(usage_agg) + "\n")
                            max_usage = return_max_val(max_usage, usage_agg)
                print("max_usage of file: " + infile + " is: " + str(max_usage))
                if self.resource == "cpu" and max_usage < 30000000:
                    print("max usage of container is less than 30% of a core! need to remove")
                    os.remove(outfile)
                    num_files_to_delete_low_usage += 1

        print("number of files deleted due to old usage: " + str(num_files_to_delete_low_usage))

    def aggregate_into_one_file(self):
        infolder = self.prefix_dc + "raw-agg/"
        outfolder = self.prefix_dc
        outfile_abs_slack = outfolder + "absolute-slacks.txt"
        outfile_rel_slack = outfolder + "relative-slacks.txt"
        directory = os.fsencode(infolder)
        with open(outfile_abs_slack, "w+") as absf, open(outfile_rel_slack, "w+") as relf:
            for file in os.listdir(directory):
                infile = os.fsdecode(file)
                infile_full_path = infolder + infile
                if infile_full_path.endswith(".txt"):
                    with open(infile_full_path, "r") as aggf:
                        # for _ in range(15):
                        next(aggf)  # skip first line (header)
                        for line in aggf:
                            abs_slack, rel_slack = get_slacks_from_line(line, ",")
                            absf.write(str(abs_slack) + "\n")
                            relf.write(str(rel_slack) + "\n")

    def remove_low_usage_containers(self, system):
        if system == "ap":
            infolder = self.prefix_ap + "raw/"
        else:
            infolder = self.prefix_dc + "raw/"

        outfolder = infolder[:-1] + "-trim/"
        if not os.path.exists(outfolder):
            os.makedirs(outfolder)

        delimiter = "\t"
        if self.multiplier != "0":
            delimiter = ","

        num_files_to_delete_low_usage = 0
        directory = os.fsencode(infolder)
        for file in os.listdir(directory):
            infile = os.fsdecode(file)
            infile_full_path = infolder + infile
            if infile_full_path.endswith(".txt"):
                outfile = outfolder + infile
                max_usage = 0
                with open(outfile, "w+") as outf:
                    with open(infile_full_path, "r") as inf:
                        print('reading in: ' + infile_full_path)
                        for line in inf:
                            usage, limit = ap_get_usage_limit(line, delimiter)
                            outf.write(str(usage) + "\t" + str(limit) + "\n")
                            max_usage = return_max_val(max_usage, usage)
                print("max_usage of file: " + infile + " is: " + str(max_usage))
                min_usage = 30000 # 30000us = 30ms = 30% of core
                if self.multiplier != "0": # values are in ns, not ms
                    min_usage = min_usage * 1000
                if self.resource == "cpu" and max_usage < min_usage: # 30000us = 30ms = 30% of core
                        print("max usage of container is less than 30% of a core! need to remove")
                        os.remove(outfile)
                        num_files_to_delete_low_usage += 1


        print("number of files deleted due to low usage (ap): " + str(num_files_to_delete_low_usage))

    def aggregate_into_one_file_autopilot(self, system):
        if system == "ap":
            infolder = self.prefix_ap + "raw-trim/"
            outfolder = self.prefix_ap
        else:
            infolder = self.prefix_dc + "raw-trim/"
            outfolder = self.prefix_dc

        outfile_abs_slack = outfolder + "absolute-slacks.txt"
        outfile_rel_slack = outfolder + "relative-slacks.txt"
        directory = os.fsencode(infolder)
        with open(outfile_abs_slack, "w+") as absf, open(outfile_rel_slack, "w+") as relf:
            for file in os.listdir(directory):
                infile = os.fsdecode(file)
                infile_full_path = infolder + infile
                if infile_full_path.endswith(".txt"):
                    with open(infile_full_path, "r") as aggf:
                        for line in aggf:
                            abs_slack, rel_slack = get_slacks_from_line(line, "\t")
                            if abs_slack >= 0:# and abs_slack < 50000:
                                if self.resource == "cpu" and abs_slack < 200000:
                                    absf.write(str(abs_slack) + "\n")
                                elif self.resource == "mem" and abs_slack < 200000000:
                                    absf.write(str(abs_slack) + "\n")
                            if rel_slack >= 0:
                                relf.write(str(rel_slack) + "\n")

    def run(self):

        """ DC ABSOLUTE """
        dc_absolute_slack_path = self.prefix_dc + self.abs_slack_file
        print("dc_abs_slack_file: " + dc_absolute_slack_path)
        dc_absolute_slack = np.loadtxt(dc_absolute_slack_path)
        data_sorted_dc_absolute = np.sort(dc_absolute_slack)
        if self.resource == "cpu":
            data_sorted_dc_absolute = data_sorted_dc_absolute / 1000 / 1000 / 100 # ns -> us -> ms -> cores
        elif self.resource == "mem":
            data_sorted_dc_absolute = data_sorted_dc_absolute / 1024 / 1024 # bytes to Mib
        p_dc_absolute = 1. * np.arange(len(dc_absolute_slack)) / (len(dc_absolute_slack) - 1)

        """ DC RELATIVE """
        dc_relative_slack_path = self.prefix_dc + self.rel_slack_file
        print("dc_rel_slack_file: " + dc_relative_slack_path)
        dc_relative_slack = np.loadtxt(dc_relative_slack_path)
        data_sorted_dc_relative = np.sort(dc_relative_slack)  # / 1000 #convert to ms
        p_dc_relative = 1. * np.arange(len(dc_relative_slack)) / (len(dc_relative_slack) - 1)

        """ AP ABSOLUTE """
        ap_absolute_slack_path = self.prefix_ap + self.abs_slack_file
        print("ap_abs_slack_file: " + ap_absolute_slack_path)
        ap_absolute_slack = np.loadtxt(ap_absolute_slack_path)
        data_sorted_ap_absolute = np.sort(ap_absolute_slack)
        if self.resource == "cpu":
            data_sorted_ap_absolute = data_sorted_ap_absolute / 1000 / 100 # us -> ms -> cores
        elif self.resource == "mem":
            data_sorted_ap_absolute = data_sorted_ap_absolute / 1024 / 1024 # bytes to MiB
        p_ap_absolute = 1. * np.arange(len(ap_absolute_slack)) / (len(ap_absolute_slack) - 1)

        """ AP RELATIVE """
        ap_relative_slack_path = self.prefix_ap + self.rel_slack_file
        print("ap_rel_slack_file: " + ap_relative_slack_path)
        ap_relative_slack = np.loadtxt(ap_relative_slack_path)
        data_sorted_ap_relative = np.sort(ap_relative_slack)  # / 1000 #convert to ms
        p_ap_relative = 1. * np.arange(len(ap_relative_slack)) / (len(ap_relative_slack) - 1)


        fig = plt.figure()
        # fig, axs = plt.subplot(1, 2)
        # axs[0,0]

        other_label = "AP"
        if self.multiplier != "0":
            other_label = "Static-" + self.multiplier

        ax1 = fig.add_subplot(211)
        ax1.plot(data_sorted_dc_absolute, p_dc_absolute, label="DC", marker='+', markevery=20)
        ax1.plot(data_sorted_ap_absolute, p_ap_absolute, label=other_label, marker='x', markevery=20)
        # ax1.plot(data_ml_exact_abs_slack, p_ml_exact_abs_slack, label="ML Ideal", marker='*', markevery=20)
        # ax1.plot(data_ml_conserv_abs_slack, p_ml_conserv_abs_slack, label="ML Conserv.", marker=mrk.TICKRIGHT, markevery=20)

        if self.resource == "cpu":
            ax1.set_xlabel('Absolute Slack (cores)')
        if self.resource == "mem":
            ax1.set_xlabel('Absolute Slack (MiB)')

        ax1.set_ylabel('')

        ax2 = fig.add_subplot(212)
        ax2.plot(data_sorted_dc_relative, p_dc_relative, label="DC", marker='+', markevery=20)
        ax2.plot(data_sorted_ap_relative, p_ap_relative, label=other_label, marker='x', markevery=20)
        # ax2.plot(data_ml_exact_relative_slack, p_ml_exact_relative_slack, label="ML Ideal", marker='*', markevery=20)
        # ax2.plot(data_ml_conserv_relative_slack, p_ml_conserv_relative_slacke, label="ML Conserv.", marker=mrk.TICKRIGHT, markevery=20)

        # ax1.legend(bbox_to_anchor=(1.05, 1), loc='upper left', borderaxespad=0.)
        ax1.legend()

        ax2.set_xlabel('Relative Slack')
        ax2.set_ylabel('')
        plt.tight_layout()
        fig.show()
        filename = self.prefix_ap[:-3] + "plot.pdf"
        fig.savefig(filename)

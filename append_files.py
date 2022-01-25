import os, sys
from itertools import islice
import matplotlib.pyplot as plt
import matplotlib.markers as mrk
import numpy as np
np.set_printoptions(threshold=sys.maxsize)

def get_absolute_slack(limit, usage):
    return limit - usage


def get_relative_slack(limit, usage):
    if limit == 0:
        print("limit is 0!")
        return -1
    return (limit - usage) / limit

def ap_get_usage_limit(line, delimiter):
    if "\t" in line:
        stats = line.rstrip().split("\t")
        delimiter = "\t"
    else:
        stats = line.rstrip().split(",")
        delimiter = ","

    if delimiter == "\t":
        return float(stats[0]), float(stats[1])
    else:
        return float(stats[1]), float(stats[0])

def static_get_usage_limit(line, delimiter):
    if "\t" in line:
        stats = line.rstrip().split("\t")
        delimiter = "\t"
    else:
        stats = line.rstrip().split(",")
        delimiter = ","

    if delimiter == "\t":
        return float(stats[0]), float(stats[1])
    else:
        return float(stats[1]), float(stats[0])

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

    # print(usage, limit)

    # limit = float(stats[0])
    # usage = float(stats[1])
    # print(limit, usage)
    abs_slack = get_absolute_slack(limit, usage)
    if abs_slack < 0:
        print("[ERROR]: abs slack < 0")
        print("usage, limit: " + str(usage) + ", " + str(limit))
        # abs_slack = 0.0
        # abs_slack = get_absolute_slack(limit, usage / 10)

    rel_slack = get_relative_slack(limit, usage)
    if rel_slack < 0:
        print("[ERROR]: rel slack < 0")
        # rel_slack = get_relative_slack(limit, usage / 10)


    return abs_slack, rel_slack

def get_static_slacks_from_line(line, separator):
    stats = line.rstrip().split(separator)
    limit = float(stats[1])
    usage = float(stats[0])

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
    def __init__(self, service_, measurement_, resource_, load_type, multiplier_=0, rel_slack_="no"):
        self.service = service_
        self.measurement = measurement_
        self.resource = resource_
        self.load_type = load_type
        self.multiplier = str(multiplier_)
        self.rel_slack = rel_slack_
        self.sysname = "Escra"

        print("multiplier: " + self.multiplier)

        base = "/home/greg/Desktop/"
        # base = "/Users/gcusack/Desktop/"

        if self.service == "grid-search":
            self.prefix_dc = base + "CDFGenerator/data/" + self.measurement + "/" + self.service + "/dc/"
            self.prefix_vanilla = base + "CDFGenerator/data/" + self.measurement + "/" + self.service + "/vanilla/"

        elif self.service == "image-proc":
            self.prefix_dc = base + "CDFGenerator/data/" + self.measurement + "/" + self.service + "/dc/"
            self.prefix_vanilla = base + "CDFGenerator/data/" + self.measurement + "/" + self.service + "/vanilla/"


        elif self.multiplier == str(-1):
            multiplier = "1.5"
            self.prefix_dc_alloc = base + "CDFGenerator/data/" + self.measurement + "/" + self.service + "/" + \
                             self.load_type + "/" + self.resource + "/dc-" + multiplier + "/"
            self.prefix_static = base + "CDFGenerator/data/" + self.measurement + "/" + self.service + "/" + \
                                 self.load_type + "/" + self.resource + "/static-" + multiplier + "/"
            self.prefix_dc = base + "CDFGenerator/data/" + self.measurement + "/" + self.service + "/" + \
                             self.load_type + "/" + self.resource + "/dc/"
            self.prefix_ap = base + "CDFGenerator/data/" + self.measurement + "/" + self.service + "/" + \
                             self.load_type + "/" + self.resource + "/ap/"

        elif self.multiplier != str(0):
            self.prefix_dc = base + "CDFGenerator/data/" + self.measurement + "/" + self.service + "/" + \
                             self.load_type + "/" + self.resource + "/dc-" + self.multiplier + "/"

            self.prefix_static = base + "CDFGenerator/data/" + self.measurement + "/" + self.service + "/" + \
                                 self.load_type + "/" + self.resource + "/static-" + self.multiplier + "/"

        else:
            self.prefix_dc = base + "CDFGenerator/data/" + self.measurement + "/" + self.service + "/" + \
                             self.load_type + "/" + self.resource + "/dc/"

            self.prefix_ap = base + "CDFGenerator/data/" + self.measurement + "/" + self.service + "/" + \
                             self.load_type + "/" + self.resource + "/ap/"

        
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
        infolders = ""
        if system == "dc-serverless":
            infolders = self.prefix_dc + "ow-"
        elif system == "vanilla":
            infolders = self.prefix_vanilla + "ow-"
        else:
            sys.exit(-1)

        outfolder = infolders[:-1] + "-trim/"
        if not os.path.exists(outfolder):
            os.makedirs(outfolder)

        num_files_to_delete_low_usage = 0
        count_files = 0
        num_data_files = 0
        if self.service == "grid-search":
            num_data_files = 3
        else:
            num_data_files = 1
        for i in range(num_data_files):
            infolder = infolders + str(i + 2) + "/" + self.resource + "_limits/"
            print("in folder: " + infolder)

            directory = os.fsencode(infolder)
            for file in os.listdir(directory):
                infile = os.fsdecode(file)
                infile_full_path = infolder + infile
                print("infile_full_path: " + infile_full_path)
                if infile.startswith("limit_wsko") and infile_full_path.endswith(".txt"):
                    print("suuuuhhhh")
                    outfile = outfolder + infile[:-4] + str(count_files) + ".txt"
                    max_usage = 0
                    with open(outfile, "w+") as outf:
                        with open(infile_full_path, "r") as inf:
                            print('reading in: ' + infile_full_path)
                            for line in inf:
                                usage, limit = ap_get_usage_limit(line, "\t")
                                if str(usage) != "0.0":
                                    outf.write(str(usage) + "\t" + str(limit) + "\n")
                                    max_usage = return_max_val(max_usage, usage)
                            count_files += 1

                    print("max_usage of file: " + infile + " is: " + str(max_usage))
                    if self.resource == "cpu":
                        if system == "ap" or system == "dc-serverless" or system == "vanilla":
                            min_usage = 30000 # 30000us = 30ms = 30% of core
                        else:
                            min_usage = 30000000  # 30000000ns = 30000us = 30ms = 30% of core
                        if max_usage < min_usage:
                            print("max usage of container is less than 30% of a core! need to remove")
                            os.remove(outfile)
                            num_files_to_delete_low_usage += 1
                    else:
                        min_usage = 10000000
                        if max_usage < min_usage:
                            print("max usage of container is less than 30% of a core! need to remove")
                            os.remove(outfile)
                            num_files_to_delete_low_usage += 1

        print("number of files deleted due to low usage (ap): " + str(num_files_to_delete_low_usage))
        print("total files read: " + str(count_files))

    def aggregate_into_one_file_autopilot(self, system):
        infolder = ""
        outfolder = ""
        if system == "dc-serverless":
            infolder = self.prefix_dc + "ow-trim/"
            outfolder = self.prefix_dc
        if system == "vanilla":
            infolder = self.prefix_vanilla + "ow-trim/"
            outfolder = self.prefix_vanilla

        outfile_abs_slack = outfolder + "absolute-slacks.txt"
        outfile_rel_slack = outfolder + "relative-slacks.txt"
        directory = os.fsencode(infolder)
        ap_large_abs_slacks = []
        with open(outfile_abs_slack, "w+") as absf, open(outfile_rel_slack, "w+") as relf:
            for file in os.listdir(directory):
                infile = os.fsdecode(file)
                infile_full_path = infolder + infile
                if infile_full_path.endswith(".txt"):
                    with open(infile_full_path, "r") as aggf:
                        for line in aggf:
                            abs_slack, rel_slack = get_slacks_from_line(line, "\t")
                            if abs_slack == 0:
                                print("abs slack 0: " + infile_full_path)
                            if system == "ap" or system == "dc-serverless" or system == "vanilla":
                                if self.resource == "cpu":
                                    if abs_slack >= 0 and abs_slack < 500000:
                                        absf.write(str(abs_slack) + "\n")
                                    else:
                                        ap_large_abs_slacks.append(abs_slack)
                                else:
                                    if abs_slack >= 0 and abs_slack < 5000 * 1024 * 1024:
                                        absf.write(str(abs_slack) + "\n")
                                    else:
                                        ap_large_abs_slacks.append(abs_slack)

                            elif abs_slack >= 0:
                                absf.write(str(abs_slack) + "\n")

                            if rel_slack >= 0:
                                relf.write(str(rel_slack) + "\n")


    def remove_low_usage_containers_static(self):
        infolder = self.prefix_static + "raw/"
        outfolder = infolder[:-1] + "-trim/"
        if not os.path.exists(outfolder):
            os.makedirs(outfolder)

        if self.resource == "mem":
            delimiter = "\t"
        else:
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
                            usage, limit = static_get_usage_limit(line, delimiter)
                            outf.write(str(usage) + "\t" + str(limit) + "\n")
                            max_usage = return_max_val(max_usage, usage)
                print("max_usage of file: " + infile + " is: " + str(max_usage/100000) + " cores")
                # min_usage = 30000 # 30000us = 30ms = 30% of core
                # if self.resource == "cpu" and max_usage < min_usage: # 30000us = 30ms = 30% of core
                #         print("max usage of container is less than 30% of a core! need to remove")
                #         os.remove(outfile)
                #         num_files_to_delete_low_usage += 1

    def aggregate_into_one_file_static(self):
        infolder = self.prefix_static + "raw-trim/"
        outfolder = self.prefix_static

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
                            abs_slack, rel_slack = get_static_slacks_from_line(line, "\t")
                            print("abs slack: " + str(abs_slack))
                            if abs_slack >= 0:# and abs_slack < 50000:
                                absf.write(str(abs_slack) + "\n")

                                # if self.resource == "cpu" and abs_slack < 200000:
                                #     absf.write(str(abs_slack) + "\n")
                                # elif self.resource == "mem":
                                #     if abs_slack > 200000000:
                                #         print("abs slack massive: " + infile_full_path)
                                #     if abs_slack < 200000000:
                                #         absf.write(str(abs_slack) + "\n")
                            if rel_slack >= 0:
                                relf.write(str(rel_slack) + "\n")

    def run(self):

        """ DC ABSOLUTE """
        dc_absolute_slack_path = self.prefix_dc + self.abs_slack_file
        print("dc_abs_slack_file: " + dc_absolute_slack_path)
        dc_absolute_slack = np.loadtxt(dc_absolute_slack_path)
        data_sorted_dc_absolute = np.sort(dc_absolute_slack)
        if self.resource == "cpu":
            data_sorted_dc_absolute = data_sorted_dc_absolute / 1000 / 100 # us -> ms -> cores
        elif self.resource == "mem":
            data_sorted_dc_absolute = data_sorted_dc_absolute / 1024 / 1024 # bytes to Mib
        p_dc_absolute = 1. * np.arange(len(dc_absolute_slack)) / (len(dc_absolute_slack) - 1)

        # """ DC RELATIVE """
        # dc_relative_slack_path = self.prefix_dc + self.rel_slack_file
        # print("dc_rel_slack_file: " + dc_relative_slack_path)
        # dc_relative_slack = np.loadtxt(dc_relative_slack_path)
        # data_sorted_dc_relative = np.sort(dc_relative_slack)  # / 1000 #convert to ms
        # p_dc_relative = 1. * np.arange(len(dc_relative_slack)) / (len(dc_relative_slack) - 1)

        """ AP ABSOLUTE """
        ap_absolute_slack_path = self.prefix_vanilla + self.abs_slack_file
        print("ap_abs_slack_file: " + ap_absolute_slack_path)
        ap_absolute_slack = np.loadtxt(ap_absolute_slack_path)
        data_sorted_ap_absolute = np.sort(ap_absolute_slack)
        if self.resource == "cpu":
            data_sorted_ap_absolute = data_sorted_ap_absolute / 1000 / 100 # us -> ms -> cores
        elif self.resource == "mem":
            data_sorted_ap_absolute = data_sorted_ap_absolute / 1024 / 1024 # bytes to MiB
        p_ap_absolute = 1. * np.arange(len(ap_absolute_slack)) / (len(ap_absolute_slack) - 1)

        # """ AP RELATIVE """
        # ap_relative_slack_path = self.prefix_ap + self.rel_slack_file
        # print("ap_rel_slack_file: " + ap_relative_slack_path)
        # ap_relative_slack = np.loadtxt(ap_relative_slack_path)
        # data_sorted_ap_relative = np.sort(ap_relative_slack)  # / 1000 #convert to ms
        # p_ap_relative = 1. * np.arange(len(ap_relative_slack)) / (len(ap_relative_slack) - 1)


        fig = plt.figure()
        # fig, axs = plt.subplot(1, 2)
        # axs[0,0]

        other_label = "Vanilla Openwhisk"
        if self.multiplier != "0":
            other_label = "Static-" + self.multiplier

        ax1 = fig.add_subplot(111)
        ax1.plot(data_sorted_dc_absolute, p_dc_absolute, label=self.sysname + " w/ Openwhisk", marker='+', markevery=400)
        ax1.plot(data_sorted_ap_absolute, p_ap_absolute, label=other_label, marker='x', markevery=400)
        # ax1.plot(data_ml_exact_abs_slack, p_ml_exact_abs_slack, label="ML Ideal", marker='*', markevery=20)
        # ax1.plot(data_ml_conserv_abs_slack, p_ml_conserv_abs_slack, label="ML Conserv.", marker=mrk.TICKRIGHT, markevery=20)

        if self.resource == "cpu":
            ax1.set_xlabel('Absolute Slack (cores)')
        if self.resource == "mem":
            ax1.set_xlabel('Absolute Slack (MiB)')

        ax1.set_ylabel('')

        # ax2 = fig.add_subplot(212)
        # ax2.plot(data_sorted_dc_relative, p_dc_relative, label=self.sysname, marker='+', markevery=20)
        # ax2.plot(data_sorted_ap_relative, p_ap_relative, label=other_label, marker='x', markevery=20)
        # ax2.plot(data_ml_exact_relative_slack, p_ml_exact_relative_slack, label="ML Ideal", marker='*', markevery=20)
        # ax2.plot(data_ml_conserv_relative_slack, p_ml_conserv_relative_slacke, label="ML Conserv.", marker=mrk.TICKRIGHT, markevery=20)

        # ax1.legend(bbox_to_anchor=(1.05, 1), loc='upper left', borderaxespad=0.)
        ax1.legend()

        # ax2.set_xlabel('Relative Slack')
        # ax2.set_ylabel('')
        plt.tight_layout()
        fig.show()
        filename = self.prefix_vanilla[:-3] + "-plot.pdf"
        file_2 = self.prefix_vanilla[:-3] + "-plot.png"
        fig.savefig(filename)
        fig.savefig(file_2)

    def run_static(self):

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

        """ STATIC ABSOLUTE """
        static_absolute_slack_path = self.prefix_static + self.abs_slack_file
        print("static_abs_slack_file: " + static_absolute_slack_path)
        static_absolute_slack = np.loadtxt(static_absolute_slack_path)
        data_sorted_static_absolute = np.sort(static_absolute_slack)
        if self.resource == "cpu":
            data_sorted_static_absolute = data_sorted_static_absolute / 1000 / 100 # us -> ms -> cores
        elif self.resource == "mem":
            data_sorted_static_absolute = data_sorted_static_absolute / 1024 / 1024 # bytes to MiB
        p_static_absolute = 1. * np.arange(len(static_absolute_slack)) / (len(static_absolute_slack) - 1)

        """ STATIC RELATIVE """
        static_relative_slack_path = self.prefix_static + self.rel_slack_file
        print("static_rel_slack_file: " + static_relative_slack_path)
        static_relative_slack = np.loadtxt(static_relative_slack_path)
        data_sorted_static_relative = np.sort(static_relative_slack)  # / 1000 #convert to ms
        p_static_relative = 1. * np.arange(len(static_relative_slack)) / (len(static_relative_slack) - 1)

        other_label = "AP"
        rm_txt = -3
        sysname = self.sysname
        if self.multiplier != "0":
            if self.multiplier == "75":
                multiplier = "0.75"
                rm_txt = -4
                sysname = sysname + "-0.75x"
            elif self.multiplier == "1":
                multiplier = "1.0"
                rm_txt = -3
                sysname = sysname + "-1.0x"
            else:
                multiplier = self.multiplier
                rm_txt = -5
                sysname = sysname + "-1.5x"
            other_label = "Static-" + multiplier + "x"

        xaxis_label = ""
        marker_freq = 100
        if self.resource == "cpu":
            xaxis_label = "Absolute Slack (cores)"
            marker_freq = 200
        if self.resource == "mem":
            xaxis_label = "Absolute Slack (MiB)"
            marker_freq = 75


        if self.rel_slack == "yes":
            fig = plt.figure()
            # fig, axs = plt.subplot(1, 2)
            # axs[0,0]

            ax1 = fig.add_subplot(211)
            ax1.plot(data_sorted_dc_absolute, p_dc_absolute, label=sysname, marker='+', markevery=marker_freq)
            ax1.plot(data_sorted_static_absolute, p_static_absolute, label=other_label, marker='x', markevery=marker_freq)
            # ax1.plot(data_ml_exact_abs_slack, p_ml_exact_abs_slack, label="ML Ideal", marker='*', markevery=20)
            # ax1.plot(data_ml_conserv_abs_slack, p_ml_conserv_abs_slack, label="ML Conserv.", marker=mrk.TICKRIGHT, markevery=20)

            ax1.set_xlabel(xaxis_label)

            ax1.set_ylabel('')

            ax2 = fig.add_subplot(212)
            ax2.plot(data_sorted_dc_relative, p_dc_relative, label=sysname, marker='+', markevery=marker_freq)
            ax2.plot(data_sorted_static_relative, p_static_relative, label=other_label, marker='x', markevery=marker_freq)
            # ax2.plot(data_ml_exact_relative_slack, p_ml_exact_relative_slack, label="ML Ideal", marker='*', markevery=20)
            # ax2.plot(data_ml_conserv_relative_slack, p_ml_conserv_relative_slacke, label="ML Conserv.", marker=mrk.TICKRIGHT, markevery=20)

            # ax1.legend(bbox_to_anchor=(1.05, 1), loc='upper left', borderaxespad=0.)
            ax1.legend()

            ax2.set_xlabel('Relative Slack')
            ax2.set_ylabel('')
            plt.tight_layout()

        else:
            fig, ax = plt.subplots(figsize=(5,3))
            ax.plot(data_sorted_dc_absolute, p_dc_absolute, label=sysname, marker='+', markevery=marker_freq)
            ax.plot(data_sorted_static_absolute, p_static_absolute, label=other_label, marker='x', markevery=marker_freq)
            ax.set_xlabel(xaxis_label)
            ax.set_ylabel('')
            plt.tight_layout()
            ax.legend(title=self.load_type.capitalize() + " Workload")


        fig.show()

        filename = self.prefix_dc[:rm_txt] + "-plot-" + self.resource + "-" + self.multiplier + "x.pdf"
        fig.savefig(filename)
        filename = self.prefix_dc[:rm_txt] + "-plot-" + self.resource + "-" + self.multiplier + "x.png"
        fig.savefig(filename)


    def run_all(self):

        """ DC ABSOLUTE ALLOC """
        dc_absolute_slack_path_alloc = self.prefix_dc_alloc + self.abs_slack_file
        print("dc_abs_slack_file: " + dc_absolute_slack_path_alloc)
        dc_absolute_slack_alloc = np.loadtxt(dc_absolute_slack_path_alloc)
        data_sorted_dc_absolute_alloc = np.sort(dc_absolute_slack_alloc)
        if self.resource == "cpu":
            data_sorted_dc_absolute_alloc = data_sorted_dc_absolute_alloc / 1000 / 1000 / 100 # ns -> us -> ms -> cores
        elif self.resource == "mem":
            data_sorted_dc_absolute_alloc = data_sorted_dc_absolute_alloc / 1024 / 1024 # bytes to Mib
        p_dc_absolute_alloc = 1. * np.arange(len(dc_absolute_slack_alloc)) / (len(dc_absolute_slack_alloc) - 1)

        """ DC RELATIVE ALLOC """
        dc_relative_slack_path_alloc = self.prefix_dc_alloc + self.rel_slack_file
        print("dc_rel_slack_file: " + dc_relative_slack_path_alloc)
        dc_relative_slack_alloc = np.loadtxt(dc_relative_slack_path_alloc)
        data_sorted_dc_relative_alloc = np.sort(dc_relative_slack_alloc)  # / 1000 #convert to ms
        p_dc_relative_alloc = 1. * np.arange(len(dc_relative_slack_alloc)) / (len(dc_relative_slack_alloc) - 1)

        """ STATIC ABSOLUTE """
        static_absolute_slack_path = self.prefix_static + self.abs_slack_file
        print("static_abs_slack_file: " + static_absolute_slack_path)
        static_absolute_slack = np.loadtxt(static_absolute_slack_path)
        data_sorted_static_absolute = np.sort(static_absolute_slack)
        if self.resource == "cpu":
            data_sorted_static_absolute = data_sorted_static_absolute / 1000 / 100 # us -> ms -> cores
            print(data_sorted_static_absolute)
        elif self.resource == "mem":
            data_sorted_static_absolute = data_sorted_static_absolute / 1024 / 1024 # bytes to MiB
        p_static_absolute = 1. * np.arange(len(static_absolute_slack)) / (len(static_absolute_slack) - 1)

        """ STATIC RELATIVE """
        static_relative_slack_path = self.prefix_static + self.rel_slack_file
        print("static_rel_slack_file: " + static_relative_slack_path)
        static_relative_slack = np.loadtxt(static_relative_slack_path)
        data_sorted_static_relative = np.sort(static_relative_slack)  # / 1000 #convert to ms
        p_static_relative = 1. * np.arange(len(static_relative_slack)) / (len(static_relative_slack) - 1)

        """ AP ABSOLUTE """
        ap_absolute_slack_path = self.prefix_ap + self.abs_slack_file
        print("ap_abs_slack_file: " + ap_absolute_slack_path)
        ap_absolute_slack = np.loadtxt(ap_absolute_slack_path)
        data_sorted_ap_absolute = np.sort(ap_absolute_slack)
        if self.resource == "cpu":
            data_sorted_ap_absolute = data_sorted_ap_absolute / 1000 / 100  # us -> ms -> cores
        elif self.resource == "mem":
            data_sorted_ap_absolute = data_sorted_ap_absolute / 1024 / 1024  # bytes to MiB
        p_ap_absolute = 1. * np.arange(len(ap_absolute_slack)) / (len(ap_absolute_slack) - 1)

        """ AP RELATIVE """
        ap_relative_slack_path = self.prefix_ap + self.rel_slack_file
        print("ap_rel_slack_file: " + ap_relative_slack_path)
        ap_relative_slack = np.loadtxt(ap_relative_slack_path)
        data_sorted_ap_relative = np.sort(ap_relative_slack)  # / 1000 #convert to ms
        p_ap_relative = 1. * np.arange(len(ap_relative_slack)) / (len(ap_relative_slack) - 1)

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

        xaxis_label = ""
        marker_freq = 100
        if self.resource == "cpu":
            xaxis_label = "Absolute Slack (cores)"
            marker_freq = 200
            marker_freq_dc = marker_freq * 10
            market_freq_dc_limit = marker_freq * 4
            marker_freq_ap = 100
        if self.resource == "mem":
            xaxis_label = "Absolute Slack (MiB)"
            marker_freq = 200
            marker_freq_dc = 100
            market_freq_dc_limit = marker_freq
            marker_freq_ap = 100

        if self.rel_slack == "yes":
            fig = plt.figure()
            # fig, axs = plt.subplot(1, 2)
            # axs[0,0]

            ax1 = fig.add_subplot(211)
            ax1.plot(data_sorted_dc_absolute_alloc, p_dc_absolute_alloc, label=self.sysname + "-1.0x", marker='*',
                     markevery=marker_freq_dc)
            ax1.plot(data_sorted_ap_absolute, p_ap_absolute, label="Autopilot", marker=mrk.TICKRIGHT,
                     markevery=marker_freq)
            ax1.plot(data_sorted_dc_absolute, p_dc_absolute, label=self.sysname + "-nolimit", marker='+',
                     markevery=marker_freq)
            ax1.plot(data_sorted_static_absolute, p_static_absolute, label="Static-1.0x", marker='x',
                     markevery=marker_freq)

            ax1.set_xlabel(xaxis_label)

            ax1.set_ylabel('')

            ax2 = fig.add_subplot(212)
            ax2.plot(data_sorted_dc_relative_alloc, p_dc_relative_alloc, label=self.sysname + "-1.0x", marker='*',
                     markevery=marker_freq)
            ax2.plot(data_sorted_ap_relative, p_ap_relative, label="Autopilot", marker=mrk.TICKRIGHT,
                     markevery=marker_freq)
            ax2.plot(data_sorted_dc_relative, p_dc_relative, label=self.sysname + "-nolimit", marker='+', markevery=marker_freq)
            ax2.plot(data_sorted_static_relative, p_static_relative, label="Static-1.0x", marker='x', markevery=marker_freq)

            # ax1.legend(bbox_to_anchor=(1.05, 1), loc='upper left', borderaxespad=0.)
            ax1.legend()

            ax2.set_xlabel('Relative Slack')
            ax2.set_ylabel('')
            plt.tight_layout()

        else:
            fig, ax = plt.subplots(figsize=(5,3))
            if self.resource == "cpu":
                ax.set_xlim([-.25,4])
            # ax.plot(data_sorted_dc_absolute_alloc, p_dc_absolute_alloc, label=self.sysname + "-1.0x", marker='*',
            #         markevery=market_freq_dc_limit)
            ax.plot(data_sorted_dc_absolute, p_dc_absolute, label=self.sysname, marker='+',
                    markevery=marker_freq_dc)
            ax.plot(data_sorted_ap_absolute, p_ap_absolute, label="Autopilot", marker=mrk.TICKRIGHT,
                    markevery=marker_freq_ap)
            ax.plot(data_sorted_static_absolute, p_static_absolute, label="Static", marker='x', markevery=marker_freq)

            # print(p_dc_absolute)
            count_dc = 0
            count_ap = 0
            count_static = 0
            val = .70
            val_up = val + .005
            print("-----------------")
            for i in p_dc_absolute:
                if i > val and i < val_up:
                    print(count_dc)
                    break
                count_dc += 1

            print("%%%%%%%%%%%%%%%")
            for i in p_ap_absolute:
                if i > val and i < val_up:
                    print(count_ap)
                    break
                count_ap += 1
            print("##############")
            for i in p_static_absolute:
                if i > val and i < val_up:
                    print(count_static)
                    break
                count_static += 1

            dc = data_sorted_dc_absolute[count_dc]
            ap = data_sorted_ap_absolute[count_ap]
            static = data_sorted_static_absolute[count_static]
            print(data_sorted_dc_absolute[count_dc])
            print(data_sorted_ap_absolute[count_ap])
            print(data_sorted_static_absolute[count_static])

            out_x = ap/dc
            out_per = (ap - dc) / ap
            print(out_per, out_x)



            ax.set_xlabel(xaxis_label)
            ax.set_ylabel('')
            plt.tight_layout()
            ax.legend(title=self.load_type.capitalize() + " Workload")


        fig.show()

        filename = self.prefix_dc[:-1] + "-plot-" + self.load_type + "-" + self.resource + "-DC-AP-Static" + ".pdf"
        fig.savefig(filename)
        filename = self.prefix_dc[:-1] + "-plot-" + self.load_type + "-" + self.resource + "-DC-AP-Static" + ".png"
        fig.savefig(filename)


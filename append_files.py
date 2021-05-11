import os
from itertools import islice


def get_absolute_slack(limit, usage):
    return limit - usage


def get_relative_slack(limit, usage):
    return (limit - usage) / limit


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


def get_slacks_from_agg_line(line):
    stats = line.rstrip().split(",")
    limit = float(stats[0])
    usage = float(stats[1])
    abs_slack = get_absolute_slack(limit, usage)
    if abs_slack < 0:
        print("[ERROR]: abs slack < 0")

    rel_slack = get_relative_slack(limit, usage)
    if rel_slack < 0:
        print("[ERROR]: rel slack < 0")

    return abs_slack, rel_slack


class ManageStatistics:
    def __init__(self, measurement_, resource_, ratio_, duration_, system_):
        self.measurement = measurement_
        self.resource = resource_
        self.ratio = ratio_
        self.duration = duration_
        self.system = system_

    def aggregate_per_period_to_per_second(self):
        prefix = "/home/greg/Desktop/CDFGenerator/data/"
        infolder = prefix + self.measurement + "/logs-" + self.resource + "-" + self.ratio + "x-" + self.duration + \
                   "min" + "-" + self.system + "/"
        outfolder = infolder[:-1] + "-agg/"
        if not os.path.exists(outfolder):
            os.makedirs(outfolder)

        directory = os.fsencode(infolder)
        for file in os.listdir(directory):
            infile = os.fsdecode(file)
            infile_full_path = infolder + infile
            if infile_full_path.endswith(".txt"):
                outfile = outfolder + infile[:-4] + "-agg-1s.txt"
                with open(outfile, "w+") as outf:
                    outf.write("1S LIMIT AGG (ns), 1S USAGE AGG (ns)\n")
                    with open(infile_full_path, "r") as inf:
                        while True:
                            lines_10 = list(islice(inf, 10))
                            if not lines_10:
                                break
                            limit_agg, usage_agg = aggregate_1s(lines_10)
                            outf.write(str(limit_agg) + "," + str(usage_agg) + "\n")

        return outfolder

    def aggregate_into_one_file(self, agg_file_folder):
        prefix = "/home/greg/Desktop/CDFGenerator/data/"
        outfolder = prefix + self.measurement + "/"
        outfile_abs_slack = outfolder + "logs-" + self.resource + "-" + self.ratio + "x-" + self.duration + \
                            "min" + "-" + self.system + "-ALL-absolute.txt"
        outfile_rel_slack = outfolder + "logs-" + self.resource + "-" + self.ratio + "x-" + self.duration + \
                            "min" + "-" + self.system + "-ALL-relative.txt"
        directory = os.fsencode(agg_file_folder)
        with open(outfile_abs_slack, "w+") as absf, open(outfile_rel_slack, "w+") as relf:
            for file in os.listdir(directory):
                infile = os.fsdecode(file)
                infile_full_path = agg_file_folder + infile
                if infile_full_path.endswith(".txt"):
                    with open(infile_full_path, "r") as aggf:
                        next(aggf)  # skip first line (header)
                        for line in aggf:
                            abs_slack, rel_slack = get_slacks_from_agg_line(line)
                            absf.write(str(abs_slack) + "\n")
                            relf.write(str(rel_slack) + "\n")

    #
    # filename_prefix = infolder + type + "-" + ratio + "x-v"
    #
    # for i in range(num_files):
    #     infile = filename_prefix + str(i) + ".txt"
    #     print(infile)
    #     temp_files.append(infile)
    #
    # outfile = filename_prefix[:-1] + "ALL.txt"
    # with open(outfile, "w+") as f:
    #     for tempfile in temp_files:
    #         with open(tempfile, "r") as tf:
    #             for line in tf:
    #                 f.write(line)
    #
    # return folder_prefix

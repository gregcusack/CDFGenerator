# Press Shift+F10 to execute it or replace it with your code.
# Press Double Shift to search everywhere for classes, files, tool windows, actions, and settings.

from append_files import ManageStatistics
import sys


# Press the green button in the gutter to run the script.
if __name__ == '__main__':
    if len(sys.argv) <= 5:
        print("ERROR: Need type, ratio, num_files args")
        sys.exit(-1)
    service = sys.argv[1]
    measurement = sys.argv[2]       # slack/throttles/ooms
    resource = sys.argv[3]          # cpu/mem
    load_type = sys.argv[4]         # static, exp, burst
    rel_slack = sys.argv[5]
    multiplier = 0
    if len(sys.argv) == 7:
        try:
            multiplier = int(sys.argv[6])
        except:
            multiplier = float(sys.argv[6])

    resources = ["cpu", "mem"]
    managers = ["dc", "ap"]
    apps = ["media-microsvc", "hipster-shop", "train-ticket", "teastore"]
    workloads = ["alibaba", "burst", "exp", "fixed"]
    percentages = [0.5, 0.99]


    for resource in resources:
        for percentage in percentages:
            ap_vs_dc_slack_results = []
            static_vs_dc_slack_results = []
            for app in apps:
                for workload in workloads:
                    manageStats = ManageStatistics(app, "slack", resource, workload, -1, "no", percentage, ap_vs_dc_slack_results, static_vs_dc_slack_results)
                    manageStats.run_all()


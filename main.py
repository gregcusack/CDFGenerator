# Press Shift+F10 to execute it or replace it with your code.
# Press Double Shift to search everywhere for classes, files, tool windows, actions, and settings.

from append_files import ManageStatistics
import sys


# Press the green button in the gutter to run the script.
if __name__ == '__main__':
    if len(sys.argv) <= 3:
        print("ERROR: Need type, ratio, num_files args")
        sys.exit(-1)
    measurement = sys.argv[1]       # slack/throttles/ooms
    resource = sys.argv[2]          # cpu/mem
    load_type = sys.argv[3]         # static, exp, burst
    multiplier = 0
    if len(sys.argv) == 5:
        multiplier = int(sys.argv[4])


    manageStats = ManageStatistics(measurement, resource, load_type, multiplier)


    if multiplier != 0:
        if resource == "cpu":
            """ DC STUFF """
            manageStats.aggregate_per_period_to_per_second()
            manageStats.aggregate_into_one_file()

            """ STATIC """
            manageStats.remove_low_usage_containers_static()
            manageStats.aggregate_into_one_file_static()


        elif resource == "mem":
            manageStats.remove_low_usage_containers("dc")
            manageStats.aggregate_into_one_file_autopilot("dc")

            print("################################## DC Stuff DONE #################################")


            manageStats.remove_low_usage_containers("static")
            manageStats.aggregate_into_one_file_autopilot("static")

        manageStats.run_static()

    else:
        if resource == "cpu":
            """ DC STUFF """
            manageStats.aggregate_per_period_to_per_second()
            manageStats.aggregate_into_one_file()

            """ AUTOPILOT STUFF """
            manageStats.remove_low_usage_containers("ap")
            manageStats.aggregate_into_one_file_autopilot("ap")

        elif resource == "mem":
            manageStats.remove_low_usage_containers("dc")
            manageStats.aggregate_into_one_file_autopilot("dc")

            manageStats.remove_low_usage_containers("ap")
            manageStats.aggregate_into_one_file_autopilot("ap")

        """ PLOT """
        manageStats.run()

    # agg_file_folder = manageStats.aggregate_per_period_to_per_second_autopilot()
    # manageStats.aggregate_into_one_file_autopilot(agg_file_folder)

    # run(measurement, resource, load_type, duration, system)

# See PyCharm help at https://www.jetbrains.com/help/pycharm/

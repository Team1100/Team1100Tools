import csv
import json
import time
import threading
from networktables import NetworkTables
import argparse
from datetime import datetime
import matplotlib.pyplot as plt

date_str = datetime.now().strftime('%Y%m%d%H%M%S')

parser = argparse.ArgumentParser(description = 'Script to log data from robot. ')
parser.add_argument('-o', '--output-file', action='store', default=date_str + '_robot_data.csv', help='Name of file to use for writing collected data')
parser.add_argument('-i', '--input-file', action='store', default='robot_nt_names.json', help='List of names to query from NetworkTables and store in the output file')
parser.add_argument('-c', '--sample-count', action='store', default=1, help='Defines the number of samples collect before exiting')
parser.add_argument('-t', '--robot-team', action='store', default=1100, type=int, help='Robot team number')
parser.add_argument('-a', '--robot-ip', action='store', default=None, help='IP Address of the robot to connect to, e.x: 10.11.21.2 or 127.0.0.1')
parser.add_argument('-l', '--use-labels', action='store_true', help='Insert heading labels in the CSV output file')
parser.add_argument('-v', '--verbose', action='store_true', help='Print more information about what happens')
args = parser.parse_args()
print(args)

class RobotDataCollector(object):
    # TOP LEVEL INPUT FILE KEYWORDS
    TRIGGER_CMD = "triggerCommand"
    TABLES = "tables"
    GRAPHS = "graphs"
    # TABLE propery keywords
    TABLE_ELEMENT_NAME = "name"
    TABLE_ELEMENT_TYPE = "type"
    TABLE_ELEMENT_TYPE_BOOLEAN = "boolean"
    TABLE_ELEMENT_TYPE_DOUBLE = "double"
    # GRAPH propery keywords
    GRAPH_TITLE = "title"
    GRAPH_YLABEL = "ylabel"
    GRAPH_XLABEL = "xlabel"
    GRAPH_DATAX = "dataX"
    GRAPH_DATAY = "dataY"
    def __init__(self, parsed_args):
        self.args = parsed_args
        self.connectToNetworkTables()
        self.config = self.loadInputFile()
        if (self.args.verbose):
            print("Input:")
            print(self.config)
            print("")

    def loadInputFile(self):
        json_content = ""
        with open(self.args.input_file) as fp:
            json_content = json.load(fp)
        return json_content

    def connectToNetworkTables(self):
        cond = threading.Condition()
        notified = [False]

        def connectionListener(connected, info):
            print(info, '; Connected=%s' % connected)
            with cond:
                notified[0] = True
                cond.notify()

        # Decide whether to start using team number or IP address
        if self.args.robot_ip is None:
            NetworkTables.startClientTeam(self.args.robot_team)
        else:
            NetworkTables.initialize(server=self.args.robot_ip)

        NetworkTables.addConnectionListener(connectionListener, immediateNotify=True)

        with cond:
            print("Waiting")
            if not notified[0]:
                cond.wait()

        # Insert your processing code here
        print("Connected!")

    def waitForRobotEnabled(self):
        table = NetworkTables.getTable('Shuffleboard/Drive')
        robotTable = NetworkTables.getTable('Robot')
        robotEnabled = robotTable.getBoolean('enabled', False)

        print("Waiting for robot to be enabled")
                
        while not robotEnabled:
            time.sleep(1)
            robotEnabled = robotTable.getBoolean('enabled', False)

        print("Robot is enabled")

    def collectFieldNames(self):
        if not self.TABLES in self.config:
            print("No tables provided to collect data from.")
            exit(0)
        tables = self.config[self.TABLES]
        field_names = []

        for table_name in tables:
            nt_table = NetworkTables.getTable(table_name)
            # Collect each item from the table
            for entry in tables[table_name]:
                # Extract field name and add to list
                if not self.TABLE_ELEMENT_NAME in entry:
                    continue
                field_name = entry[self.TABLE_ELEMENT_NAME]
                field_names.append(field_name)
        return field_names

    def collectData(self):
        # Check that there are tables to collect data from
        if not self.TABLES in self.config:
            print("No tables provided to collect data from.")
            exit(0)
        tables = self.config[self.TABLES]
        samples = {}

        # Collect field names from input file
        field_names = self.collectFieldNames()
        # Open output file
        out_file = open(self.args.output_file, 'w')
        csv_writer = csv.DictWriter(out_file, fieldnames=field_names)
        csv_writer.writeheader()

        # While there are still samples to collect
        number_of_samples = 0
        while (number_of_samples < self.args.sample_count):
            csv_line = {}
            # For each table from the input file
            for table_name in tables:
                print("Collecting data from table " + table_name)
                nt_table = NetworkTables.getTable(table_name)
                # Collect each item from the table
                for entry in tables[table_name]:
                    # Extract sample name
                    if not self.TABLE_ELEMENT_NAME in entry:
                        continue
                    sample_name = entry[self.TABLE_ELEMENT_NAME]
                    # Extract sample type (default is double if not provided)
                    sample_type = self.TABLE_ELEMENT_TYPE_DOUBLE
                    if (self.TABLE_ELEMENT_TYPE in entry):
                        sample_type = entry[self.TABLE_ELEMENT_TYPE]
                    # Collect the sample
                    sample_value = None
                    if sample_name not in samples:
                        samples[sample_name] = []
                    if (sample_type == self.TABLE_ELEMENT_TYPE_DOUBLE):
                        sample_value = nt_table.getNumber(sample_name, 0)
                    elif (sample_type == self.TABLE_ELEMENT_TYPE_BOOLEAN):
                        sample_value = nt_table.getBoolean(sample_name, False)
                    else:
                        print("Unknown sample type {} for sample {}. Using None.".format(sample_type, sample_name))
                        sample_value = None
                    samples[sample_name].append(sample_value)
                    csv_line[sample_name] = sample_value
                    print("Collected sample {}={} from table {}".format(sample_name, sample_value, table_name))
            # Log an entry for the collected information in the csv file
            csv_writer.writerow(csv_line)

            #Increment sample count
            number_of_samples += 1
        # If there are graphs requested from the input file
        #   For each graph
        #       Generate a graph with matplotlib
        #       Save an image of the graph
        pass

data_collector = RobotDataCollector(args)
data_collector.collectData()

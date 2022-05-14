import os
import csv
import json
import time
import threading
from networktables import NetworkTables
import argparse
from datetime import datetime
import matplotlib.pyplot as plt

date_str = datetime.now().strftime('%Y%m%d%H%M%S')
COMMAND_MODE = "COMMAND_MODE"
COUNT_MODE = "COUNT_MODE"
TIME_MODE = "TIME_MODE"

parser = argparse.ArgumentParser(description = 'Script to log data from robot. ')
parser.add_argument('-d', '--output-directory', action='store', default='./', help='Name of directory to store the output file')
parser.add_argument('-o', '--output-file', action='store', default=date_str + '_robot_data.csv', help='Name of file to use for writing collected data')
parser.add_argument('-i', '--input-file', action='store', default='robot_nt_names.json', help='List of names to query from NetworkTables and store in the output file')
parser.add_argument('-m', '--sample-mode', action='store', choices=[COMMAND_MODE, COUNT_MODE, TIME_MODE], default=COUNT_MODE,
        help='Defines the samples collection mode. {} is indicates that a command will be executed and samples collected for the duration of the command. {} indicates that a specified sample count of samples will be collected. {} indicates that samples will be collected for a period of time.'.format(COMMAND_MODE, COUNT_MODE, TIME_MODE))
parser.add_argument('-c', '--sample-count', action='store', type=int, default=1, help='Defines the number of samples collect before exiting')
parser.add_argument('-t', '--robot-team', action='store', default=1100, type=int, help='Robot team number')
parser.add_argument('-a', '--robot-ip', action='store', default=None, help='IP Address of the robot to connect to, e.x: 10.11.21.2 or 127.0.0.1')
parser.add_argument('-l', '--no-labels', action='store_true', help='Do not insert heading labels in the CSV output file')
parser.add_argument('-v', '--verbose', action='store_true', help='Print more information about what happens')
args = parser.parse_args()
print(args)

class RobotDataCollector(object):
    # TOP LEVEL INPUT FILE KEYWORDS
    CONTROLS = "controls"
    TABLES = "tables"
    GRAPHS = "graphs"
    # CONTROLS property keywords
    CONTROL_ROBOT_ENABLED = "robotEnabled"
    CONTROL_TRIGGER_CMD = "triggerCommand"
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
    GRAPH_REQUIRED_LABELS = [GRAPH_TITLE, GRAPH_YLABEL, GRAPH_XLABEL,
                             GRAPH_DATAX, GRAPH_DATAY]
    def __init__(self, parsed_args):
        self.args = parsed_args
        self.connectToNetworkTables()
        self.config = self.loadInputFile()
        self.samples = {}
        self.field_names = []
        if (self.args.verbose):
            print("Input:")
            print(self.config)
            print("")
        self.verifyConfigControls()

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

    def verifyConfigControls(self):
        if not "controls" in self.config:
            raise Exception("Controls section missing from input file.")
        controls = self.config["controls"]
        if not self.CONTROL_ROBOT_ENABLED in controls:
            raise Exception("No network table entry identified for determining robot enable/disable state.")
        self.robotEnabledCtrl = controls[self.CONTROL_ROBOT_ENABLED]
        if not type(self.robotEnabledCtrl) is dict:
            raise Exception("The " + self.CONTROL_ROBOT_ENABLED + " entry MUST be a dictionary type in the json input file!")
        if not self.robotEnabledCtrl:
            raise Exception("Multiple " + self.CONTROL_ROBOT_ENABLED + " entries provided in json input file. Only one is supported!")
        if not self.CONTROL_TRIGGER_CMD in controls:
            raise Exception("No trigger command supplied.")
        self.triggerCommandCtrl = controls[self.CONTROL_TRIGGER_CMD]
        if not type(self.triggerCommandCtrl) is dict:
            raise Exception("The triggerCommand entry MUST be a dictionary type in the json input file!")
        # Verify that all control objects have a table name
        # and network tables table entry
        required_control_labels = ["table", "entry"]
        for control_name in self.config["controls"]:
            control_obj = self.config["controls"][control_name]
            for label in required_control_labels:
                if label not in control_obj:
                    raise Exception("The {} entry must have a dictionary entry for {} but none was found!".format(control_name, label))



    def waitForRobotEnabled(self):
        ctrlTable = NetworkTables.getTable(self.robotEnabledCtrl["table"])
        robotEnabled = ctrlTable.getBoolean(self.robotEnabledCtrl["entry"], False)

        print("Waiting for robot to be enabled")
                
        while not robotEnabled:
            time.sleep(1)
            robotEnabled = ctrlTable.getBoolean(self.robotEnabledCtrl["entry"], False)

        print("Robot is enabled")

    def startCommand(self):
        # Get trigger command from configuration file
        trigger_cmd = self.config["controls"][self.CONTROL_TRIGGER_CMD]
        # Get the table associated with the trigger cmd
        trigger_table = self.config["controls"]["table"]
        table = NetworkTables.getTable(trigger_table)
        # Query the running state of the trigger command.
        # Note that the trigger cmd should look something like this:
        # "DriveCompensatedDistance/DriveCompensatedDistance/running"
        table.putBoolean(trigger_cmd, True)

    def isCommandRunning(self):
        # Get trigger command from configuration file
        trigger_cmd = self.config["controls"][self.CONTROL_TRIGGER_CMD]
        # Get the table associated with the trigger cmd
        trigger_table = self.config["controls"]["table"]
        table = NetworkTables.getTable(trigger_table)
        # Query the running state of the trigger command.
        # Note that the trigger cmd should look something like this:
        # "DriveCompensatedDistance/DriveCompensatedDistance/running"
        cmd_current_state = table.getBoolean(trigger_cmd, False)
        return cmd_current_state

    def commandInitializeInputs(self):
        pass

    def commandInputDone(self):
        pass

    def commandIncrementInputs(self):
        pass

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
                field_short_name = field_name.split('/')[-1]
                field_names.append(field_short_name)
        return field_names

    def collectData(self):
        # Check that there are tables to collect data from
        if not self.TABLES in self.config:
            print("No tables provided to collect data from.")
            return

        samples = {}

        # Collect field names from input file
        field_names = self.collectFieldNames()
        self.field_names = field_names
        # Open output file
        output_filepath = os.path.join(self.args.output_directory, self.args.output_file)
        out_file = open(output_filepath, 'w')
        csv_writer = csv.DictWriter(out_file, fieldnames=field_names, dialect='unix')
        if not self.args.no_labels: # Write labels by default
            csv_writer.writeheader()

        number_of_samples = 0
        # Determine the requested mode and collect samples
        if (self.args.sample_mode == COUNT_MODE):
            # While there are still samples to collect
            while (number_of_samples < self.args.sample_count):
                # Collect a sample
                self.collectSample(samples, csv_writer)
                # Increment sample count
                number_of_samples += 1
        elif (self.args.sample_mode == COMMAND_MODE):
            # Initialize inputs
            self.commandInitializeInputs()
            # While not all inputs have reached their target
            while (not self.commandInputDone()):
                # Start the command
                self.startCommand()
                # While the command is still running
                while (self.isCommandRunning()):
                    # Collect a sample
                    self.collectSample(samples, csv_writer)
                    # Increment sample count
                    number_of_samples += 1
                # Increment inputs
                self.commandIncrementInputs()
            # Open and write a new file?
        elif (self.args.sample_mode == TIME_MODE):
            # Start the clock
            # While there is still time remaining
                # Collect a sample
                # Increment sample count
            pass
        self.samples = samples

    def collectSample(self, samples, csv_writer):
        tables = self.config[self.TABLES]
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
                sample_short_name = sample_name.split('/')[-1]
                if sample_short_name not in samples:
                    samples[sample_short_name] = []
                if (sample_type == self.TABLE_ELEMENT_TYPE_DOUBLE):
                    sample_value = nt_table.getNumber(sample_name, 0)
                elif (sample_type == self.TABLE_ELEMENT_TYPE_BOOLEAN):
                    sample_value = nt_table.getBoolean(sample_name, False)
                else:
                    print("Unknown sample type {} for sample {}. Using None.".format(sample_type, sample_name))
                    sample_value = None
                samples[sample_short_name].append(sample_value)
                csv_line[sample_short_name] = sample_value
                if self.args.verbose:
                    print("Collected sample {}={} from table {}".format(sample_name, sample_value, table_name))
        # Log an entry for the collected information in the csv file
        csv_writer.writerow(csv_line)

    def generateGraphs(self):
        # If there are graphs requested from the input file
        if not self.GRAPHS in self.config:
            print("No graphs to generate.")
            return

        if self.args.verbose:
            print("Generating graphs")

        graphs = self.config[self.GRAPHS]
        # For each graph
        for graph in graphs:
            # check that all lables exist for this graph
            if not self.doGraphLablesExist(graph):
                continue # skip this graph
            if self.args.verbose:
                print("Generating graph: {}".format(graph[self.GRAPH_TITLE]))
            # Graph x and y field names from the graph
            x_field_name = graph[self.GRAPH_DATAX].split('/')[-1]
            y_field_names = [ y.split('/')[-1] for y in graph[self.GRAPH_DATAY]]
            # Make sure X and Y sample values are present and valid
            if not self.doGraphFieldNamesExist(graph, x_field_name, y_field_names):
                continue # skip this graph
            # Generate a graph with matplotlib
            # Gather all of the lines for sorting
            graph_data = list(zip(self.samples[x_field_name], *[self.samples[y_name] for y_name in y_field_names]))
            graph_data.sort()
            # Pull the sorted data back out again
            x = [v[0] for v in graph_data]
            if self.args.verbose:
                print("X data: {}".format(x))
            yvals = []
            for i in range(len(y_field_names)):
                yvals.append([v[i+1] for v in graph_data])
            if self.args.verbose:
                print("Y data: {}".format(yvals))
            fig, ax = plt.subplots()
            lines = []
            # Graph each line on the plot
            for t in zip(y_field_names, yvals):
                data_label = t[0]
                y = t[1]
                if self.args.verbose:
                    print("Graphing yvalue {}".format(t))
                line, = ax.plot(x,y,label=data_label)
                lines.append(line)
            # Set graph properties
            ax.legend()
            ax.set_xlabel(graph[self.GRAPH_XLABEL])
            ax.set_ylabel(graph[self.GRAPH_YLABEL])
            ax.set_title(graph[self.GRAPH_TITLE])
            # Save an image of the graph
            img_file_name = self.args.output_file[0:-4] + "_" + graph[self.GRAPH_TITLE].replace(" ","_").lower() + ".png"
            img_file_path = os.path.join(self.args.output_directory, img_file_name)
            fig.savefig(img_file_path)

    def doGraphFieldNamesExist(self, graph, x_field_name, y_field_names):
        graph_title = graph[self.GRAPH_TITLE]
        if x_field_name not in self.samples:
            print("Field name {} for graph {} was not found in the samples collected. Skipping Graph.".format(x_field_name, graph_title))
            return False
        if len(y_field_names) == 0:
            print("There were no {} entries provided for graph {}. Skipping Graph.".format(self.GRAPH_DATAY, graph_title))
            return False
        for y_name in y_field_names:
            if y_name not in self.samples:
                print("Field name {} for graph {} was not found in the samples collected. Skipping Graph.".format(y_name, graph_title))
                return False
        return True

    def doGraphLablesExist(self, graph):
        graph_title = "no title"
        if self.GRAPH_TITLE in graph:
            graph_title = graph[self.GRAPH_TITLE]
        for label in self.GRAPH_REQUIRED_LABELS:
            if not label in graph:
                print("Label '{}' expected in graph '{}' but not found. Skipping graph.".format(label, graph_title))
                return False
        return True

data_collector = RobotDataCollector(args)
data_collector.waitForRobotEnabled()
data_collector.collectData()
data_collector.generateGraphs()

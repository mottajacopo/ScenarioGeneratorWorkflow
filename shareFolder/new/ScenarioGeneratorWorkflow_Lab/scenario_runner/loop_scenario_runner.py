import os
import sys
import subprocess

scenario = sys.argv[1]
directory = sys.argv[2]

for filename in os.listdir(directory):
    print(directory+filename)
    subprocess.Popen("python scenario_runner.py --openscenario {0}".format(directory+filename))
    os.system("python manual_control.py --scenario {0}".format(scenario))

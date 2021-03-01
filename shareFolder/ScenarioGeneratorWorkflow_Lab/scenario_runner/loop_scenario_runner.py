import os
import sys

directory = sys.argv[1]

for filename in os.listdir(directory):
    print(directory+filename)
    os.system("python scenario_runner.py --openscenario {0}".format(directory+filename))

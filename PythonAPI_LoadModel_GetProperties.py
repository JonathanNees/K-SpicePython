import kspice
from datetime import timedelta

project_path = "C:/K-Spice Test Projects/DemoProject"

timeline = "Tutorial"
mdlFile = "KSpiceTutorial Model"
prmFile = "KSpiceTutorial Model"
valFile = "KSpiceTutorial Model"

# instanciate the simulator object
sim = kspice.Simulator(project_path)

# open the project and load the timeline
tl = sim.activate_timeline(timeline)
tl.load(mdlFile, prmFile, valFile)

# initialize the timeline
tl.initialize()

# get all applications on the timeline
apps = tl.applications
print("Applications on the timeline:")
print(apps)

selected_app = tl.applications[0].name

# get all the names of the blocks on first application (Process Model)
block_names = tl.get_block_names(selected_app)
print("Blocks on the timeline:")
print(block_names)

# get all blocks (as objects) on the timeline
blocks = tl.get_blocks(selected_app, block_names)

# select all alarm transmitters and store them in new list
alarmTransmitters = []
print("Alarm transmitters on the timeline:")
for block in blocks:
    if block.type == "AlarmTransmitter":
        alarmTransmitters.append(block)
        print(block.name)

# for the first block, print all available variable names
print("Available variable names for the first alarm transmitter:")
print(alarmTransmitters[0].get_output_names())


# construct a list of variable names and units to be read, by using transmitter name and output variable "MeasuredValue"
varNames = []
for transmitter in alarmTransmitters:
    varNames.append(f"{transmitter.name}:MeasuredValue")
print("Variable names to be read:")
print(varNames)

# get values of measured values in SI units
values = tl.get_values(selected_app, varNames)
print("Initial values of measured values in SI units:")
print(values)

# close the inlet valve
tl.set_value(selected_app, "25ESV0001:LocalInput", False)

# set the execution speed of the timleine to 1000X real time
tl.set_speed(100)

# let the simulator run for a simulation duration of 10 minutes
duration = timedelta(minutes = 10)
tl.run_for(duration)

# get values of measured values in SI units
values = tl.get_values(selected_app, varNames)
print("Values of measured values in SI units, 10 minutes after closing the inlet valve:")
print(values)
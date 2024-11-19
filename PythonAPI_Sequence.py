import kspice
import csv
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
selected_app = tl.applications[0].name

# set the execution speed of the timleine to 1000X real time
tl.set_speed(20)

# create a list of variables to be recorded
variables = [["23LT0001:MeasuredValue","mm"],
            ["23LT0002:MeasuredValue","mm"], 
            ["23PT0001:MeasuredValue","barg"], 
            ["23PT0003:MeasuredValue","barg"], 
            ["25ESV0001:ValveStemPosition", "%"],
            ["23ESV0005:ValveStemPosition", "%"],
            ["23KA0001_m:Speed[0]", "rpm"],
            ["23PA0001_m:Speed[0]", "rpm"]]
samples = []


# create a state variable to control the sequence
state = 0

# run the simulator endlessly
while (True):

    match state:
        case 0: # initial state. 
            # Close the inlet valve 
            tl.set_value(selected_app, "25ESV0001:LocalInput", False)

            # wait for the inlet valve to close
            if tl.get_value(selected_app, "25ESV0001:IsDefinedClosed") == True:
                state = 1

        case 1: # inlet valve is closed. 
            # Close the outlet valve
            tl.set_value(selected_app, "23ESV0005:LocalInput", False)

            # wait for the outlet valve to close
            if tl.get_value(selected_app, "23ESV0005:IsDefinedClosed") == True:
                state = 2
        
        case 2: # inlet and outlet valve are closed.
            # Stop the pump
            tl.set_value(selected_app, "23KA0001_m:LocalInput", False)

            # wait for the pump to spin down
            if tl.get_value(selected_app, "23KA0001_m:Speed[0]") <= 10.0:
                state = 3
        
        case 3: # inlet and outlet valve are closed, pump is stopped
            # Stop the Compressor
            tl.set_value(selected_app, "23PA0001_m:LocalInput", False)

            # wait for the compressor to spin down
            if tl.get_value(selected_app, "23PA0001_m:Speed[0]") <= 10.0:
                break
    
    # step the simulator for 1 second
    tl.run_for(timedelta(seconds=1))
    sample = tl.get_values(selected_app, variables)
    sample.insert(0,tl.model_time.total_seconds())
    samples.append(sample)

# Write out data to CSV
with open("sample_data.csv", "w", newline="") as csvfile:
    writer = csv.writer(csvfile)
    header_row = variables.copy()
    header_row.insert(0,["ModelTime", "s"])
    writer.writerow(header_row)  # Write headers first
    writer.writerows(samples)
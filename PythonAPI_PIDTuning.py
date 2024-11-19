import kspice
from datetime import timedelta
import numpy as np
from scipy.integrate import simpson  # For numerical integration
import matplotlib.pyplot as plt


class PIDTuner:
    def __init__(self, process_data, setpoint, control_params, thresholds):
        """
        process_data: Tuple of time, sensor output from K-Spice (process time and response)
        setpoint: Desired setpoint for the control loop
        control_params: Initial PID control parameters (Kp, Ki, Kd)
        thresholds: Thresholds for IAE, ISE, and ITAE to trigger tuning (dict with 'iae', 'ise', 'itae' keys)
        """
        self.time, self.process_output = process_data
        self.setpoint = setpoint
        self.Kp, self.Ki, self.Kd = control_params
        self.thresholds = thresholds
        self.error = self.setpoint - self.process_output

    def calculate_iae(self):
        """Calculate Integral of Absolute Error (IAE)."""
        iae = simpson(np.abs(self.error), x=self.time)
        return iae

    def calculate_ise(self):
        """Calculate Integral of Square Error (ISE)."""
        ise = simpson(np.square(self.error), x=self.time)
        return ise

    def calculate_itae(self):
        """Calculate Integral of Time-weighted Absolute Error (ITAE)."""
        itae = simpson(self.time * np.abs(self.error), x=self.time)
        return itae

    def update_pid_params(self):
        """
        Adjust PID parameters based on error criteria and thresholds.
        """
        iae = self.calculate_iae()
        ise = self.calculate_ise()
        itae = self.calculate_itae()

        # Check if the error exceeds the thresholds and adjust parameters accordingly
        if iae > self.thresholds['iae']:
            self.Kp *= 1.1  # Increase proportional gain
            self.Ki *= 1.05  # Increase integral gain
            print(f"IAE {iae:.2f} exceeded threshold. Adjusting Kp and Ki.")

        if ise > self.thresholds['ise']:
            self.Kd *= 0.95  # Reduce derivative gain to stabilize oscillations
            print(f"ISE {ise:.2f} exceeded threshold. Adjusting Kd.")

        if itae > self.thresholds['itae']:
            self.Kp *= 0.95  # Slight reduction in proportional gain for smoother response
            print(f"ITAE {itae:.2f} exceeded threshold. Adjusting Kp.")

        return self.Kp, self.Ki, self.Kd

    def plot_response(self):
        """Plot the process response to visualize tuning."""
        plt.plot(self.time, self.process_output, label="Process Output")
        plt.plot(self.time, [self.setpoint] * len(self.time), 'r--', label="Setpoint")
        plt.xlabel("Time")
        plt.ylabel("Response")
        plt.legend()
        plt.show()

    def plot_response(self):
        """Plot the process response to visualize tuning."""
        plt.plot(self.time, self.process_output, label="Process Output")
        plt.plot(self.time, [self.setpoint] * len(self.time), 'r--', label="Setpoint")
        plt.xlabel("Time")
        plt.ylabel("Response")
        plt.legend()
        plt.show()

# Thresholds for tuning (define them based on your process requirements)
thresholds = {
    'iae': 10.0,  # Threshold for IAE
    'ise': 5.0,   # Threshold for ISE
    'itae': 20.0  # Threshold for ITAE
}

##############################################################################################
# Project settings

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
target_application = tl.applications[0].name
tl.set_speed(1000)

# duration for one optimization run
duration = timedelta(minutes=20)
samples = 20

# do n optimization iterations
n = 8
for  i in range(0,n) :
    # load initial condition
    tl.load_initial_condition(valFile)
    tl.initialize()

    # get the control parameters       
    Kp = tl.get_value(target_application, "23LIC002:Gain")
    Ki = tl.get_value(target_application, "23LIC002:IntegralTime")
    Kd = tl.get_value(target_application, "23LIC002:DerivativeTime")

    control_params = (Kp, Ki, Kd)
    print("The current PID parameters are: Kp = {:.2f}, Ki = {:.2f}, Kd = {:.2f}".format(*control_params))

    # set the controller setpoint
    tl.set_value(target_application, "23LIC002:InternalSetpoint", 500, "mm")

    time = np.linspace(0, duration.seconds, samples)

    process_feedback = []
    # get the value before running the simulation
    process_feedback.append(tl.get_value(target_application, "23LIC002:MeasuredValue", "mm"))
    # run the simulation for the specified duration and collect the values


    for j in range (1,samples):
        
        tl.run_for(duration/samples)
        process_feedback.append(tl.get_value(target_application, "23LIC002:MeasuredValue", "mm"))

    process_feedback = np.array(process_feedback)

    # Initialize the PID Tuner 
    tuner = PIDTuner((time, process_feedback), 500, control_params, thresholds)

    # calculate the new control parameters
    control_params = tuner.update_pid_params()
    # Print new PID parameters
    print("Updated PID parameters: Kp = {:.2f}, Ki = {:.2f}, Kd = {:.2f}".format(*control_params))

    # set the new control parameters
    tl.set_value(target_application, "23LIC002:Gain", control_params[0])
    tl.set_value(target_application, "23LIC002:IntegralTime", control_params[1])
    tl.set_value(target_application, "23LIC002:DerivativeTime", control_params[2])
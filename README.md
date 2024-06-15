# Feedback Control for a UAS

## Overview

The objective is to design a feedback control algorithm to stabilize the position of a UAS using a Proportional-Integral-Derivative (PID) controller. The project involves reading sensor data, performing coordinate transformations, calculating actuation commands, and sending these commands to the UAS to achieve a specified position.

## Project Structure

- **controller.py**: This Python script contains the implementation of the feedback control algorithm.
- **targets.csv**: A CSV file that provides a list of target positions for the UAS.
- **run.py**: The main script to run the simulation and controller. It initializes the environment, loads the target positions, and invokes the controller to stabilize the UAS at the desired positions.

## Aims

The primary aim is to create a simple feedback control algorithm for the position stabilization of a UAS. The project tasks include:

1. Reading data from a position/attitude/velocity feedback sensor.
2. Performing necessary coordinate transformations.
3. Calculating an actuation command.
4. Sending commands to the UAS to achieve the desired position.

## Components of PID Control

PID control, short for Proportional-Integral-Derivative control, is a feedback mechanism widely used in control systems to achieve desired performance by continuously adjusting inputs based on the error between a desired setpoint and a measured process variable.

- **Proportional (P) Term**: Provides an output proportional to the current error, helping to reduce steady-state error and improve responsiveness.
- **Integral (I) Term**: Accumulates the error over time and produces a response to eliminate any long-term steady-state error.
- **Derivative (D) Term**: Predicts future behavior of the error based on its rate of change, aiding in stabilizing the system and damping oscillations.

## Implementation Details

### Controller Implementation

The main tasks involve implementing a PID controller to stabilize the UAS in a 2D simulation environment. The controller reads the current position, velocity, and attitude of the UAS and outputs thrust commands to maintain the desired position.

### Simulation Environment

The project uses a custom simulator that provides the current state of the UAS and allows the input of thrust commands. The simulator includes options to introduce wind gusts, which add complexity to the control problem.

### Advanced Methods

While the primary focus is on PID control, the project also explores advanced control strategies such as:

- **Cascade Controllers**: Using multiple PID controllers in series to manage different update rates of sensors.
- **State Estimators**: To predict future states and improve control accuracy.
- **LQR Controllers**: Linear-Quadratic Regulator for optimal control.

## Usage

### Running the Controller

To run the controller, first, ensure that the `controller.py` script has been updated with any necessary changes. Then, use the `run.py` script to execute the simulation and controller.

1. **Modify `controller.py`**: Make any necessary changes to the PID control algorithm and other logic within the `controller.py` script.
2. **Update Configuration**: Modify the top lines of `controller.py` to indicate if wind is active:
    ```python
    wind_active = False  # Select whether you want to activate wind or not
    ```
3. **Run the Simulation**: Execute the `run.py` script to start the simulation and controller:
    ```bash
    python3 run.py
    ```

Ensure that the `targets.csv` file is in the same directory as `run.py` and `controller.py`. The `run.py` script will initialize the environment, load the target positions from `targets.csv`, and invoke the controller to stabilize the UAS at the desired positions.


### Testing and Evaluation

The controller will be tested by sending random desired positions to the UAS and measuring its performance in achieving and maintaining these positions. The performance will be evaluated based on positional error and consistency.

To evaluate the performance:

1. **Set Up the Environment**: Ensure the simulator is correctly installed and running. The environment should be configured to provide the current state of the UAS, including position, velocity, and attitude.
2. **Run the Controller**: Execute the `run.py` script. The script will read the current state from the simulator and output the necessary thrust commands to the UAS.
    ```bash
    python3 run.py
    ```
3. **Test with Random Positions**: The UAS will be commanded to move to random desired positions within a specified range. The simulator will provide feedback on the UAS's ability to reach and maintain these positions.
4. **Measure Performance**: Over multiple test runs, collect data on the positional error and the consistency of the UAS's performance. Calculate the average positional error and standard deviation to assess accuracy and stability.
5. **Advanced Testing**: Introduce wind gusts in the simulation environment to test the robustness of the controller. Evaluate the controller's performance in these more challenging conditions.


## Conclusion

This project highlights the importance of PID controllers and advanced control methods in ensuring the stability and accuracy of UAS operations. By dynamically regulating motor outputs using feedback, the PID controller helps maintain desired positions and orientations essential for effective drone functionality. Advanced strategies like cascade controllers and state estimators further enhance control precision and operational autonomy.

## Video Explanation

To better understand the implementation and tuning methodology, watch the following video explanation:

[![Feedback Control for a UAS](https://img.youtube.com/vi/7EzZIs0uMCM/0.jpg)](https://youtu.be/7EzZIs0uMCM)





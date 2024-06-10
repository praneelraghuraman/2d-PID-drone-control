# Settings for environmental interaction
wind_active = True  # Enable or disable wind effects
group_number = 5     # Identifier for the group or team

# Preset integral control accumulators for error integration
e_int_y = 0          # Integral of the y-axis position error
e_int_x = 0          # Integral of the x-axis position error
e_int_phi = 0        # Integral of the orientation error (phi)

def controller(state, target_pos, dt):
    """
    Purpose: Calculate the control signals for position and orientation based 
    on PID controllers.

    Args:
    state (list): Contains the current state [x, y, vx, vy, phi, phidot]
    target_pos (list): Desired position [x_des, y_des]
    dt (float): Time step for integral calculation

    Returns:
    tuple: Control signals for the motors (u1_clamped, u2_clamped)
    """
    # Unpack current state and target position
    x, y, vx, vy, phi, phidot = state
    x_des, y_des = target_pos

    # PID coefficients for y-axis control
    Kp_y = 63.5        # Proportional gain for y
    Ki_y = 62          # Integral gain for y
    Kd_y = 30          # Derivative gain for y

    # PID coefficients for x-axis control
    Kp_x = 0.1631        # Proportional gain for x
    Ki_x = 0.05607       # Integral gain for x
    Kd_x = 0.2345        # Derivative gain for x

    # PID coefficients for phi (orientation) control
    Kp_phi = 50      # Proportional gain for phi
    Ki_phi = 0.35     # Integral gain for phi
    Kd_phi = 20      # Derivative gain for phi
    
    # Calculate positional errors
    err_y = y - y_des
    err_x = x - x_des

    # Call the global integral accumulator variables
    global e_int_y, e_int_x, e_int_phi

    # Update integral accumulators with clamping to prevent windup
    e_int_y = min(max(e_int_y + err_y * dt, -0.15), 0.15)
    e_int_x = min(max(e_int_x + err_x * dt, -0.085),0.085)

    # Calculate target orientation (phi_c) based on x-axis control
    max_pitch_angle = 10 * (3.14159 / 180)  # Maximum pitch angle in radians
    phi_c = -1 * (Kd_x * vx + Kp_x * err_x + Ki_x * e_int_x)

    # Clamp the target orientation to the maximum pitch angle
    phi_c = min(max(phi_c, -max_pitch_angle), max_pitch_angle)

    # Update integral accumulator for the error in phi
    err_phi = phi - phi_c
    e_int_phi = min(max(e_int_phi + err_phi * dt, -0.15), 0.15)
            
    # Calculate forces needed based on PID outputs
    F =  (Kd_y * vy + Kp_y * err_y + Ki_y * e_int_y)

    # Calculate moments needed based on PID outputs for phi
    M = (Kd_phi * phidot + Kp_phi * err_phi + Ki_phi * e_int_phi)

    # Calculate motor commands with clamping to prevent actuator saturation
    u1 = (F - M)
    u2 = (F + M)
    u1_clamped = min(max(0, u1), 0.75)
    u2_clamped = min(max(0, u2), 0.75)
       
    # Return clamped motor commands
    #action = (u1_clamped, u2_clamped)
    #return action
    return u1_clamped, u2_clamped, err_x, err_y    

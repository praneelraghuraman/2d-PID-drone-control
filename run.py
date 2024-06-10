from src.environment import Environment
import controller
import pygame_gui
import pygame
import csv
import sys
import importlib
import pathlib
import matplotlib.pyplot as plt


targets = []
with open("targets.csv", "r") as file:
    csvreader = csv.reader(file)
    header = next(csvreader)
    for row in csvreader:
        if (
            float(row[0]) > 8
            or float(row[1]) > 8
            or float(row[0]) < 0
            or float(row[1]) < 0
        ):
            print(
                "WARNING: Target outside of environment bounds (0, 0) to (8, 8), not loading target"
            )
        else:
            targets.append((float(row[0]), float(row[1])))

environment = Environment(
    render_mode="human",
    render_path=True,
    screen_width=1000,
    ui_width=200,
    rand_dynamics_seed=controller.group_number,
    wind_active=controller.wind_active,
)

running = True
target_pos = targets[0]


theme_path = pathlib.Path("src/theme.json")
manager = pygame_gui.UIManager(
    (environment.screen_width, environment.screen_height), theme_path
)

reset_button = pygame_gui.elements.UIButton(
    relative_rect=pygame.Rect((800, 0), (200, 50)),
    text="Reset",
    manager=manager,
)

wind_button = pygame_gui.elements.UIButton(
    relative_rect=pygame.Rect((800, 50), (200, 50)),
    text="Toggle Wind",
    manager=manager,
)

target_label = pygame_gui.elements.UILabel(
    relative_rect=pygame.Rect((800, 700), (200, 50)),
    text="Target: " + str(target_pos),
    manager=manager,
)

prev_target_button = pygame_gui.elements.UIButton(
    relative_rect=pygame.Rect((800, 750), (100, 50)),
    text="Prev",
    manager=manager,
)

next_target_button = pygame_gui.elements.UIButton(
    relative_rect=pygame.Rect((900, 750), (100, 50)),
    text="Next",
    manager=manager,
)


def reload():
    # re importing the controller module without closing the program
    try:
        importlib.reload(controller)
        environment.reset(controller.group_number, controller.wind_active)

    except Exception as e:
        print("Error reloading controller.py")
        print(e)



#CHANGE len(unchecked_action) != x ..WHERE X IS LENGTH OF WHAT U ARE RETURNING
def check_action(unchecked_action):
    # Check if the action is a tuple or list and of length 2
    if isinstance(unchecked_action, (tuple, list)):
        if len(unchecked_action) != 4:
            print(
                "WARNING: Controller returned an action of length "
                + str(len(unchecked_action))
                + ", expected 2"
            )
            checked_action = (0, 0)
            pygame.quit()
            sys.exit()
        else:
            checked_action = unchecked_action

    else:
        print(
            "WARNING: Controller returned an action of type "
            + str(type(unchecked_action))
            + ", expected list or tuple"
        )
        checked_action = (0, 0)
        pygame.quit()
        sys.exit()

    return checked_action

#EDIT THIS PART BELOW=========================================================
error_x_list = []
error_y_list = []
time = 0
time_list = []
#END OF EDIT PART ABOVE=======================================================



#PLOTTING ON CLOSE BELOW================================================
# Create a figure and axis object for the plot
fig, ax = plt.subplots(figsize=(12, 6))

# Set up the plot
ax.set_xlabel('Time (s)')
ax.set_ylabel('Error (m)')

# Initialize an empty plot
ax.axhline(y=0, color='red', linestyle=':', label='Zero Error')
line_y, = ax.plot([], [], '-', label='Error in y')
line_x, = ax.plot([], [], '-', label='Error in x')
#PLOTTING ON CLOSE ABOVE================================================


# Game loop
while running:
    time_delta = environment.clock.tick(60) / 1000.0

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
            pygame.quit()
            sys.exit()
        if event.type == pygame_gui.UI_BUTTON_PRESSED:
            if event.ui_element == reset_button:
                reload()
            if event.ui_element == wind_button:
                environment.toggle_wind()
            if event.ui_element == prev_target_button:
                target_pos = targets[targets.index(target_pos) - 1]
                target_label.set_text("Target: " + str(target_pos))
            if event.ui_element == next_target_button:
                target_pos = targets[(targets.index(target_pos) + 1) % len(targets)]
                target_label.set_text("Target: " + str(target_pos))

        manager.process_events(event)

    # Get the state of the drone
    state = environment.drone.get_state()
    # Call the controller function
    action = check_action(controller.controller(state, target_pos, 1 / 60))
        
    environment.step(action)

    manager.update(time_delta)
    environment.render(manager, target_pos)
    
    #EDIT THIS PART BELOW======================================================
    #Add errors to list
    error_x = action[2] #Check location of error_x in function return
    error_y = action[3] #Check location of error_y in function return
    error_x_list.append(error_x)
    error_y_list.append(error_y)
    
    #Add time counter
    time += 1/60
    time_list.append(time)
    #EDIT THIS PART ABOVE=====================================================

    # # Live Plotting Below=====================================================
    # plt.clf()  # Clear the previous plot
    # plt.plot(time_list, error_y_list, linestyle='-',label='Error in y')
    # plt.plot(time_list, error_x_list, linestyle='-.',label='Error in x')
    # plt.xlabel("Time (s)")
    # plt.ylabel("Error (m)")
    # plt.legend()
    # plt.title("Live Plot")
    # plt.draw()
    # plt.pause(0.001)  # Pause to allow GUI interaction 
    
    # # Print error values in x and y against time
    # for t, error_x, error_y in zip(time_list, error_x_list, error_y_list):
    #     print(f"Time: {t:.2f} s, Error in x: {error_x:.2f} m, Error in y: {error_y:.2f} m")
    # # Live Plotting Above=====================================================
    
    # # Plotting on Close Below================================================
    # # Update the plot with new data
    # line_y.set_data(time_list, error_y_list)
    # line_x.set_data(time_list, error_x_list)

    # # Adjust plot limits if needed
    # ax.set_xlim(min(time_list), max(time_list))
    # ax.set_ylim(min([min(error_y_list),min(error_x_list)])-0.1, max([max(error_y_list),max(error_x_list)])+0.1)
    # #ax.set_ylim(-0.1,0.1)
    # ax.legend()
    # # Redraw the plot
    # #fig.canvas.draw()
    # plt.draw()
    
    # Optional: Stop the loop after a certain number of iterations
    if len(time_list) == 1200:
        pygame.quit()
        sys.exit()
    # Plotting on Close Above=================================================

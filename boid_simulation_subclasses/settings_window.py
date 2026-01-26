"""TODO: Header comment"""
# TODO: refactor apply codeblocks, too mcuh repeating

import tkinter as tk
from tkinter import ttk


# Ensures all left columns are consistent width, as a result the
# right columns are then all aligned.
MIN_WIDTH = 35

class SettingsWindow:
    def __init__(self, visualizer):
        # Reference to parent, needed to update changed parameters.
        self.visualizer = visualizer

        # Setup tkinter window for ui.
        self.ui_win = tk.Toplevel(visualizer.root, padx=20, pady=10)
        self.ui_win.title('Settings / User Interface')
        # self.ui_win.geometry("400x800")

        # Setup the configuration frames.
        self.create_boid_frame()
        self.create_pred_frame()
        self.create_agent_frame()
        self.create_tank_frame()
        self.create_stat_frame()

        # Ensures toggle button is triggered when window is closed with x.
        self.ui_win.protocol("WM_DELETE_WINDOW", self.visualizer.toggle_settings)
        # TODO error console?

    def create_frame_header(self, frame, title, btntext, btnfunc):
        """Creates label with frame title and a button to apply changes from corresponding
        frame."""
        label_header = tk.Label(frame, text=title, font=("TkDefaultFont", 14, 'bold'))
        label_header.grid(row=0, column=0, sticky='W', padx=(0,30))

        apply_button = tk.Button(frame, text=btntext, command=btnfunc)
        apply_button.grid(row=0, column=1, sticky='E')

    def create_input_row(self, frame, row, text, value):
        """Creates label with name of changed parameter and an tkinter entry widget for
        user input."""
        label = tk.Label(frame, text=text, width=MIN_WIDTH, anchor='w')
        label.grid(row=row, column=0, sticky='W')
        entry = tk.Entry(frame)
        entry.grid(row=row, column=1)
        entry.insert(0, value)
        return label, entry

    def add_splitter(self, frame, row):
        """Creates a horizontal line, placed in between frames to act as separator."""
        splitter = ttk.Separator(frame, orient='horizontal')
        splitter.grid(row=row, columnspan=2, sticky='WE', pady=10)

    def create_boid_frame(self):
        """Create confiuration frame for boids."""
        boid_frame = tk.Frame(self.ui_win)
        boid_frame.grid(row=0, column=0, sticky='EW', padx=0, pady=0)

        self.create_frame_header(boid_frame, title='Fish configuration:', btntext='Apply',
                                 btnfunc=self.apply_boid_changes)

        _, self.entry_turn_factor = self.create_input_row(boid_frame, row=1, text='turn factor:',
                                                          value=self.visualizer.sim.turn_factor)

        _, self.entry_visual_range = self.create_input_row(boid_frame, row=2, text='visual range:',
                                                           value=self.visualizer.sim.visual_range)

        _, self.entry_protected_range = self.create_input_row(boid_frame, row=3, text='protected range:',
                                                              value=self.visualizer.sim.protected_range)

        _, self.entry_centering_factor = self.create_input_row(boid_frame, row=4, text='centering factor:',
                                                               value=self.visualizer.sim.centering_factor)

        _, self.entry_avoid_factor = self.create_input_row(boid_frame, row=5, text='avoid factor:',
                                                           value=self.visualizer.sim.avoid_factor)

        _, self.entry_matching_factor = self.create_input_row(boid_frame, row=6, text='matching factor:',
                                                              value=self.visualizer.sim.matching_factor)

        _, self.entry_maxspeed = self.create_input_row(boid_frame, row=7, text='maximum speed:',
                                                       value=self.visualizer.sim.maxspeed)

        _, self.entry_minspeed = self.create_input_row(boid_frame, row=8, text='minimum speed:',
                                                       value=self.visualizer.sim.minspeed)

        _, self.entry_fieldofview = self.create_input_row(boid_frame, row=9, text='FOV (0-360):',
                                                          value=self.visualizer.sim.fieldofview_degrees)

        _, self.entry_front_weight = self.create_input_row(boid_frame, row=10, text='front weight:',
                                                           value=self.visualizer.sim.front_weight)

        _, self.entry_speed_control = self.create_input_row(boid_frame, row=11, text='speed control:',
                                                            value=self.visualizer.sim.speed_control)

        _, self.entry_turning_control = self.create_input_row(boid_frame, row=12, text='turning control:',
                                                              value=self.visualizer.sim.turning_control)

        _, self.entry_max_turn = self.create_input_row(boid_frame, row=13, text='max turn:',
                                                       value=self.visualizer.sim.max_turn)

        self.add_splitter(boid_frame, row=14)

    def apply_boid_changes(self):
        """Applies changes entered in the boid configuration frame. If input is invalid, it replaces it with the internal
        variable value, which is either the default or last put valid input. If input is too large or too small, it clips
        the value. See the README on min and max values for each parameter."""
        self.visualizer.sim.turn_factor = self.handle_input(self.entry_turn_factor, minval=10**-6, maxval=1,
                                                            type_func=float, fallback=self.visualizer.sim.turn_factor)

        self.visualizer.sim.visual_range = self.handle_input(self.entry_visual_range, minval=10**-6, maxval=10**6,
                                                             type_func=float, fallback=self.visualizer.sim.visual_range)

        self.visualizer.sim.protected_range = self.handle_input(self.entry_protected_range, minval=10**-6, maxval=10**6,
                                                                type_func=float, fallback=self.visualizer.sim.protected_range)

        self.visualizer.sim.centering_factor = self.handle_input(self.entry_centering_factor, minval=10**-6, maxval=1,
                                                                 type_func=float, fallback=self.visualizer.sim.centering_factor)

        self.visualizer.sim.avoid_factor = self.handle_input(self.entry_avoid_factor, minval=10**-6, maxval=1,
                                                             type_func=float, fallback=self.visualizer.sim.avoid_factor)

        self.visualizer.sim.matching_factor = self.handle_input(self.entry_matching_factor, minval=10**-6, maxval=1,
                                                                type_func=float, fallback=self.visualizer.sim.matching_factor)

        self.visualizer.sim.minspeed = self.handle_input(self.entry_minspeed, minval=10**-6, maxval=10**6,
                                                         type_func=float, fallback=self.visualizer.sim.minspeed)

        self.visualizer.sim.maxspeed = self.handle_input(self.entry_maxspeed, minval=self.visualizer.sim.minspeed,
                                                         maxval=10**6, type_func=float, fallback=self.visualizer.sim.maxspeed)

        self.visualizer.sim.fieldofview_degrees = self.handle_input(self.entry_fieldofview, minval=0, maxval=360,
                                                                type_func=float, fallback=self.visualizer.sim.fieldofview_degrees)
        self.visualizer.sim.edit_fov()  # Needed to recompute internal cosine from the input in degrees

        self.visualizer.sim.front_weight = self.handle_input(self.entry_front_weight, minval=10**-6, maxval=1,
                                                                type_func=float, fallback=self.visualizer.sim.front_weight)

        self.visualizer.sim.speed_control = self.handle_input(self.entry_speed_control, minval=10**-6, maxval=1,
                                                                type_func=float, fallback=self.visualizer.sim.speed_control)

        self.visualizer.sim.turning_control = self.handle_input(self.entry_turning_control, minval=10**-6, maxval=1,
                                                                type_func=float, fallback=self.visualizer.sim.turning_control)

        self.visualizer.sim.max_turn = self.handle_input(self.entry_max_turn, minval=10**-6, maxval=1,
                                                                type_func=float, fallback=self.visualizer.sim.max_turn)

    def create_pred_frame(self):
        pred_frame = tk.Frame(self.ui_win)
        pred_frame.grid(row=1, column=0, sticky='EW', padx=0, pady=0)

        self.create_frame_header(pred_frame, title='Predator configuration:', btntext='Apply',
                                 btnfunc=self.apply_pred_changes)

        _, self.entry_turn_factor_pred = self.create_input_row(pred_frame, row=1, text='turn factor:',
                                                          value=self.visualizer.sim.turn_factor_pred)
        
        _, self.entry_visual_range_pred = self.create_input_row(pred_frame, row=2, text='visual range:',
                                                           value=self.visualizer.sim.visual_range_pred)
    
        _, self.entry_predatory_range = self.create_input_row(pred_frame, row=3, text='predatory range:',
                                                       value=self.visualizer.sim.predatory_range)
        
        _, self.entry_eating_range = self.create_input_row(pred_frame, row=4, text='eating range:',
                                                       value=self.visualizer.sim.eating_range)
        
        _, self.entry_eating_duration = self.create_input_row(pred_frame, row=5, text='eating duration:',
                                                       value=self.visualizer.sim.eating_duration)

        _, self.entry_avoid_factor_pred = self.create_input_row(pred_frame, row=6, text='avoid factor (pred2pred):',
                                                           value=self.visualizer.sim.avoid_factor_pred)
        
        _, self.pred2fish_attraction = self.create_input_row(pred_frame, row=7, text='pred2fish attract factor:',
                                                           value=self.visualizer.sim.pred2fish_attraction)

        _, self.fish2pred_avoidance = self.create_input_row(pred_frame, row=8, text='fish2pred avoid factor:',
                                                           value=self.visualizer.sim.fish2pred_avoidance)

        _, self.entry_maxspeed_pred = self.create_input_row(pred_frame, row=9, text='maximum speed:',
                                                       value=self.visualizer.sim.maxspeed_pred)

        _, self.entry_minspeed_pred = self.create_input_row(pred_frame, row=10, text='minimum speed:',
                                                       value=self.visualizer.sim.minspeed_pred)
        
        self.add_splitter(pred_frame, row=14)

    def apply_pred_changes(self):
        """Applies changes entered in the tank configuration fields.""" 
        self.visualizer.sim.turn_factor_pred = self.handle_input(self.entry_turn_factor_pred, minval=10**-6, maxval=1,
                                                            type_func=float, fallback=self.visualizer.sim.turn_factor_pred)
        
        self.visualizer.sim.visual_range_pred = self.handle_input(self.entry_visual_range_pred, minval=0, maxval=10**6,
                                                            type_func=float, fallback=self.visualizer.sim.visual_range_pred)
    
        self.visualizer.sim.predatory_range = self.handle_input(self.entry_predatory_range, minval=0, maxval=10**6,
                                                            type_func=float, fallback=self.visualizer.sim.predatory_range)
        
        self.visualizer.sim.eating_range = self.handle_input(self.entry_eating_range, minval=0, maxval=10**6,
                                                            type_func=int, fallback=self.visualizer.sim.eating_range)
        
        self.visualizer.sim.eating_duration = self.handle_input(self.entry_eating_duration, minval=0, maxval=10**6,
                                                            type_func=int, fallback=self.visualizer.sim.eating_duration)

        self.visualizer.sim.avoid_factor_pred = self.handle_input(self.entry_avoid_factor_pred, minval=10**-6, maxval=1,
                                                            type_func=float, fallback=self.visualizer.sim.avoid_factor_pred)
        
        self.visualizer.sim.pred2fish_attraction = self.handle_input(self.pred2fish_attraction, minval=-1, maxval=1,
                                                            type_func=float, fallback=self.visualizer.sim.pred2fish_attraction)

        self.visualizer.sim.fish2pred_avoidance = self.handle_input(self.fish2pred_avoidance, minval=-1, maxval=1,
                                                            type_func=float, fallback=self.visualizer.sim.fish2pred_avoidance)

        self.visualizer.sim.minspeed_pred = self.handle_input(self.entry_minspeed_pred, minval=10**-6, maxval=10**6,
                                                            type_func=float, fallback=self.visualizer.sim.minspeed_pred)
        
        self.visualizer.sim.maxspeed_pred = self.handle_input(self.entry_maxspeed_pred, minval=self.visualizer.sim.minspeed_pred, 
                                                            maxval=10**6, type_func=float, fallback=self.visualizer.sim.maxspeed_pred)

    def create_tank_frame(self):
        """Create confiuration frame for the tank."""
        tank_frame = tk.Frame(self.ui_win)
        tank_frame.grid(row=2, column=0, sticky='EW', padx=0, pady=0)

        self.create_frame_header(tank_frame, title='Tank configuration:', btntext='Apply & Resize',
                                 btnfunc=self.apply_tank_changes)

        _, self.entry_width = self.create_input_row(tank_frame, row=1, text='width:',
                                                    value=self.visualizer.sim.width)

        _, self.entry_height = self.create_input_row(tank_frame, row=2, text='height:',
                                                     value=self.visualizer.sim.height)

        _, self.entry_margin = self.create_input_row(tank_frame, row=3, text='wall avoidance margin:',
                                                     value=self.visualizer.sim.margin)

        _, self.entry_delay = self.create_input_row(tank_frame, row=4, text='frame delay:',
                                                    value=self.visualizer.delay)

        self.add_splitter(tank_frame, row=6)


    def apply_tank_changes(self):
        """Applies changes entered in the tank configuration fields."""
        self.visualizer.sim.width = self.handle_input(self.entry_width, minval=60, maxval=4000,
                                                       type_func=int, fallback=self.visualizer.sim.width)

        self.visualizer.sim.height = self.handle_input(self.entry_height, minval=60, maxval=4000,
                                                       type_func=int, fallback=self.visualizer.sim.height)

        self.visualizer.sim.margin = self.handle_input(self.entry_margin, minval=1,
                                                       maxval=int(0.4*(max(self.visualizer.sim.height,
                                                                        self.visualizer.sim.width))),
                                                       type_func=int, fallback=self.visualizer.sim.margin)

        self.visualizer.resize()

        self.visualizer.delay = self.handle_input(self.entry_delay, minval=1, maxval=1000,
                                                  type_func=int, fallback=self.visualizer.delay)

    def create_agent_frame(self):
        """Create confiuration frame for agents."""
        agent_frame = tk.Frame(self.ui_win)
        agent_frame.grid(row=3, column=0, sticky='EW', padx=0, pady=0)

        self.create_frame_header(agent_frame, title='Agent configuration:', btntext='Apply',
                                 btnfunc=self.apply_agent_changes)

        _, self.entry_num_boids = self.create_input_row(agent_frame, row=1, text='number of boids:',
                                                        value=self.visualizer.sim.num_boids)
        
        _, self.entry_num_preds = self.create_input_row(agent_frame, row=2, text='number of predators:',
                                                        value=self.visualizer.sim.num_preds)

        _, self.entry_triangle_size = self.create_input_row(agent_frame, row=3, text='boid triangle size:',
                                                        value=self.visualizer.triangle_size)

        _, self.entry_pred_triangle_size = self.create_input_row(agent_frame, row=4, text='predator triangle size:',
                                                        value=self.visualizer.pred_triangle_size)

        self.add_splitter(agent_frame, row=5)

    def apply_agent_changes(self):
        """Applies changes entered in the agent configuration fields."""
        pass

        self.visualizer.sim.num_boids = self.handle_input(self.entry_num_boids, minval=1, maxval=10**5,
                                                          type_func=int, fallback=self.visualizer.sim.num_boids)
        self.visualizer.edit_boid_count()

        self.visualizer.sim.num_preds = self.handle_input(self.entry_num_preds, minval=0, maxval=10**5,
                                                          type_func=int, fallback=self.visualizer.sim.num_preds)
        self.visualizer.edit_pred_count()

        self.visualizer.triangle_size = self.handle_input(self.entry_triangle_size, minval=1, maxval=200,
                                                          type_func=int, fallback=self.visualizer.triangle_size)

        self.visualizer.pred_triangle_size = self.handle_input(self.entry_pred_triangle_size, minval=1, maxval=200,
                                                          type_func=int, fallback=self.visualizer.pred_triangle_size)

    def create_stat_frame(self):
        """Applies changes entered into the stat configuration field."""
        stat_frame = tk.Frame(self.ui_win)
        stat_frame.grid(row=4, column=0, sticky='EW', padx=0, pady=0)

        self.create_frame_header(stat_frame, title='Stat configuration:', btntext='Apply',
                                 btnfunc=self.apply_stat_changes)

        _, self.entry_xrange = self.create_input_row(stat_frame, row=1, text='x range:',
                                                        value=self.visualizer.stat_xrange)

        #self.add_splitter(stat_frame, row=2)

    def handle_boid_eaten(self):
        self.entry_num_boids.delete(0, tk.END)
        self.entry_num_boids.insert(0, self.visualizer.sim.num_boids)

    def apply_stat_changes(self):
        self.visualizer.stat_xrange = self.handle_input(self.entry_xrange, minval=10, maxval=10**5,
                                                          type_func=int, fallback=self.visualizer.stat_xrange)

        if self.visualizer and self.visualizer.stats_open:
            self.visualizer.stats.resize()

    def is_float(self, input):
        """Return true if input is float, else false."""
        try:
            input = float(input)
        except ValueError:
            return False
        return True

    def check_type(self, input, type_func):
        """Return true if input is float, else false."""
        try:
            input = type_func(input)
        except ValueError:
            return False
        return True

    def clip(self, input, minval, maxval):
        """Clip input between max and min values."""
        return max(minval, min(input, maxval))

    def read(self, input, minval, maxval, fallback):
        """Return clipped input as float if vallid, else return fallback (old parameter value)."""
        if not self.is_float(input):
            print(f"Rejected input: '{input}', using last valid value: '{fallback}'")
            return fallback
        input = float(input)
        return self.clip(input, minval, maxval)

    def handle_input(self, entry, minval, maxval, type_func, fallback):
        """TODO"""
        input = entry.get()
        if not self.check_type(input, type_func):
            print(f"Rejected input: '{input}', using last valid value: '{fallback}'")
            new_val = fallback
        else:
            input = type_func(input)
            new_val = self.clip(input, minval, maxval)

        entry.delete(0, tk.END)
        if type_func == int:
            entry.insert(0, f"{new_val}")
        else:
            entry.insert(0, f"{new_val:.6f}")

        return new_val

    def close(self):
        """Destroy window and dereference object."""
        self.ui_win.destroy()
        self.ui_win = None


if __name__ == "__main__":
    print("This file is not meant to be run directly. Refer to the README for details.")

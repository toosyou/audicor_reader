import re
import tkinter as tk
import matplotlib
matplotlib.use('TkAgg')
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure

import reader

class App:
    def __init__(self):
        self.tk_root = tk.Tk()
        self.tk_root.geometry('+300+100')
        self.tk_root.resizable(0, 0)

        self.signal, self.sampling_rates = reader.get_heart_sounds('./test.raw')
        print('reading finished!')

        self.signal_length = self.signal[0].shape[0] // self.sampling_rates[0] # in seconds

        # add signal figure
        self.time_interval = 10
        self.figure = Figure(figsize=(15, 12), dpi=100)
        self.canvas = FigureCanvasTkAgg(self.figure, master=self.tk_root)
        self.canvas.get_tk_widget().grid(row=0, columnspan=3)
        self.axes = None
        self.lines = None
        self.initial_plot()

        self.time_frame = tk.Frame(borderwidth=10)
        self.time_frame.grid(row=1, column=0, columnspan=8, sticky='NSWE')
        # add rescale button
        self.rescale_button = tk.Button(self.time_frame, width=5, text='Rescale', command=self.rescale_plot)
        self.rescale_button.pack(side=tk.LEFT, padx=5)

        # add slider bar for time
        self.time_slider = tk.Scale(self.time_frame,
                                    from_=0, to=self.signal_length-self.time_interval-1,
                                    resolution=5,
                                    length=1200,
                                    showvalue='no',
                                    orient='horizontal',
                                    command=self.time_slider_callback)
        self.time_slider.pack(side=tk.LEFT, padx=5)

        # add time input
        self.time_box_hour = tk.Entry(self.time_frame, validate='key', width=3, validatecommand=self.get_numerical_check(), justify=tk.RIGHT)
        self.time_box_min = tk.Entry(self.time_frame, validate='key', width=3, validatecommand=self.get_numerical_check(), justify=tk.RIGHT)
        self.time_box_sec = tk.Entry(self.time_frame, validate='key', width=3, validatecommand=self.get_numerical_check(), justify=tk.RIGHT)
        self.time_box_hour.pack(sid=tk.LEFT)
        tk.Label(self.time_frame, text=':', width=1).pack(sid=tk.LEFT)
        self.time_box_min.pack(sid=tk.LEFT)
        tk.Label(self.time_frame, text=':', width=1).pack(sid=tk.LEFT)
        self.time_box_sec.pack(sid=tk.LEFT)

    def rescale_plot(self):
        for ax in self.axes:
            ax.relim()
            ax.autoscale_view()
        self.canvas.draw()

    def get_numerical_check(self):
        def valid(action, index, value_if_allowed,
                           prior_value, text, validation_type, trigger_type, widget_name):
            return True if re.match(r'^[0-9]*$', value_if_allowed) else False

        return (self.tk_root.register(valid),
                '%d', '%i', '%P', '%s', '%S', '%v', '%V', '%W')

    def set_time_of_box(self, time_in_sec):
        self.time_box_hour.delete(0, tk.END)
        self.time_box_min.delete(0, tk.END)
        self.time_box_sec.delete(0, tk.END)
        self.time_box_hour.insert(0, str(time_in_sec // 60 // 60))
        self.time_box_min.insert(0, str((time_in_sec // 60) % 60))
        self.time_box_sec.insert(0, str(time_in_sec % 60))

    def time_slider_callback(self, time_in_sec):
        self.set_time_of_box(int(time_in_sec))
        self.update_plot(int(time_in_sec))

    def initial_plot(self):
        self.figure.clf()

        start_s = 0
        end_s = start_s + self.time_interval

        self.axes = list()
        self.lines = list()
        for index_channel, (channel_data, sampling_rate) in enumerate(zip(self.signal, self.sampling_rates)):
            ax = self.figure.add_subplot(self.signal.shape[0], 1, index_channel+1)

            channel_data = channel_data[ int(start_s*sampling_rate): int(end_s*sampling_rate)]
            line, = ax.plot(channel_data)
            ax.margins(x=0, y=0)
            self.lines.append(line)
            self.axes.append(ax)

        self.figure.tight_layout()
        self.canvas.draw()

    def update_plot(self, start_time):

        start_s = start_time
        end_s = start_s + self.time_interval

        for index_channel, (line, channel_data, sampling_rate) in enumerate(zip(self.lines, self.signal, self.sampling_rates)):
            channel_data = channel_data[ int(start_s*sampling_rate): int(end_s*sampling_rate)]
            line.set_ydata(channel_data)

        self.canvas.draw()

    def loop(self):
        self.tk_root.mainloop()

if __name__ == '__main__':
    App().loop()

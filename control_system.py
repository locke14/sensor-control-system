from cffi import FFI
import matplotlib.pyplot as plt
import threading
import queue
import numpy as np
import time

ffi = FFI()

# Load the shared library
lib = ffi.dlopen('./control_system.dll')

# Define the C functions that we want to use
ffi.cdef("""
    void* ControlSystem_new();
    void ControlSystem_run(void*, int);
    int ControlSystem_get_temperature(void*);
    int ControlSystem_get_pressure(void*);
""")

# Define the ControlSystem class and its methods
class ControlSystem:
    def __init__(self):
        self.obj = lib.ControlSystem_new()

    def run(self, num_iterations):
        lib.ControlSystem_run(self.obj, num_iterations)

    def get_temperature(self):
        return lib.ControlSystem_get_temperature(self.obj)

    def get_pressure(self):
        return lib.ControlSystem_get_pressure(self.obj)

# Create a ControlSystem object
cs = ControlSystem()

# Create an event to signal the threads to stop
stop_event = threading.Event()

# Run the control system in a separate thread
num_iterations = 1000
cs_thread = threading.Thread(target=cs.run, args=(num_iterations,))
cs_thread.start()

# Define a function to get sensor readings from the control system
def get_sensor_data(cs, stop_event):
    while not stop_event.is_set():
        temperature = cs.get_temperature()
        pressure = cs.get_pressure()
        sensor_data.put((temperature, pressure))
        time.sleep(0.1)


# Create a queue to hold sensor readings
sensor_data = queue.Queue()

# Get sensor readings in a separate thread
data_thread = threading.Thread(target=get_sensor_data, args=(cs, stop_event))
data_thread.start()

# Plot sensor readings in real-time
plt.figure()
temperature_data = []
pressure_data = []
for _ in range(num_iterations):
    try:
        temperature, pressure = sensor_data.get_nowait()
        temperature_data.append(temperature)
        pressure_data.append(pressure)
        plt.clf()
        plt.plot(temperature_data, label='Temperature')
        plt.plot(pressure_data, label='Pressure')
        plt.plot([0, num_iterations], [50, 50], 'k--', label='Temperature Setpoint')
        plt.plot([0, num_iterations], [2.5, 2.5], 'r--', label='Pressure Setpoint')
        plt.legend()
        plt.pause(0.01)
    except queue.Empty:
        continue

# Signal the threads to stop
stop_event.set()

# Wait for the threads to finish
cs_thread.join()
data_thread.join()

plt.show()

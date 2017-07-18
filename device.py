"""
This module represents a device.

Computer Systems Architecture Course
Assignment 1
March 2016
"""

# Ionita Costel-Cosmin, 335CC

from threading import Event, Thread, Lock

from barrier import Barrier
from ThreadPool import ThreadPool

class Device(object):
    """
    Class that represents a device.
    """

    def __init__(self, device_id, sensor_data, supervisor):
        """
        Constructor.
        @type device_id: Integer
        @param device_id: the unique id of this node; between 0 and N-1

        @type sensor_data: List of (Integer, Float)
        @param sensor_data: a list containing (location, data) as measured by this device

        @type supervisor: Supervisor
        @param supervisor: the testing infrastructure's control and validation component
        """
        self.device_id = device_id
        self.sensor_data = sensor_data
        self.supervisor = supervisor
        self.script_received = Event()
        self.scripts = []
        self.timepoint_done = Event()

        self.barrier = None
        self.location_locks = {location : Lock() for location in sensor_data}
        self.scripts_arrived = False

        self.thread = DeviceThread(self)
        self.thread.start()

    def __str__(self):
        """
        Pretty prints this device.

        @rtype: String
        @return: a string containing the id of this device
        """
        return "Device %d" % self.device_id

    def setup_devices(self, devices):
        """
        Setup the devices before simulation begins.

        @type devices: List of Device
        @param devices: list containing all devices
        """
        if self.device_id == 0:
            self.barrier = Barrier(len(devices))
            self.send_barrier(devices, self.barrier)

    @staticmethod
    def send_barrier(devices, barrier):
        """
        Spreads the barrier to all devices in the simulation

        @devices: the list of all the devices in the simulation
        @barrier: the barrier that needs to be spread
        """

        for device in devices:
            if device.device_id != 0:
                device.set_barrier(barrier)

    def set_barrier(self, barrier):
        """
        Sets the barrier on the device (setter)
        This method is called by the send_barrier method

        @barrier: the barrier that needs to be set
        """
        self.barrier = barrier

    def assign_script(self, script, location):
        """
        Provide a script for the device to execute.

        @type script: Script
        @param script: the script to execute from now on at each timepoint; None if the
        current timepoint has ended

        @type location: Integer
        @param location: the location for which the script is interested in
         """
        if script is not None:
            self.scripts.append((script, location))
            self.scripts_arrived = True
        else:
            self.timepoint_done.set()

    def get_data(self, location):
        """
        Returns the pollution value this device has for the given location.

        @type location: Integer
        @param location: a location for which obtain the data

        @rtype: Float
        @return: the pollution value
        """
        if location in self.sensor_data:
            self.location_locks[location].acquire()
            return self.sensor_data[location]
        else:
            return None

    def set_data(self, location, data):
        """
        Sets the pollution value stored by this device for the given location.

        @type location: Integer
        @param location: a location for which to set the data

        @type data: Float
        @param data: the pollution value
        """
        if location in self.sensor_data:
            self.sensor_data[location] = data
            self.location_locks[location].release()

    def shutdown(self):
        """
        Instructs the device to shutdown (terminate all threads). This method
        is invoked by the tester. This method must block until all the threads
        started by this device terminate.
        """
        self.thread.join()

class DeviceThread(Thread):
    """
    Class that implements the device's worker thread.
    """

    def __init__(self, device):
        """
        Constructor.

        @type device: Device
        @param device: the device which owns this thread
        """
        Thread.__init__(self, name="Device Thread %d" % device.device_id)
        self.device = device

        self.thread_pool = ThreadPool(8)

    def run(self):

        self.thread_pool.set_device(self.device)

        while True:

            # get the current neighbourhood
            neighbours = self.device.supervisor.get_neighbours()
            if neighbours is None:
                break

            # stay in this loop until the timepoint ends
            while True:

                # if we already have scripts or the timepoint is finished
                if self.device.scripts_arrived or self.device.timepoint_done.wait():
                    if self.device.scripts_arrived:
                        self.device.scripts_arrived = False

                        # run scripts received until now
                        for (script, location) in self.device.scripts:
                            self.thread_pool.submit(neighbours, script, location)
                    else:
                        self.device.timepoint_done.clear()
                        self.device.scripts_arrived = True
                        break

            # wait for thread pool to finish it's job
            self.thread_pool.wait_threads()

            # wait for all devices to reach this point
            self.device.barrier.wait()

        # close all threads in the thread pool
        self.thread_pool.end_threads()

"""
This module implements a simple ThreadPool using a Queue for
storing tasks. Each task is a tuple of (neighbours, script, location)

When all the jobs need to be stopped, a dummy task is added into the
queue (None, None, None) which makes each worker thread to stop it's
execution

"""

# Ionita Costel-Cosmin, 335CC

from Queue import Queue
from threading import Thread

class ThreadPool(object):

    """
    This is the actual implementation of the ThreadPool
    """

    def __init__(self, threads_count):
        """
        Creates an object of type ThreadPool

        @threads_count: the number of worker threads
        """

        self.queue = Queue(threads_count)

        self.threads = []
        self.device = None

        self.create_workers(threads_count)
        self.start_workers()

    def create_workers(self, threads_count):
        """"
        Creates a list of worker threads

        @threads_count: the number of worker threads
        """

        for _ in xrange(threads_count):
            new_thread = Thread(target=self.execute)
            self.threads.append(new_thread)

    def start_workers(self):
        """
        Starts all workers in the pool
        """

        for thread in self.threads:
            thread.start()

    def set_device(self, device):
        """
        Sets the device on the ThreadPool (setter)

        @device: the device that needs to be set
        """
        self.device = device

    def execute(self):
        """
        This is the logic of each worker thread. It waits for
        a new task from the queue and then it executes it.
        """

        while True:

            neighbours, script, location = self.queue.get()

            if neighbours is None and script is None:
                self.queue.task_done()
                return

            self.run_script(neighbours, script, location)
            self.queue.task_done()

    def run_script(self, neighbours, script, location):
        """
        Runs the actual script (get data, run script, set data)

        @neigbours: the devices around the current device (on current timepoint)
        @script: the script that needs to be run
        @location: the location associated with the script
        """

        script_data = []

        # collect data from current neighbours
        for device in neighbours:
            if device.device_id != self.device.device_id:
                data = device.get_data(location)
                if data is not None:
                    script_data.append(data)

        # add our data, if any
        data = self.device.get_data(location)
        if data is not None:
            script_data.append(data)

        if script_data != []:
            # run script on data
            result = script.run(script_data)

            # update data of neighbours
            for device in neighbours:
                if device.device_id != self.device.device_id:
                    device.set_data(location, result)

            # update our data
            self.device.set_data(location, result)

    def submit(self, neighbours, script, location):
        """
        Inserts a new task into the queue

        @neighbours: the devices around the current device
        @script: the script that needs to be run
        @location: the location associated with the script
        """

        self.queue.put((neighbours, script, location))

    def wait_threads(self):
        """
        Waits for all the worker threads to finish their job
        """

        self.queue.join()

    def end_threads(self):
        """
        Terminates all the threads in the threadpool by
        submitting a dummy task (the workers know that when
        this task is submitted, then they need to stop
        """

        self.wait_threads()

        for _ in xrange(len(self.threads)):
            self.submit(None, None, None)

        for thread in self.threads:
            thread.join()

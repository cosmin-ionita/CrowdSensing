"""
This module implements a simple barrier made using
the Condition variable
"""

# Ionita Costel-Cosmin, 335CC

from threading import Condition

class Barrier(object):
    """
    This is the actual implementation of the Barrier
    """

    def __init__(self, num_threads):
        """
        Creates a new object of type Barrier

        @num_threads: the length of the barrier
        """

        self.num_threads = num_threads
        self.count_threads = self.num_threads
        self.cond = Condition()

    def wait(self):
        """
        Blocks until num_threads reach the calling point
        """

        self.cond.acquire()
        self.count_threads -= 1

        if self.count_threads == 0:
            self.cond.notify_all()
            self.count_threads = self.num_threads
        else:
            self.cond.wait()

        self.cond.release()

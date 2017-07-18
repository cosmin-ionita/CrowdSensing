# CrowdSensing
This project is a simulation of a CrowdSensing system that analyzes the noise reduction on a wide area

## Purpose

This project is an University assignment for the Computer Architecture course. It's main purpose is to simulate a set of real devices
(mobile devices - phones) that exchange data in a synchronized way.

More exactly, this infrastructure can be used for noise mapping - the mobile phones record the outside noise, exchange that
information between them and finally sends it to a central process which actually generates the map.

## Implementation

The entire system works as follows: devices are moving continuously and they get information about the location they were, in each
moment. When devices are close to each other (when they meet), they exchange information only if they have something to share (for 
example if device 1 has some data that device 2 is interested in. That information is called "script", which is a simulation of a 
light workload.

Each device has a number of cores on it's processor (8, more exactly), so if it meets a lot of devices that contains "interesting"
scripts, it has to get that scripts and to execute them as fast as it can (in parallel). That execution is performed using a 
ThreadPool, which contains a Queue of tasks that the device uses to execute the scripts concurrently. The ThreadPool has also a
number of workers (actually 8) that are waiting for some tasks to be entered in the queue in order to execute them.

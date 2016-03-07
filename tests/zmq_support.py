""" Simple script to support zmq testing out of process. Open a
publisher socket, write a value to it every second.
"""

import zmq
import time

context = zmq.Context()
socket = context.socket(zmq.PUB)
port = "6545"
print("Setup zmq publisher on port %s" % port)
socket.bind("tcp://*:%s" % port)

topic = "temperatures_and_power"

power_simulate = 1
ltemp_simulate = 10
max_iterations = 1000000
sleep_interval = 0.1

while power_simulate < max_iterations:

    str_mesg = ("%s 1,%s,%s" % (topic, ltemp_simulate, power_simulate))

    print "Send %s" % str_mesg
    socket.send(str_mesg)
    power_simulate += 1
    ltemp_simulate += 1

    time.sleep(sleep_interval)


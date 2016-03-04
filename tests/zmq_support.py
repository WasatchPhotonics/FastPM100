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

count = 1
max_iterations = 1000000
sleep_interval = 0.1
while count < max_iterations:

    str_mesg = ("%s 1,2,%s" % (topic, count))
    print "Send %s" % str_mesg
    socket.send(str_mesg)
    count += 1

    time.sleep(sleep_interval)


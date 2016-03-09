""" Simple script to support zmq testing out of process. Open a
publisher socket, write a value to it every second.
"""

import zmq
import time
import random

context = zmq.Context()
socket = context.socket(zmq.PUB)
port = "6545"
print("Setup zmq publisher on port %s" % port)
socket.bind("tcp://*:%s" % port)

topic = "temperatures_and_power"

power_simulate = 1
ltemp_simulate = 100
max_iterations = 1000000
sleep_interval = 0.01

ccd_temp = 32.00
laser_temp = 35.00
laser_power = 60.00
yellow_t = 22.00
blue_t = 25.00
amps = 3560
while power_simulate < max_iterations:

    # First generation laser temp and power only
    #str_mesg = ("%s 1,%s,%s" % (topic, ltemp_simulate, power_simulate))

    # All six values
    str_mesg = ("%s %s,%s,%s,%s,%s,%s" \
                % (topic, ccd_temp, laser_temp, laser_power,
                          yellow_t, blue_t, amps
                  )
               )
    print "Send %s" % str_mesg
    socket.send(str_mesg)
    power_simulate += 1
    ltemp_simulate += 1

    toggle = random.uniform(0.1, 0.9)
    if toggle >= 0.5:
        ccd_temp += random.uniform(0.1, 0.9)
        laser_temp += random.uniform(0.1, 0.9)
        laser_power += random.uniform(0.1, 0.9)
        yellow_t += random.uniform(0.1, 0.9)
        blue_t += random.uniform(0.1, 0.9)
        amps += random.uniform(0.1, 0.9)
    else:
        ccd_temp -= random.uniform(0.1, 0.9)
        laser_temp -= random.uniform(0.1, 0.9)
        laser_power -= random.uniform(0.1, 0.9)
        yellow_t -= random.uniform(0.1, 0.9)
        blue_t -= random.uniform(0.1, 0.9)
        amps -= random.uniform(0.1, 0.9)


    time.sleep(sleep_interval)


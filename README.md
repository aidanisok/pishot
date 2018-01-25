# pishot
HTTP Raspberry Pi Camera Snapshot Service

Edit the rc.local to file to launch the boot.sh file on system boot.

<code>sudo nano /etc/rc.local</code>

<code>/home/pi/pishot/boot.sh &</code>

Before powering on the Raspberry Pi ensure that the HDMI and Ethernet are plugged in, and the HDMI input device is powered on and is emitting video signal before powering on the Raspberry Pi by plugging in the MicroUSB.

To view a base64 representation of the HDMI inputs current frame navigate to:
<code>http://PI_IP:8082/current_frame.base64</code>

To get a visual representation of the HDMI inputs current frame in a browser navigate to:
<code>http://PI_IP:8032/current.html</code>


24th Jan, 2018, TODO: This service sometimes crashes when spammed and on crash needs restart as does not close HTTP port.

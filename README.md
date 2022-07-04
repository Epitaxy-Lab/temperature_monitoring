# Temperature Monitoring

This project in its current state serves to read and display the reading from a Williamson
pyrometer, pointed at an MBE sample stage. Pyrometer outputs an analog signal between 4 and 
20mA, and this code converts the signal into a temperature and displays it on a GUI.

Legacy code in `laser_control.py` also exists for the control of a Coherent laser based on 
this temperature reading, however this has  not been fully tested to due additional calibration
needed regarding the laser's heating curves.

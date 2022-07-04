import tkinter as tk
import tkinter.font as tkfont
from datetime import datetime
from utilities import *
from constants import *
import Adafruit_ADS1x15, os, socket


class Rack_GUI():
    '''
    Class to encompass the GUI components of the Ozone Controller
    '''
    def __init__(self, root, other):
        '''
        Creates GUI and relevant control scheme for Ozone control

        :param ion_com: serial connection to the ion gauge
        :param leak_com: serial connection to the leak valve
        '''
        self.root = root
        self.CRLR = other

        self.init_fonts()
        
        self.lbl_frame = tk.Frame(self.root)
        self.lbl_frame.config(bg=BG_COLOR)
        
        self.text_read_temp = tk.Label(self.lbl_frame, text="Current Temperature", font=self.txt_font)
        self.lbl_read_temp = tk.Label(self.lbl_frame, text="100C", bg="black", fg="white", font = self.reading_font)
        
        self.text_read_temp.pack(side=tk.TOP, pady = top_el_padding)
        self.lbl_read_temp.pack(side=tk.TOP, pady  = bottom_el_padding)


        self.lbl_frame.pack()

    def init_fonts(self):
        '''
        Initializes consistent fonts for GUI usage.
        '''
        self.txt_font = tkfont.Font(family="Helvetica", size=20)
        self.reading_font = tkfont.Font(family="Helvetica", size=36)
        
 
    def create_numpad(self, entry_widget):
        '''
        Creates a GUI numpad allowing the user to type with a touch screen

        :param entry_widget: the widget you would like to write to with this numpad
        '''
        if(self.numpad != None):
            self.numpad.destroy()
        self.numpad = tk.Toplevel(self.root)
        self.numpad.overrideredirect(True)

        title_bar = tk.Frame(self.numpad, bg="black", relief="raised", bd=2)
        close_button = tk.Button(title_bar, width=15, height=2, bg="red", text="X", command=self.numpad.destroy)
        title_bar.grid(row=0, column=2)
        close_button.pack()

        self.numpad.wm_title("Numpad")
        digits = ['7', '8', '9', '4', '5', '6', '1', '2', '3', '0', '.', '⌫']

        for i, b in enumerate(digits):
            cmd = lambda bu=b: self.type_in(entry_widget, bu)
            self.numpad.b = tk.Button(self.numpad, text=str(b), font=self.num_font, width=8, height=2, command = cmd).grid(row = int(i / 3) + 1, column = i % 3)

    def type_in(self, entry_widget, item):
        '''
        Allows numpad to act
        '''
        entry_widget.insert("end", item) if item != "⌫" else entry_widget.delete(0, "end")

class Laser_Operation():
    '''
    Full GUI and control operations for Ozone flow.
    '''
    def __init__(self, root):
        '''
        Sets up ozone control software. Initializes a GUI and stores it, as well as sets up default control parameters.

        :param ion_com: serial connection to the ion gauge
        :param leak_com: serial connection to the leak valve
        '''
        self.root = root
        self.GUI = Rack_GUI(root, self)
        
        
        #self.connect_laser()
        
        self.temp_rdr = Adafruit_ADS1x15.ADS1115() 

        self.ctrl_loop = None
        self.duty_cycle = 0
        self.freq = DEFAULT_FREQ
        self.temp = 200

        self.scale = (MAX_TEMP - MIN_TEMP) / (MAX_CURRENT - MIN_CURRENT)
        self.offset = -MIN_CURRENT * (MAX_TEMP - MIN_TEMP) / (MAX_CURRENT - MIN_CURRENT ) + 200

        # (2200 - 200) / (20 - 4) --> (2000) / (16)
        # -4 * (2200 - 200) / (20 - 4) + 200

        ## 8 -> 1000 - 500 + 200 --> 700C

        self.update_temperature()
    
    def connect_laser(self):
        self.lasr = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.lasr.connect((LASER_IP, LASER_PORT))
        self.lasr.settimeout(None)
        print('laser connected successfully')

    def update_temperature(self):
        '''
        Updates the current temperature reading.
        '''
        adc_val = self.temp_rdr.read_adc(0, gain=2)
        self.temp = (adc_val * 6.22e-4) * self.scale + self.offset

        self.GUI.lbl_read_temp['text'] = round(self.temp, 2)
        self.GUI.lbl_read_dc['text'] = round(self.duty_cycle, 2)
        '''
        self.lasr.send("glp \n\r".encode())
        pwr = self.lasr.recv(1024).strip()
        self.GUI.lbl_read_power['text'] = pwr
        '''
        self.root.after(500, self.update_temperature);

    def stop_heating(self):
        '''
        Gradually shuts off laser
        '''
        try:
            self.root.after_cancel(self.ctrl_loop)
        except:
            pass
        self.duty_cycle = 0
        self.lasr.send(SHUTTER_OFF)
        self.lasr.send(LASER_OFF)
        #self.lasr.close()
        '''
        if(self.duty_cycle > MIN_DUTY_CYCLE):
            self.duty_cycle -= 2
            self.laser_heat()
            self.root.after(15000, self.stop_heating)
        else:
            self.send(SHUTTER_OFF)
            self.send(LASER_OFF)
        ''' 
    
    
    def start_heating(self):
        '''
        Begins control process by initializing PID.
        '''
        self.lasr.send(SET_MOD_FREQUENCY(self.freq))
        resp = self.lasr.recv(1024)
        #print("Freq response: " + str(resp))

        self.data = ""

        set_temp = int(self.GUI.lbl_set_temp.get())
        ramp_time = int(self.GUI.lbl_set_ramp.get())
        sample_time = int(self.GUI.lbl_set_sample.get())

        if(self.ctrl_loop is not None):
            self.root.after_cancel(self.ctrl_loop)
            self.duty_cycle = DEFAULT_DC
            self.ctrl.target = set_temp
            self.ctrl.sample_time = sample_time
        else:
            self.duty_cycle = DEFAULT_DC
            self.ctrl = PID_ff(def_P, def_I, def_D, set_temp, sample_time, ramp_time)
            self.laser_heat()

        self.adjust_temperature()

    def laser_heat(self):
        '''
        Send laser command to heat to desired pulse width
        '''
        self.lasr.send(LASER_ENABLE)
        print("laser enabled: " + str(self.lasr.recv(1024)))
        # Open shutter and turn on laser
        self.lasr.send(SHUTTER_ON)
        shutter_resp = self.lasr.recv(1024)
        print("Shutter On Response: " + str(shutter_resp))
        self.lasr.send(LASER_ON)
        laser_resp = self.lasr.recv(1024)
        print("Laser ON Response: " + str(laser_resp))
        
    def laser_setting_update(self):
        # Set modulation strength
        self.lasr.send(SET_MOD_FREQUENCY(self.freq))
        freq_resp = self.lasr.recv(1024)
        print("Freq response: " + str(freq_resp))
        self.lasr.send(SET_MOD_STRENGTH(self.duty_cycle))
        mod_resp = self.lasr.recv(1024)
        print("Mod response: " + str(mod_resp))



    def adjust_temperature(self):
        '''
        Calibrate laser inputs to reach and maintain desired temperature
        '''
        curr_temp = self.temp
        temp_diff = calc_per_diff(curr_temp, self.ctrl.target)
#         print("DIFF: " + str(temp_diff))
#         print("Curr temp: " + str(curr_temp))
#         print("Target temp: " + str(self.ctrl.target))

        if(self.ctrl.ramping or abs(temp_diff) > convergence_bound):
            per_diff = self.ctrl.calc_percent_change(curr_temp)
            dc_adjustment = 1 + per_diff / 100
            new_dc = self.duty_cycle * dc_adjustment

            if(new_dc < MAX_DUTY_CYCLE):
                self.duty_cycle = new_dc
                self.laser_setting_update()
            else:
                print("DUTY CYCLE TOO HIGH")
        else:
            print("CONVERGED!")

        self.log_values(curr_temp)
        self.ctrl_loop = self.root.after(int(self.ctrl.sample_time * 1000), self.adjust_temperature)

    def log_values(self, curr_pressure):
        '''
        Logs data during heating.
        '''
        curr_time = datetime.now()
        curr_time = curr_time.strftime("%H:%M:%S")

        self.data += str(curr_time) + "," + str(self.temp) + "," + str(self.duty_cycle) + "\n"

def main():
    root = tk.Tk()
    root.geometry("800x480")
    root.config(bg=BG_COLOR)

    app = Laser_Operation(root)

    root.mainloop()

if __name__ == "__main__":
    main()

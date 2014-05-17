from Tkinter import *
import time, calendar
import threading, Queue
import SimpleHTTPServer, urlparse
import SocketServer


#global variable declarations

## Communication queue
exitFlag = 0

homename = "HOME"
homescore = 0
guestname = "GUEST"
guestscore = 0
time_elapsed = "0:00"
extra_text = ""
time_started = time.gmtime()
time_paused = time.gmtime() # not relevant as will be updated when timer actually paused
timer_paused = True
pause_iterations = 0 # see below for explanation
resolution = (1024, 576)

class server(threading.Thread):
    PORT = 8000
    def __init__(self,):
        threading.Thread.__init__(self)
    def run(self):
        print "Starting SERVER"
        Handler = MyHandler

        httpd = SocketServer.TCPServer(("", self.PORT), Handler)
        httpd.serve_forever()
        print "Exiting SERVER"

        
class MyHandler(SimpleHTTPServer.SimpleHTTPRequestHandler):
    def do_GET(self):
        qs = {}
        path = self.path
        if '?' in path:
            path, tmp = path.split('?', 1)
            qs = urlparse.parse_qs(tmp)
        print "Path: " + path
        dict_print = ""
        for key, value in qs.items():
            dict_print += "{} : {}".format(key, value) # for debug/log
            dict_print += "<br />"
            if key == "homename":
                set_home(value[0])
            if key == "guestname":
                set_guest(value[0])
            if key == "extra_text":
                set_extra_text(value[0])
            if key == "set_timer":
                set_timer(value[0])
            if key == "timer_toggle":
                if value[0] == "true":
                    timer_toggle()
            if key == "homescore":
                if value[0] == "add":
                    change_score(True, True)
                if value[0] == "take":
                    change_score(True, Ffalse)
            if key == "guestscore":
                if value[0] == "add":
                    change_score(False, True)
                if value[0] == "take":
                    change_score(False, False)
            
        print(dict_print)

        self.send_response(200, 'OK')
        self.send_header('Content-type', 'html')
        self.end_headers()
        html = "<html> <head><title> Hello World </title> </head> <body>you just changed " + dict_print + "</body> </html>"
        self.wfile.write(bytes(html))

    def log_request(self, code=None, size=None):
        print('Request')

    def log_message(self, format, *args):
        print('Message')

def update_clock():
	global time_elapsed
	global clock_update_id
	seconds_time = calendar.timegm(time.gmtime()) # now since epoch
	seconds_started = calendar.timegm(time_started)
	total_seconds_elapsed = seconds_time - seconds_started
	hours_elapsed = time.strftime("%H", time.gmtime(total_seconds_elapsed))
	minutes_elapsed = time.strftime("%M", time.gmtime(total_seconds_elapsed))
	seconds_elapsed = time.strftime("%S", time.gmtime(total_seconds_elapsed))
	time_elapsed = str(int(hours_elapsed) * 60 + int(minutes_elapsed)) + ":" + seconds_elapsed
	draw_video(time_elapsed, homename, guestname, homescore, guestscore, extra_text)
	clock_update_id = video.after(1000, update_clock)
	
def timer_toggle():
	global timer_paused
	if timer_paused:
		resume_timer()
	else:
		pause_timer()
		
def set_timer(minutes):
	global time_started
	if not minutes:
		minutes = 0
	seconds_time = calendar.timegm(time.gmtime()) # since epoch
	time_started = time.gmtime(seconds_time - (int(minutes) * 60))
	# toggle on/off to update display
	timer_toggle()
	timer_toggle()
	
def start_timer():
	global time_elapsed
	global time_started
	time_started = time.gmtime()
	update_clock()
	timer_paused = False

def pause_timer():
	global time_paused
	global timer_paused
	global pause_iterations
	time_paused = time.gmtime()
	timer_paused = True
	video.after_cancel(clock_update_id)
	if pause_iterations < 10: # after_cancel only works when id is set, not always the case (when clock just updated), therefore attempt 10 times over half a second.
		video.after(50, pause_timer)
		pause_iterations += 1
	else:
		pause_iterations = 0

def resume_timer():
	global pauser_counter_id
	global time_started
	global time_paused
	global timer_paused
	if timer_paused:
		# increase time started by time paused
		seconds_time = calendar.timegm(time.gmtime())
		seconds_started = calendar.timegm(time_started)
		seconds_paused = calendar.timegm(time_paused)
		seconds_started = seconds_started + (seconds_time - seconds_paused)
		time_started = time.gmtime(seconds_started)
		update_clock()
		timer_paused = False
	

def draw_video(time_elapsed, home, guest, hscore, gscore, extra_text):
        w.create_rectangle(0, 0, resolution[0], resolution[1], fill="#00ff00")

        text = time_elapsed + " | " + home + ": " + str(hscore) + " | " + guest + ": " + str(gscore) + " " + extra_text
        boxlength = int(len(text) * 6.9)
	w.create_rectangle(50, 25, (50 + boxlength), 50, fill="light blue", outline="light blue")
	w.create_text(60, 40, text=text, anchor="w")

def change_score(home, plus):
	global homescore
	global guestscore
	if plus:
		if home:
			homescore += 1
		else:
			guestscore += 1
	else:
		if home:
			homescore -= 1
		else:
			guestscore -= 1
	draw_video(time_elapsed, homename, guestname, homescore, guestscore, extra_text)
		
def set_guest(name):
	global guestname
	guestname = name
	draw_video(time_elapsed, homename, guestname, homescore, guestscore, extra_text)
	
def set_home(name):
	global homename
	homename = name
	draw_video(time_elapsed, homename, guestname, homescore, guestscore, extra_text)

def set_extra_text(text):
	global extra_text
	extra_text = text
	draw_video(time_elapsed, homename, guestname, homescore, guestscore, extra_text)
	
# Set Windows
video = Tk()
admin = Tk()

# Initialise Canvas
w = Canvas(video, width=resolution[0], height=resolution[1])
w.pack()

draw_video(time_elapsed, homename, guestname, homescore, guestscore, extra_text)

# Buttons
# Change Scores
buttons = Frame(admin)
b_home_plus = Button(admin, text="Home +", command=lambda: change_score(True, True))
b_home_minus = Button(admin, text="Home -", command=lambda: change_score(True, False))
b_guest_plus = Button(admin, text="Guest +", command=lambda: change_score(False, True))
b_guest_minus = Button(admin, text="Guest -", command=lambda: change_score(False, False))

b_home_plus.pack()
b_home_minus.pack()
b_guest_plus.pack()
b_guest_minus.pack()

# Team Names
team = Frame(admin)
e_hteam = Entry(admin)
b_set_hteam = Button(admin, text="Set Home", command=lambda: set_home(e_hteam.get()))
e_gteam = Entry(admin)
b_set_gteam = Button(admin, text="Set Guest", command=lambda: set_guest(e_gteam.get()))

e_hteam.pack()
b_set_hteam.pack()
e_gteam.pack()
b_set_gteam.pack()

#Timer
b_toggle_timer = Button(admin, text="Start/Pause Timer", command=lambda: timer_toggle())
e_timer_minutes = Entry(admin)
b_set_timer = Button(admin, text="Set Timer to Minute", command=lambda: set_timer(e_timer_minutes.get()))

b_toggle_timer.pack()
b_set_timer.pack()
e_timer_minutes.pack()

# Extra Text
e_extra_text = Entry(admin)
b_set_text = Button(admin, text="Set Extra Text", command=lambda: set_extra_text(e_extra_text.get()))

b_set_text.pack()
e_extra_text.pack()

#run

# Create new threads
serverThread = server()

# Start new Threads
serverThread.start()
mainloop()
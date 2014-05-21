from Tkinter import *
import time, calendar
import threading, Queue
import SimpleHTTPServer, urlparse
import SocketServer
import socket
import re



#global variable declarations
PORT = 8000
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
resolution = (1920, 1080)

class server(threading.Thread):
    def __init__(self,):
        threading.Thread.__init__(self)
    def run(self):
        print "Starting SERVER on " + str(PORT)
        Handler = MyHandler
        httpd = SocketServer.TCPServer(("", PORT), Handler)
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
        timer_set = ""
        dict_print = ""
        scorechanged = False
        for key, value in qs.items():
            dict_print += "{} : {}".format(key, value) # for debug/log
            dict_print += "\n"
            if key == "homename":
                set_home(value[0])
            if key == "guestname":
                set_guest(value[0])
            if key == "extratext":
                set_extra_text(value[0])
            if key == "set_timer":
                set_timer(value[0])
                set_timer(value[0])
                set_timer(value[0])
                set_timer(value[0])
                timer_set = value[0]
            if key == "timer_toggle":
                if value[0] == "true":
                    timer_toggle()
            if key == "homescore":
                if value[0] == "add":
                    change_score(True, True)
                if value[0] == "take":
                    change_score(True, False)
                scorechanged = True
            if key == "guestscore":
                if value[0] == "add":
                    change_score(False, True)
                if value[0] == "take":
                    change_score(False, False)
                scorechanged = True
                
        print(dict_print)

        self.send_response(200, 'OK')
        self.send_header('Content-type', 'text/html')
        self.end_headers()
        #html = "<html> <head><title> Hello World </title> </head> <body>you just changed " + dict_print + "</body> </html>"
        html = """
        <!doctype html>
        <html>
            <head>
                <meta charset="UTF-8">
                <meta name="viewport" content="width=device-width, initial-scale=1">
                <meta name="viewport" content="width=device-width, initial-scale=1, maximum-scale=1, user-scalable=no">
                <link rel="icon" href="data:;base64,=">
                <link rel="stylesheet" href="//netdna.bootstrapcdn.com/bootstrap/3.1.1/css/bootstrap.min.css">
                <link rel="stylesheet" href="//netdna.bootstrapcdn.com/bootstrap/3.1.1/css/bootstrap-theme.min.css">
                <script src="//netdna.bootstrapcdn.com/bootstrap/3.1.1/js/bootstrap.min.js"></script>
                <script src="//code.jquery.com/jquery-1.11.0.min.js"></script>
                <script src="//code.jquery.com/jquery-migrate-1.2.1.min.js"></script>
                <title>PiCG DEV by Nik</title>
            </head>
            <body style="width:95%;margin-left:auto;margin-right:auto;">
            <div class="page-header">
                <h1>PyScore <small> A Python Score Board</small></h1>
            </div>
            """
        if scorechanged:
            html+="""
            <div class="alert alert-success alert-dismissable">
                <button type="button" class="close" data-dismiss="alert-success" aria-hidden="true">&times;</button>
                <strong>Score changed!</strong> The new score is <strong>""" + str(homescore) + ":" + str(guestscore) + """</strong>
            </div>
            """
        
        html+="""
            <div style="width:80%;margin-left:auto;margin-right:auto;text-align:center;" }>
                <a class="btn btn-lg btn-default" href="?homescore=add">Home +</a>
                <a class="btn btn-lg btn-default" href="?homescore=take">Home -</a>
                <br /><br />
                <a class="btn btn-lg btn-default" href="?guestscore=add">Guest +</a>
                <a class="btn btn-lg btn-default" href="?guestscore=take">Guest -</a>
                <br /><br />
                <a class="btn btn-lg btn-default" href="?timer_toggle=true">Toggle Timer</a>
            
            <br /><br />
            <form class="form-horizontal" role="form" action="" method="GET" style="text-align:left;">
                <div class="form-group">
                  <label for="homename" class="col-sm-2 control-label">Home Name</label>
                  <div class="col-sm-10">
                    <input type="text" class="form-control" id="homename" name="homename" placeholder=""" + '"' + homename + '"' + """>
                  </div>
                </div>
                <div class="form-group">
                  <label for="guestname" class="col-sm-2 control-label">Guest Name</label>
                  <div class="col-sm-10">
                    <input type="text" class="form-control" id="guestname" name="guestname" placeholder=""" + '"' +  guestname + '"' + """>
                  </div>
                </div>
                <div class="form-group">
                  <label for="extratext" class="col-sm-2 control-label">Extra Text</label>
                  <div class="col-sm-10">
                    <input type="text" class="form-control" id="extratext" name="extratext" placeholder=""" + '"' +  extra_text + '"' + """>
                  </div>
                </div>
                <div class="form-group">
                  <div class="col-sm-offset-2 col-sm-10">
                    <button type="submit" class="btn btn-default">Submit</button>
                  </div>
                </div>
              </form>
              <form class="form-inline" role="form" action="/" method="get">
                <div class="form-group">
                  <label class="sr-only" for="minutes">Minutes</label>
                  <input type="number" class="form-control" id="minutes" name="set_timer" placeholder="Full Minutes" value=""" + '"' +  timer_set + '"' + """>
                </div>
                <button type="submit" class="btn btn-default">Set Timer</button>
              </form>
            </body>
            </div>
        </html>
        """
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
	boxlength = int(len(text) * 22)
	w.create_rectangle(100, 35, (50 + boxlength), 90, fill="light blue", outline="light blue")
	w.create_text(120, 60, font=("Nimbus Mono", 25, "bold"), text=text, anchor="w")
        
def draw_address():
	"""Draws the IP address in big font in the middle of the scren"""
	ip = [(s.connect(('8.8.8.8', 80)), s.getsockname()[0], s.close()) for s in [socket.socket(socket.AF_INET, socket.SOCK_DGRAM)]][0][1] # needs internet connections
	ip_pattern = re.compile("^(?:[0-9]{1,3}\.){3}[0-9]{1,3}$")
	if not (ip_pattern.search(ip) == None):
		w.create_text(20, (resolution[1]/2 - 20), font=("Consolas", 100, "bold"), text=(ip + ":" + str(PORT)), anchor="w")
	else:
		print "IP WRONG: " + ip
		w.create_text(20, (resolution[1]/2 - 20), font=("Consolas", 100, "bold"), text=(str(socket.gethostbyname(socket.gethostname())) + ":" + str(PORT)), anchor="w")

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
fw, fh = video.winfo_screenwidth(), video.winfo_screenheight()
video.overrideredirect(1)
video.geometry("%dx%d+0+0" % (fw, fh))
w.pack()

draw_video(time_elapsed, homename, guestname, homescore, guestscore, extra_text)
draw_address()

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

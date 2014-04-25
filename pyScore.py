from Tkinter import *

homename = "HOME"
homescore = 0
guestname = "GUEST"
guestscore = 0


def draw_scorebox(home, guest, hscore, gscore):
	w.create_rectangle(50, 25, 220, 50, fill="light blue", outline="light blue")
	w.create_text(60, 40, text=home + ": " + str(hscore) + " | " + guest + ": " + str(gscore), anchor="w")

def change_score(home, plus):
	print "CS"
	global homename
	global guestname
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
	draw_scorebox(homename, guestname, homescore, guestscore)
		
def set_guest(name):
	global homename
	global guestname
	global homescore
	global guestscore
	guestname = name
	draw_scorebox(homename, guestname, homescore, guestscore)
	
def set_home(name):
	global homename
	global guestname
	global homescore
	global guestscore
	homename = name
	draw_scorebox(homename, guestname, homescore, guestscore)
	
# Set Windows
video = Tk()
score = Tk()
teams = Tk()

#Initialise Canvas
w = Canvas(video, width=720, height=480)
w.pack()

w.create_line(0, 0, 200, 100)
w.create_line(0, 100, 200, 0, fill="red", dash=(4, 4))

w.create_rectangle(0, 0, 720, 480, fill="#00ff00")
w.create_rectangle(50, 25, 220, 50, fill="light blue", outline="light blue")
w.create_text(60, 40, text=homename + ": " + str(homescore) + " | " + guestname + ": " + str(guestscore), anchor="w")


# Buttons
# New 
buttons = Frame(score)
b_home_plus = Button(score, text="Home +", command=lambda: change_score(True, True))
b_home_minus = Button(score, text="Home -", command=lambda: change_score(True, False))
b_guest_plus = Button(score, text="Guest +", command=lambda: change_score(False, True))
b_guest_minus = Button(score, text="Guest -", command=lambda: change_score(False, False))

b_home_plus.pack()
b_home_minus.pack()
b_guest_plus.pack()
b_guest_minus.pack()

# Team Names
team = Frame(teams)
e_hteam = Entry(teams)
b_set_hteam = Button(teams, text="Set Home", command=lambda: set_home(e_hteam.get()))
e_gteam = Entry(teams)
b_set_gteam = Button(teams, text="Set Guest", command=lambda: set_guest(e_gteam.get()))

e_hteam.pack()
b_set_hteam.pack()
e_gteam.pack()
b_set_gteam.pack()

#run
mainloop()

import win32api
import win32con
import math
def start():
	win32api.mouse_event(win32con.MOUSEEVENTF_MOVE | win32con.MOUSEEVENTF_ABSOLUTE, int(960/1920*65535.0), int(540/1080*65535.0))

def setMouseByForce(force):
	delta = math.floor((960 - force)/50)

	win32api.mouse_event(win32con.MOUSEEVENTF_MOVE | win32con.MOUSEEVENTF_ABSOLUTE, int(delta/1920*65535.0), int(540/1080*65535.0))

start()

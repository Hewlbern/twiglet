"""Tiny Pi-side driver for the two TwigletEyes boards (Pi Zero 2W UART /dev/serial0, 115200).
Enable the UART: raspi-config -> Interface -> Serial: login shell NO, hardware YES.  pip install pyserial"""
import serial, time
class Eyes:
    def __init__(self, port="/dev/serial0", baud=115200):
        self.s = serial.Serial(port, baud, timeout=0.2)
    def cmd(self, line, side=None):
        self.s.write(((f"{side}:" if side else "") + line + "\n").encode())
        return self.s.readline().decode(errors="ignore").strip()     # reply comes from the L board only
    def expr(self, name): return self.cmd(f"EYE {name}")             # ring heart happy angry wide blink off test
    def look(self, x, y): return self.cmd(f"LOOK {x:.2f} {y:.2f}")   # -1..1, +x = robot's own left, +y = up
    def blink(self): return self.cmd("BLINK")
if __name__ == "__main__":
    e = Eyes(); print(e.cmd("PING"))
    for n in ("ring", "happy", "angry", "heart", "wide", "ring"):
        print(n, e.expr(n)); time.sleep(1.5)
    for x in (-1, 0, 1, 0): e.look(x, 0); time.sleep(0.6)
    e.blink()

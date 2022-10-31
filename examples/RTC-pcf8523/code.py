import busio
import adafruit_pcf8523
import time
import board
from adafruit_macropad import MacroPad

#This gets the RTC device on the stemma qt port
myI2C = busio.I2C(board.SCL, board.SDA)
rtc = adafruit_pcf8523.PCF8523(myI2C)

year = 2000
mon = 0
day = 1
hr = 6
min = 0

t = rtc.datetime
#print(t)     # uncomment for debugging
year = t.tm_year
mon = t.tm_mon
day = t.tm_mday
hr = t.tm_hour
min = t.tm_min

CLICKED = False
SAVE = False

state = ("Year", "Month", "Day", "Hour", "Minute")
mode_lines = ("^^^^/MM/DD HH:MM",
             "YYYY/^^/DD HH:MM",
             "YYYY/MM/^^ HH:MM",
             "YYYY/MM/DD ^^:MM",
             "YYYY/MM/DD HH:^^",
             "Save Date Time?",
             "----------------")
state_step = 0

macropad = MacroPad()

previous_position = macropad.encoder

text_lines = macropad.display_text()

text_lines[0].text = "%d/%02d/%02d %02d:%02d (%d)" % (year, mon+1, day, hr, min, state_step)
text_lines[1].text = mode_lines[state_step]
text_lines.show()

while True:
    time.sleep(0.2)
    if macropad.encoder_switch == True and CLICKED == False:
        state_step +=1
        state_step %= 7
        if state_step == 6:
            if SAVE == True:
                                     #year, mon,   date,  hour, min, sec, wday, yday, isdst
                t = time.struct_time((year, mon, day, hr,   min, 0,   0,    -1,   -1))
                rtc.datetime = t
                print()
                text_lines[2].text = "Saved"
            else:
                text_lines[2].text = "Not Saved"
            state_step=0
        text_lines[0].text = "%d/%02d/%02d %02d:%02d (%d)" % (year, mon+1, day, hr, min, state_step)
        text_lines[1].text = mode_lines[state_step]
        text_lines.show()
        CLICKED = True
    elif macropad.encoder_switch == False and CLICKED == True:
        CLICKED = False

    if previous_position != macropad.encoder:
        change = macropad.encoder - previous_position
        previous_position = macropad.encoder

        if state_step == 0:
            year += change
        elif state_step == 1:
            mon += change
            mon %= 12
        elif state_step == 2:
            day += change
            day %= 31
        elif state_step == 3:
            hr += change
            hr %= 24
        elif state_step == 4:
            min += change
            min %= 60
        if state_step == 5:
            if change < 0:
                SAVE = False
                text_lines[2].text = "No"
            else:
                SAVE = True
                text_lines[2].text = "Yes"
        text_lines[0].text = "%d/%02d/%02d %02d:%02d (%d)" % (year, mon+1, day, hr, min, state_step)
        text_lines.show()

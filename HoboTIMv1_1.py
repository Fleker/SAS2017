#Trying a git update
import time
import serial
import smbus


#########################################
# Initializing UART Port                #
# Parameters as close to -2 as possible #
#########################################

ser = serial.Serial(
	
	port = '/dev/ttyS0',
	baudrate = 9600,
	parity=serial.PARITY_NONE,
	stopbits=serial.STOPBITS_ONE,
	bytesize=serial.EIGHTBITS,
	timeout=.25
)



########################################
# Initializing I2C Bus
########################################

bus = smbus.SMBus(1)


TEMPHUMIDAddress = 0x40
EEPROMAddress = 0x50
LEDAddress = 0x67



#######################################
#Initialize LED States
#######################################
LED0 = 0b000000
LED1 = 0b000000
LED2 = 0b000000
LED3 = 0b000000
LED4 = 0b000000

bus.write_byte_data(LEDAddress, 0x06, 0x00)
bus.write_byte_data(LEDAddress, 0x07, 0x00)
bus.write_byte_data(LEDAddress, 0x08, 0x00)
bus.write_byte_data(LEDAddress, 0x09, 0x00)





#######################################
# Sensor/Actuator Functions
# These are specific to the sensors which are
# being utilized. Depending on your implementation
# you will need to adjust or completely change
# these functions.
#######################################

def TempRead():
	rawtemp = bus.read_word_data(TEMPHUMIDAddress, 0xE0)
	print rawtemp
	temp = (175.72*(rawtemp))/65536 - 46.85
	return temp


def HumidRead():
	rawhumid = bus.read_word_data(TEMPHUMIDAddress, 0xE5)
	print rawhumid
	humidity = (125*(rawhumid))/65536 - 6
	return humidity


def EEPROMSingleRead(AddressMSB, AddressLSB):
	bus.write_byte_data(EEPROMAddress, AddressMSB, AddressLSB)
	data = bus.read_byte(EEPROMAddress)
	return data

def EEPROMSingleWrite(AddressMSB, AddressLSB, Data):
	print Data
	status = bus.write_i2c_block_data(EEPROMAddress, AddressMSB, [AddressLSB, Data])
	return status

def LED(LEDNumber, Color):
	global LED0
	global LED1
	global LED2
	global LED3
	global LED4

	if LEDNumber == "0":
		LED0 = LEDColor(Color)
	elif LEDNumber == "1":
		print "changing led1"
		print "Color: "+Color
		LED1 = LEDColor(Color)
	elif LEDNumber == "2":
		LED2 = LEDColor(Color)
	elif LEDNumber == "3":
		LED3 = LEDColor(Color)
	elif LEDNumber == "4":
		LED4 = LEDColor(Color)
	else:
		print "Error with LED Number"
		return -1
	NewState = (0b00 << 30) + (LED4 << 24) + (LED3 << 18) + (LED2 << 12) + (LED1 << 6) + LED0
	LS0 = (NewState >> 0) & 0xFF
	LS1 = (NewState >> 8) & 0xFF
	LS2 = (NewState >> 16) & 0xFF
	LS3 = (NewState >> 24) & 0xFF
	bus.write_byte_data(LEDAddress, 0x06, LS0)
	bus.write_byte_data(LEDAddress, 0x07, LS1)
	bus.write_byte_data(LEDAddress, 0x08, LS2)
	bus.write_byte_data(LEDAddress, 0x09, LS3) 
	return "0"

_colors = {
    'red': 0b000001,
    'green': 0b000100,
    'blue': 0b010000,
    'purple': 0b010001,
    'white': 0b010101,
    'yellow': 0b000101,
    'cyan': 0b010100,
    'off': 0b000000
}
def LEDColor(Color):
    # Use a small lookup map of common colors 
    try:
        # Try to return user-input.
        return _colors[Color.lower()]
    except:
		print "Error with Color"
		return "-1"




#######################################
# Channel Definitions
# Each sensor will have its channel in
# which we can call upon its specific 
# function.
#######################################

def ChannelSelect(msg):
	print "MSG into Channel Select: "+str(msg)
	ChanID = msg[0].strip()
	print ChanID
	if ChanID == "001":
		print "Chan1 Read"
		data = TempRead()
	elif ChanID == "002":
		print "Chan2 Read"
		data = HumidRead()
	elif ChanID == "003":
		data = EEPROMSingleRead(int(msg[1],16),int(msg[2],16))		
	elif ChanID == "004":
		data = EEPROMSingleWrite(int(msg[1],16),int(msg[2],16),int(msg[3],16))
	elif ChanID == "005":
		data = LED("0",msg[1].strip())
	elif ChanID == "006":
		print msg[1]
		data = LED("1",msg[1].strip())
	elif ChanID == "007":
		data = LED("2",msg[1].strip())
	elif ChanID == "008":
		data = LED("3",msg[1].strip())
	elif ChanID == "009":
		data = LED("4",msg[1].strip())
	else:
		data = "Error"
	return data
		

 


#######################################
# TIM Functions
#######################################


		
while 1:
	msg = ser.readline()
	print "MSG: "+msg
	UARTData = msg.split(",")
	print "UARTData: "+str(UARTData)
	if UARTData[0] != '':
		UARTData.pop(0)
		print "Popped UARTData: "+str(UARTData)
		data = ChannelSelect(UARTData)
		ser.write(UARTData[0]+","+str(data))	

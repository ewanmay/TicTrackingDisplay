import glob
import sys
# import SerialStub as serial
import serial

def getAllSerialPorts():
    # Lists serial port names

    #     :raises EnvironmentError:
    #         On unsupported or unknown platforms
    #     :returns:
    #         A list of the serial ports available on the system
    # 
    if sys.platform.startswith('win'):
        ports = ['COM%s' % (i + 1) for i in range(32)]
    elif sys.platform.startswith('linux') or sys.platform.startswith('cygwin'):
        # this excludes your current terminal "/dev/tty"
        ports = glob.glob('/dev/tty[A-Za-z]*')
    elif sys.platform.startswith('darwin'):
        ports = glob.glob('/dev/tty.*')
    else:
        raise EnvironmentError('Unsupported platform')

    result = []
    for port in ports:
        try:
            s = serial.Serial(port)
            s.close()
            result.append(port)
        except (OSError, serial.SerialException):
            pass
    if len(result) == 0:
        return ["No Serial Ports Found"]
    else:
        return result
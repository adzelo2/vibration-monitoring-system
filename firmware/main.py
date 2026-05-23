import sys
import select
from machine import Pin, SPI
import time

# ============================================
# SPI CONFIG
# ============================================
spi = SPI(
    1,
    baudrate=1000000,
    polarity=0,
    phase=1,
    sck=Pin(18),
    mosi=Pin(23),
    miso=Pin(19)
)

cs = Pin(5, Pin.OUT)
drdy = Pin(4, Pin.IN)
cs.value(1)

# ============================================
# ADS1256 COMMANDS & REGISTERS
# ============================================
CMD_RDATA = 0x01
CMD_WREG  = 0x50

REG_ADCON  = 0x02
REG_DRATE  = 0x03

PGA_64 = 1 # PGA Gain = 64

DRATE_15K = 0xE0
DRATE_30K = 0xF0

# State variables
is_sampling = False

# ============================================
# ADS1256 FUNCTIONS
# ============================================
def wait_drdy():
    while drdy.value() == 1:
        pass

def write_register(register, value):
    wait_drdy()
    cs.value(0)
    time.sleep_us(5)
    spi.write(bytearray([CMD_WREG | register]))
    spi.write(bytearray([0x00]))
    spi.write(bytearray([value]))
    time.sleep_us(5)
    cs.value(1)

def configure_pga():
    write_register(REG_ADCON, PGA_64)

def read_adc():
    # Assumes DRDY is already 0
    cs.value(0)
    time.sleep_us(5)
    spi.write(bytearray([CMD_RDATA]))
    time.sleep_us(10)
    data = spi.read(3)
    cs.value(1)
    
    raw = (data[0] << 16) | (data[1] << 8) | data[2]
    if raw & 0x800000:
        raw -= 0x1000000
    return raw

# ============================================
# INITIALIZATION
# ============================================
print("Initializing ADS1256...")
configure_pga()
# Set a default rate
write_register(REG_DRATE, DRATE_15K)

# Calibrate zero offset
print("Calibrating...")
time.sleep(1)
zero = 0
for i in range(100):
    wait_drdy()
    zero += read_adc()
zero = int(zero / 100)
print("Ready. Zero offset:", zero)

poll_obj = select.poll()
poll_obj.register(sys.stdin, select.POLLIN)

cmd_buffer = ""

while True:
    # 1. Check for incoming commands (non-blocking)
    poll_res = poll_obj.poll(0)
    if poll_res:
        char = sys.stdin.read(1)
        if char == '\n' or char == '\r':
            if cmd_buffer:
                cmd = cmd_buffer.strip()
                cmd_buffer = ""
                if cmd == "START":
                    is_sampling = True
                elif cmd == "STOP":
                    is_sampling = False
                elif cmd == "RATE:15K":
                    write_register(REG_DRATE, DRATE_15K)
                elif cmd == "RATE:30K":
                    write_register(REG_DRATE, DRATE_30K)
        else:
            cmd_buffer += char

    # 2. If sampling is active, check DRDY and read
    if is_sampling:
        if drdy.value() == 0:
            val = read_adc() - zero
            print(val)
    else:
        time.sleep(0.01)

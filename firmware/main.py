import sys
import select
from machine import Pin, SPI
import time

# ============================================
# STATUS LED
# ============================================
led = Pin(2, Pin.OUT)
led.value(0)

# ============================================
# 10-SECOND SAFETY WINDOW (reduced for convenience)
# ============================================
print("=" * 40)
print("  VIBRATION MONITOR - ESP32 FIRMWARE")
print("  10s safety window active!")
print("  >>> Press Ctrl+C in Thonny to abort <<<")
print("=" * 40)

for i in range(10, 0, -1):
    print("  Booting in {}s...".format(i))
    led.value(i % 2)
    time.sleep(1)

# ============================================
# SPI CONFIG
# ============================================
spi = SPI(
    1,
    baudrate=1920000,
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

PGA_1     = 0x01
DRATE_15K = 0xE0
DRATE_30K = 0xF0

def wait_drdy():
    while drdy.value() == 1:
        pass

def write_register(register, value):
    wait_drdy()
    cs.value(0)
    time.sleep_us(2)
    spi.write(bytearray([CMD_WREG | register, 0x00, value]))
    time.sleep_us(2)
    cs.value(1)

# ============================================
# INITIALIZATION
# ============================================
print("Initializing ADS1256...")
write_register(REG_ADCON, PGA_1)
write_register(REG_DRATE, DRATE_15K)

_rdata_cmd = bytearray([CMD_RDATA])
_read_buf = bytearray(3)

print("Calibrating zero offset...")
time.sleep(0.5)
zero = 0
for i in range(100):
    wait_drdy()
    cs.value(0)
    time.sleep_us(2)
    spi.write(_rdata_cmd)
    time.sleep_us(7)
    spi.readinto(_read_buf)
    cs.value(1)
    raw = (_read_buf[0] << 16) | (_read_buf[1] << 8) | _read_buf[2]
    if raw & 0x800000:
        raw -= 0x1000000
    zero += raw
zero = zero // 100
print("Zero offset: {}".format(zero))

print("READY_115200")
led.value(1)

poll_obj = select.poll()
poll_obj.register(sys.stdin, select.POLLIN)
cmd_buffer = ""
is_sampling = False

# ============================================
# MAIN LOOP (100% STABLE)
# ============================================
while True:
    try:
        # 1. Non-blocking read of commands
        poll_res = poll_obj.poll(0)
        if poll_res:
            char = sys.stdin.read(1)
            if char == '\n' or char == '\r':
                if cmd_buffer:
                    cmd = cmd_buffer.strip()
                    cmd_buffer = ""
                    # Still supporting '1'/'0' as well as 'START'/'STOP' 
                    # just in case, but at 115200 the REPL won't drop letters.
                    if cmd in ("START", "1"):
                        is_sampling = True
                        led.value(1)
                    elif cmd in ("STOP", "0"):
                        is_sampling = False
                        led.value(0)
                    elif cmd in ("RATE:15K", "15"):
                        write_register(REG_DRATE, DRATE_15K)
                    elif cmd in ("RATE:30K", "30"):
                        write_register(REG_DRATE, DRATE_30K)
            else:
                cmd_buffer += char

        # 2. Sample and print
        if is_sampling:
            if drdy.value() == 0:
                cs.value(0)
                time.sleep_us(2)
                spi.write(_rdata_cmd)
                time.sleep_us(7)
                spi.readinto(_read_buf)
                cs.value(1)

                raw = (_read_buf[0] << 16) | (_read_buf[1] << 8) | _read_buf[2]
                if raw & 0x800000:
                    raw -= 0x1000000
                val = raw - zero
                print(val)
        else:
            time.sleep(0.01)

    except Exception as e:
        print("Error in loop:", e)
        time.sleep(1)

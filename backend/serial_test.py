"""
Test at 460800 baud - passive listening first, then START.
"""
import serial
import time

PORT = "COM7"
BAUD = 460800

print(f"Opening {PORT} @ {BAUD} baud (DTR/RTS disabled)...")
ser = serial.Serial()
ser.port = PORT
ser.baudrate = BAUD
ser.dtr = False
ser.rts = False
ser.timeout = 1
ser.open()

# DON'T clear buffer - we want to see boot messages
print("\n--- Phase 1: Passive listening (5s) - looking for READY/IDLE ---")
for i in range(5):
    time.sleep(1)
    n = ser.in_waiting
    if n > 0:
        data = ser.read(min(n, 1000))
        text = data.decode('utf-8', errors='replace')
        print(f"  [+] {len(data)} bytes: {repr(text[:120])}")
    else:
        print(f"  [ ] No data (second {i+1})")

ser.reset_input_buffer()

print("\n--- Phase 2: Sending START, listening 10s ---")
ser.write(b"1\n")
ser.flush()
print("  Sent: START")

total_samples = 0
for i in range(10):
    time.sleep(1)
    n = ser.in_waiting
    if n > 0:
        data = ser.read(min(n, 2000))
        text = data.decode('utf-8', errors='replace')
        lines = text.strip().split('\n')
        numeric = [l.strip() for l in lines if l.strip().lstrip('-').isdigit()]
        total_samples += len(numeric)
        print(f"  [+] {len(data)} bytes, {len(numeric)} samples (total: {total_samples})")
        if numeric:
            print(f"      First 5 values: {numeric[:5]}")
        elif lines:
            print(f"      Content: {repr(text[:100])}")
    else:
        print(f"  [ ] No data (second {i+1})")

ser.write(b"0\n")
ser.flush()
print(f"\n--- Summary ---")
print(f"Total numeric samples received: {total_samples}")
if total_samples > 0:
    print(f"Estimated SPS: ~{total_samples // 10}")

ser.close()
print("Done.")

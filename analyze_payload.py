from pypixelcolor.commands.send_text import send_text

def analyze(plan, name):
    d = plan.windows[0].data
    prefix = int.from_bytes(d[:2], 'little')
    print(f"\n=== {name} ===")
    print(f"Total len  : {len(d)}")
    print(f"Prefix len : {prefix}")
    print(f"Frame header bytes 2-14: {d[2:15].hex()}")
    payload_size = int.from_bytes(d[7:11], 'little')
    crc = int.from_bytes(d[11:15], 'little')
    print(f"Payload size : {payload_size}")
    print(f"CRC : {crc:08x}")
    offset = 15
    num_chars = d[offset]
    print(f"Num chars : {num_chars}")
    props = d[offset+1:offset+14]
    print(f"Props hex : {props.hex()}")
    print(f"  anim={props[3]}, speed={props[4]}, rainbow={props[5]}, color={props[6:9].hex()}")
    if props[9] == 1:
        print(f"  bg ENABLED, color={props[10:13].hex()}")
    else:
        print(f"  bg DISABLED")
    chars_start = offset + 14
    print(f"First 30 chars bytes: {d[chars_start:chars_start+30].hex()}")

analyze(send_text('hello', font='UNIFONT', char_height=32), "CLI")
analyze(send_text('hello', font='UNIFONT', char_height=32, animation='STATIC', speed=50, color='00ff00', bg_color='000000'), "GUI")

import struct

# Correct RGB values
rgb = (0, 120, 210)

# Correctly pack the RGB values into bytes
rgb_bytes = struct.pack('BBB', *rgb)

# Print the hexadecimal representation of the byte string for clarity
print(rgb_bytes.hex())
print(rgb_bytes)
import struct
import os
import zlib

def write_png(filename, width, height, pixels):
    # PNG file signature
    png_signature = b'\x89PNG\r\n\x1a\n'

    def chunk(chunk_type, data):
        length = struct.pack(">I", len(data))
        crc = struct.pack(">I", zlib.crc32(chunk_type + data) & 0xffffffff)
        return length + chunk_type + data + crc

    # IHDR chunk
    ihdr_data = struct.pack(">IIBBBBB", width, height, 8, 2, 0, 0, 0)
    ihdr = chunk(b'IHDR', ihdr_data)

    # Prepare raw image data (no filtering)
    raw_data = b''
    for y in range(height):
        raw_data += b'\x00'  # filter type 0
        for x in range(width):
            r, g, b = pixels[y][x]
            raw_data += bytes([r, g, b])

    # Compress image data
    idat = chunk(b'IDAT', zlib.compress(raw_data))

    # IEND chunk
    iend = chunk(b'IEND', b'')

    # Write to file
    with open(filename, 'wb') as f:
        f.write(png_signature)
        f.write(ihdr)
        f.write(idat)
        f.write(iend)

def capture_folder_to_png(folder_path, output_png):
    # List files in folder
    files = os.listdir(folder_path)
    files = [f for f in files if os.path.isfile(os.path.join(folder_path, f))]
    width = 400
    height = len(files) * 20 + 20
    # Create white background
    pixels = [[[255,255,255] for _ in range(width)] for _ in range(height)]
    # Write file names as black rectangles (simulate text)
    for i, fname in enumerate(files):
        y = i * 20 + 10
        for x in range(10, 10 + min(len(fname)*8, width-20)):
            for dy in range(8):
                if y+dy < height:
                    pixels[y+dy][x] = [0,0,0]
    write_png(output_png, width, height, pixels)

# Example usage:
# capture_folder_to_png('your_folder_path_here', 'output.png')
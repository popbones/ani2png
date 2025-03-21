#!/usr/bin/env python3
"""
ANI to Mousecape Converter

This script converts Windows ANI cursor files to animated PNG files suitable for
Mousecape, which expects frames to be stacked vertically with a transparent background.
"""

import os
import struct
import argparse
from PIL import Image
from io import BytesIO

class ANIReader:
    def __init__(self, file_path):
        self.file_path = file_path
        self.frames = []
        self.rate = 1000 // 60  # Default to 60 fps
        self.width = 0
        self.height = 0
        self.title = ""
        self.artist = ""
    
    def read_chunk(self, file):
        """Read a chunk from the file and return its ID, size, and data."""
        chunk_id = file.read(4)
        if not chunk_id or len(chunk_id) < 4:
            return None, 0, None
        
        chunk_size_data = file.read(4)
        if len(chunk_size_data) < 4:
            return None, 0, None
            
        chunk_size = struct.unpack("<I", chunk_size_data)[0]
        chunk_data = file.read(chunk_size)
        
        # Padding byte if chunk size is odd
        if chunk_size % 2 == 1:
            file.read(1)
            
        return chunk_id, chunk_size, chunk_data
    
    def process_ani_header(self, data):
        """Process the 'anih' chunk which contains header information."""
        if len(data) < 36:  # Minimum anih chunk size
            return
            
        # Handle both 36-byte and 40-byte headers
        if len(data) >= 40:
            # 40-byte header
            header = struct.unpack("<IIIIIIIIII", data[:40])
            self.num_frames = header[1]
            self.steps = header[2]
            self.width = header[3]
            self.height = header[4]
            self.jiffies = header[7]
            self.flags = header[9]
        else:
            # 36-byte header
            header = struct.unpack("<IIIIIIIII", data[:36])
            self.num_frames = header[1]
            self.steps = header[2]
            self.width = header[3]
            self.height = header[4]
            self.jiffies = header[7]
            self.flags = header[8]
        
        if self.jiffies > 0:
            self.rate = self.jiffies
    
    def extract_frame_from_icon(self, icon_data):
        """Extract an image from icon/cursor data."""
        try:
            # Try to open as an ICO file
            image = Image.open(BytesIO(icon_data))
            # Convert to RGBA to ensure transparency
            return image.convert("RGBA")
        except Exception as e:
            print(f"Error extracting frame: {e}")
            return None
    
    def parse(self):
        """Parse the ANI file and extract all frames."""
        try:
            with open(self.file_path, 'rb') as file:
                # Check RIFF header
                riff_id = file.read(4)
                if riff_id != b'RIFF':
                    raise ValueError("Not a valid RIFF file")
                
                # Skip file size
                file.read(4)
                
                # Check ANI header
                ani_id = file.read(4)
                if ani_id != b'ACON':
                    raise ValueError("Not a valid ANI file")
                
                # Read chunks until end of file
                icon_data = []
                seq_data = []
                
                while True:
                    chunk_id, chunk_size, chunk_data = self.read_chunk(file)
                    if chunk_id is None:
                        break
                    
                    if chunk_id == b'anih':
                        # ANI header chunk
                        self.process_ani_header(chunk_data)
                    
                    elif chunk_id == b'rate':
                        # Frame rate data
                        if chunk_size >= 4:
                            rates = struct.unpack(f"<{chunk_size // 4}I", chunk_data)
                            if rates and rates[0] > 0:
                                self.rate = rates[0]
                    
                    elif chunk_id == b'seq ':
                        # Frame sequence data
                        if chunk_size >= 4:
                            num_seq_entries = chunk_size // 4
                            seq_data = struct.unpack(f"<{num_seq_entries}I", chunk_data)
                    
                    elif chunk_id == b'LIST':
                        # List chunk, which may contain frames
                        if len(chunk_data) > 4:
                            list_type = chunk_data[:4]
                            list_data = chunk_data[4:]
                            
                            if list_type == b'fram':
                                # This is a frame list
                                pos = 0
                                while pos < len(list_data):
                                    if pos + 8 > len(list_data):
                                        break
                                        
                                    frame_id = list_data[pos:pos+4]
                                    pos += 4
                                    
                                    if pos + 4 > len(list_data):
                                        break
                                        
                                    frame_size = struct.unpack("<I", list_data[pos:pos+4])[0]
                                    pos += 4
                                    
                                    if pos + frame_size > len(list_data):
                                        break
                                        
                                    if frame_id == b'icon':
                                        # This is an icon frame
                                        icon_data.append(list_data[pos:pos+frame_size])
                                    
                                    pos += frame_size
                                    # Skip padding if size is odd
                                    if frame_size % 2 == 1:
                                        pos += 1
                
                # Process frames
                if not icon_data:
                    raise ValueError("No frames found in the ANI file")
                
                # Extract frames based on sequence if available
                if seq_data:
                    for idx in seq_data:
                        if 0 <= idx < len(icon_data):
                            frame = self.extract_frame_from_icon(icon_data[idx])
                            if frame:
                                self.frames.append(frame)
                else:
                    # No sequence data, use frames in order
                    for data in icon_data:
                        frame = self.extract_frame_from_icon(data)
                        if frame:
                            self.frames.append(frame)
                
                if not self.frames:
                    raise ValueError("Failed to extract any valid frames")
                
                # Get dimensions from the first frame if not in header
                if self.width == 0 or self.height == 0:
                    self.width, self.height = self.frames[0].size
                
                return True
                
        except Exception as e:
            print(f"Error parsing ANI file: {e}")
            return False

def generate_yaml_summary(converted_files):
    """Generate a YAML summary of converted files."""
    yaml_content = "cursors:\n"
    for file_info in converted_files:
        yaml_content += f"  - name: {file_info['name']}\n"
        yaml_content += f"    frames: {file_info['frames']}\n"
        if file_info['original_frames'] != file_info['frames']:
            yaml_content += f"    original_frames: {file_info['original_frames']}\n"
        yaml_content += f"    size: {file_info['width']}x{file_info['height']}\n"
        yaml_content += f"    stacked_size: {file_info['width']}x{file_info['height'] * file_info['frames']}\n"
        yaml_content += f"    rate: {file_info['rate']}\n"
        yaml_content += "\n"
    
    return yaml_content

def convert_ani_to_mousecape_png(ani_path, output_path=None):
    """Convert an ANI file to a Mousecape-compatible PNG file."""
    if output_path is None:
        # Default output is same name but with .png extension
        output_path = os.path.splitext(ani_path)[0] + ".png"
    
    try:
        # Parse the ANI file
        ani_reader = ANIReader(ani_path)
        if not ani_reader.parse():
            print(f"Failed to parse '{ani_path}'")
            return None
        
        frames = ani_reader.frames
        
        if not frames:
            raise ValueError("No valid frames extracted")
        
        # Get dimensions from the first frame
        width, height = frames[0].size
        
        # Limit to 24 frames if more frames exist
        original_frames = len(frames)
        if original_frames > 24:
            # Calculate step size to evenly sample frames
            step = original_frames / 24
            selected_frames = []
            for i in range(24):
                frame_index = int(i * step)
                selected_frames.append(frames[frame_index])
            frames = selected_frames
            print(f"Reduced frames from {original_frames} to 24")
        
        # Create a new image with all frames stacked vertically
        total_height = height * len(frames)
        result_image = Image.new("RGBA", (width, total_height), (0, 0, 0, 0))
        
        # Paste each frame
        for i, frame in enumerate(frames):
            result_image.paste(frame, (0, i * height))
        
        # Save the result
        result_image.save(output_path, "PNG")
        
        print(f"Successfully converted '{ani_path}' to '{output_path}'")
        print(f"Frames: {len(frames)}, Size: {width}x{height}, Stacked size: {width}x{total_height}")
        
        # Return file info for YAML summary
        return {
            'name': os.path.basename(ani_path),
            'frames': len(frames),
            'original_frames': original_frames,
            'width': width,
            'height': height,
            'rate': ani_reader.rate
        }
        
    except Exception as e:
        print(f"Error converting '{ani_path}': {e}")
        return None

def main():
    parser = argparse.ArgumentParser(description="Convert Windows ANI files to Mousecape-compatible PNG files")
    parser.add_argument("input", help="Input ANI file or directory containing ANI files")
    parser.add_argument("-o", "--output", help="Output PNG file or directory (default: same as input with .png extension)")
    parser.add_argument("-r", "--recursive", action="store_true", help="Process directories recursively")
    parser.add_argument("-v", "--verbose", action="store_true", help="Display detailed information during conversion")
    
    args = parser.parse_args()
    
    converted_files = []
    
    if os.path.isfile(args.input):
        # Process a single file
        if args.input.lower().endswith('.ani'):
            file_info = convert_ani_to_mousecape_png(args.input, args.output)
            if file_info:
                converted_files.append(file_info)
        else:
            print(f"Error: '{args.input}' is not an ANI file")
    elif os.path.isdir(args.input):
        # Process a directory
        output_dir = args.output if args.output else args.input
        if not os.path.exists(output_dir):
            os.makedirs(output_dir)
        
        for root, dirs, files in os.walk(args.input):
            for file in files:
                if file.lower().endswith('.ani'):
                    input_path = os.path.join(root, file)
                    
                    # Calculate relative path for output
                    rel_path = os.path.relpath(input_path, args.input)
                    output_path = os.path.join(output_dir, os.path.splitext(rel_path)[0] + ".png")
                    
                    # Ensure output directory exists
                    os.makedirs(os.path.dirname(output_path), exist_ok=True)
                    
                    file_info = convert_ani_to_mousecape_png(input_path, output_path)
                    if file_info:
                        converted_files.append(file_info)
            
            if not args.recursive:
                break
    
    # Generate YAML summary if any files were converted
    if converted_files:
        yaml_content = generate_yaml_summary(converted_files)
        yaml_path = os.path.join(output_dir if args.output else os.path.dirname(args.input), "cursors.yaml")
        with open(yaml_path, 'w', encoding='utf-8') as f:
            f.write(yaml_content)
        print(f"\nGenerated YAML summary at: {yaml_path}")
    else:
        print(f"Error: '{args.input}' is not a valid file or directory")

if __name__ == "__main__":
    main()
import json
import sys
import os
import re

def convert_json_file_simple(input_filename):
    """
    A simpler version that uses regex to split JSON objects
    """
    # Create output filename
    base, ext = os.path.splitext(input_filename)
    output_filename = f"{base}_array{ext}"
    
    try:
        # Read input file
        with open(input_filename, 'r', encoding='utf-8') as file:
            content = file.read()
        
        # Use regex to find all JSON objects
        # This pattern finds strings that start with { and end with }
        pattern = r'\{[^{}]*(?:\{[^{}]*\}[^{}]*)*\}'
        matches = re.findall(pattern, content)
        
        # Parse each JSON object
        json_objects = []
        for match in matches:
            try:
                obj = json.loads(match)
                json_objects.append(obj)
            except json.JSONDecodeError:
                print(f"Warning: Skipping invalid JSON object")
        
        # Write the array to output file
        with open(output_filename, 'w', encoding='utf-8') as file:
            file.write('[\n')
            for i, obj in enumerate(json_objects):
                json_str = json.dumps(obj, indent=2)
                if i < len(json_objects) - 1:
                    file.write(json_str + ',\n')
                else:
                    file.write(json_str + '\n')
            file.write(']\n')
            
        print(f"Successfully converted {len(json_objects)} JSON objects.")
        print(f"Output written to: {output_filename}")
        
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    # Check if input filename was provided
    if len(sys.argv) < 2:
        print("Usage: python json_converter_simple.py <input_filename>")
        sys.exit(1)
    
    input_filename = sys.argv[1]
    convert_json_file_simple(input_filename)
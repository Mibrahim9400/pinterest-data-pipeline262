import re
import json

def fix_malformed_json(input_file, output_file):
    pattern = re.compile(r"(\w+)=([^,{}\n]+)")  

    fixed_data = []
    
    with open(input_file, "r", encoding="utf-8") as file:
        for line in file:
            entry_dict = {}
            matches = pattern.findall(line)
            for key, value in matches:
                # Convert numbers where applicable
                if key in ['latitude', 'longitude']:
                    entry_dict[key] = float(value)
                elif key == 'ind':
                    entry_dict[key] = int(value)
                elif key == 'timestamp':
                    entry_dict[key] = value.strip()
                else:
                    entry_dict[key] = value.strip()
            fixed_data.append(entry_dict)

    # Save as properly formatted JSON with each entry on a new line
    with open(output_file, "w", encoding="utf-8") as json_out:
        for entry in fixed_data:
            json.dump(entry, json_out, separators=(',', ':'), ensure_ascii=False)
            json_out.write("\n")  # Write each JSON object on a new line

    print(f"Fixed JSON saved to {output_file}")

# Usage
input_json_file = "mo_user_user.json" 
output_json_file = "fixed_output.json"

fix_malformed_json(input_json_file, output_json_file)

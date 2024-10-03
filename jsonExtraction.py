import json

def txt_to_json(txt_file_path, json_file_path):
    try:
        with open(txt_file_path, 'r', encoding='utf-8') as txt_file:
            file_contents = txt_file.read()
        
        data = json.loads(file_contents)
        
        with open(json_file_path, 'w', encoding='utf-8') as json_file:
            json.dump(data, json_file, indent=4)
        
        print(f"Successfully converted {txt_file_path} to {json_file_path}.")
    except Exception as e:
        print(f"An error occurred: {e}")

txt_file_path = "V2properties62-69.txt"
json_file_path = "V2properties62-69.json"

txt_to_json(txt_file_path, json_file_path)

import json

def load_materials(filename="dataset_20250405.json"):
    with open(filename, "r", encoding="utf-8") as f:
        materials = json.load(f)
    return materials

if __name__ == "__main__":
    # For testing: print the first few materials
    materials = load_materials()
    for material in materials[:5]:
        print(material)
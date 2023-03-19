import os
import json
import random
from hashlib import sha1
from PIL import Image


def load_layers_config(file_path):
    with open(file_path, "r") as f:
        layers_config = json.load(f)
    return layers_config


def get_elements(layer_path):
    return [file for file in os.listdir(layer_path) if file.lower().endswith('.png')]


def generate_dna(attributes):
    dna_string = "".join([attr["name"] + attr["element"] for attr in attributes])
    dna_hash = sha1(dna_string.encode()).hexdigest()
    return dna_hash


def calculate_unique_variations(layers):
    variations = 1
    for layer in layers:
        elements = get_elements(layer["path"])
        variations *= len(elements)
    return variations


def generate_art(layers, output_path, num_images):
    unique_variations = calculate_unique_variations(layers)
    if unique_variations < num_images:
        print(f"Warning: Requested {num_images} images, but only {unique_variations} unique variations are possible.")
        return

    generated_dna = set()

    for i in range(num_images):
        while True:
            composite = None
            attributes = []

            for layer in layers:
                elements = get_elements(layer["path"])
                element = random.choice(elements)
                img = Image.open(os.path.join(layer["path"], element)).convert("RGBA")

                attributes.append({"name": layer["name"], "element": element})

                if composite is None:
                    composite = Image.new("RGBA", img.size, (0, 0, 0, 0))

                composite.alpha_composite(img)

            dna = generate_dna(attributes)

            if dna not in generated_dna:
                generated_dna.add(dna)
                break

        renders_path = os.path.join(output_path, "renders")
        metadata_path = os.path.join(output_path, "metadata")
        os.makedirs(renders_path, exist_ok=True)
        os.makedirs(metadata_path, exist_ok=True)
        composite.save(os.path.join(renders_path, f"output_{i + 1}.png"))

        metadata = {"attributes": attributes, "dna": dna}

        with open(os.path.join(metadata_path, f"metadata_{i + 1}.json"), "w") as f:
            json.dump(metadata, f, indent=2)


layers = load_layers_config("./config/layers.json")
output_path = "output"
num_images = 44
generate_art(layers, output_path, num_images)

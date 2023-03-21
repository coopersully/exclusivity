import os
import json
import random
from hashlib import sha1
from PIL import Image

# Configurable settings
num_images = 44
output_path = "output"
renders_path = os.path.join(output_path, "renders")
metadata_path = os.path.join(output_path, "metadata")


# Get predefined layers as a json object from layers.config
def load_collections_config(file_path):
    with open(file_path, "r") as f:
        collections_config = json.load(f)
    return collections_config


# Get predefined layers as a json object from layers.config
def load_layers_config(file_path):
    with open(file_path, "r") as f:
        layers_config = json.load(f)
    return layers_config


# Get all png files in a given folder
def get_elements(layer_path):
    return [file for file in os.listdir(layer_path) if file.lower().endswith('.png')]


# Generate SHA-1 hash string from a list of attributes
def generate_dna(attributes):
    dna_string = "".join([attr["name"] + attr["element"] for attr in attributes])
    dna_hash = sha1(dna_string.encode()).hexdigest()
    return dna_hash


# Determine how many unique tokens can be created from the given layers
def calculate_unique_variations(layers):
    variations = 1
    for layer in layers:
        elements = get_elements(layer["path"])
        variations *= len(elements)
    return variations


# Delete all files in a specified directory
def remove_files_from_directory(directory):
    for file in os.listdir(directory):
        file_path = os.path.join(directory, file)
        if os.path.isfile(file_path):
            os.remove(file_path)


# Generate tokens with the current configurations
def generate_art(layers, collections_config):
    unique_variations = calculate_unique_variations(layers)
    if unique_variations < num_images:
        print(f"Warning: Requested {num_images} images, but only {unique_variations} unique variations are possible.")
        return

    os.makedirs(renders_path, exist_ok=True)
    os.makedirs(metadata_path, exist_ok=True)

    if collections_config["purge_on_generate"]:
        # Remove all files from output directories
        print('Purging previous generative metadata and renders...')
        remove_files_from_directory(renders_path)
        remove_files_from_directory(metadata_path)

    prefix = collections_config["name"]["prefix"]
    suffix = collections_config["name"]["suffix"]

    generated_dna = set()

    for edition in range(1, num_images + 1):
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

        composite.save(os.path.join(renders_path, f"{edition}.png"))

        token_name = prefix + str(edition) + suffix
        metadata = {"name": token_name, "edition": edition, "dna": dna, "attributes": attributes}

        with open(os.path.join(metadata_path, f"{edition}.json"), "w") as f:
            json.dump(metadata, f, indent=2)


if __name__ == "__main__":
    collections_config = load_collections_config("./config/collections.json")
    layers_config = load_layers_config("./config/layers.json")
    generate_art(layers_config, collections_config)

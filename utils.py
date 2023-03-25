import yaml
import os
from hashlib import sha1

from models.Collection import Collection
from models.Layer import Layer


def load_collections_config(file_path):
    with open(file_path, "r") as f:
        config = yaml.safe_load(f)
    name = config["name"]
    purge_on_generate = config["purge_on_generate"]
    strip_extensions = config["strip_extensions"]
    num_tokens = config["tokens"]
    return Collection(name, purge_on_generate, strip_extensions, num_tokens)


def load_layers_config(file_path):
    with open(file_path, "r") as f:
        config = yaml.safe_load(f)
    return [Layer(**layer) for layer in config["layers"]]



def get_images_in_dir(layer_path):
    return [file for file in os.listdir(layer_path) if file.lower().endswith('.png')]


def generate_dna(attributes):
    dna_string = "".join([attr["name"] + attr["element"] for attr in attributes])
    dna_hash = sha1(dna_string.encode()).hexdigest()
    return dna_hash


def calculate_unique_variations(layers):
    variations = 1
    for layer in layers:
        elements = get_images_in_dir(layer.path)
        variations *= len(elements)
    return variations


def remove_files_from_directory(directory):
    for file in os.listdir(directory):
        file_path = os.path.join(directory, file)
        if os.path.isfile(file_path):
            os.remove(file_path)

import json
import os
from hashlib import sha1

from Collection import Collection
from Layer import Layer


def load_collections_config(file_path):
    with open(file_path, "r") as f:
        config_json = json.load(f)
    name = config_json["name"]
    prefix = name["prefix"]
    suffix = name["suffix"]
    purge_on_generate = config_json["purge_on_generate"]
    strip_extensions = config_json["strip_extensions"]
    return Collection(name, purge_on_generate, prefix, suffix, strip_extensions)


def load_layers_config(file_path):
    with open(file_path, "r") as f:
        config_json = json.load(f)
    return [Layer(**layer) for layer in config_json]


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

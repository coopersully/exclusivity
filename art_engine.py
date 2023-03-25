import json
import random
import time

from PIL import Image

from models.Token import Token
from utils import *

output_path = "output"
renders_path = os.path.join(output_path, "renders")
metadata_path = os.path.join(output_path, "metadata")


def generate_art(layers, config):
    # Calculate the number of unique variations possible from the given layers
    unique_variations = calculate_unique_variations(layers)

    # If the number of unique variations is less than the
    # requested number of tokens, print an error message and return.
    if unique_variations < config.num_tokens:
        print(
            f"[ERROR] Requested {config.num_tokens} images, but only {unique_variations} unique variations are possible.")
        return

    # Create directories to store the generated images and metadata
    os.makedirs(renders_path, exist_ok=True)
    os.makedirs(metadata_path, exist_ok=True)

    # If configured to do so, remove any previously generated metadata and images
    if config.purge_on_generate:
        print('[PRE] Purging previous generative metadata and renders...')
        remove_files_from_directory(renders_path)
        remove_files_from_directory(metadata_path)
        print('[PRE] Purging previous generative metadata and renders... Done!')

    # Keep track of generated DNA strings to ensure uniqueness
    generated_dna = set()

    # Generate the specified number of tokens
    for edition in range(1, config.num_tokens + 1):
        while True:
            composite = None
            attributes = []

            # Iterate over each layer and randomly select an image from its directory
            for layer in layers:
                elements = get_images_in_dir(layer.path)
                element: str = random.choice(elements)
                img = Image.open(os.path.join(layer.path, element)).convert("RGBA")

                # If configured to do so, strip the file extension from the element name
                if config.strip_extensions:
                    elements = element.rsplit('.', 1)
                    element = elements[0]

                # Store the name of the layer and the selected element in the attributes list
                attributes.append({"name": layer.name, "element": element})

                # If this is the first layer being added to the composite
                # image, create a new one with the same size as the selected image
                if composite is None:
                    composite = Image.new("RGBA", img.size, (0, 0, 0, 0))

                # Alpha composite the selected image onto the composite image
                composite.alpha_composite(img)

            # Generate a DNA string based on the selected images and their layers
            dna = generate_dna(attributes)

            # If this DNA string has not been generated before, add it
            # to the set of generated DNA strings and break out of the loop
            if dna not in generated_dna:
                generated_dna.add(dna)
                break

        # Create a token object and save its metadata to a JSON file
        token_name = f'{config.prefix}{edition}{config.suffix}'
        token = Token(token_name, edition, dna, attributes)

        # Save the composite image to a PNG file with the edition number as the filename
        composite.save(os.path.join(renders_path, f"{edition}.png"))

        # Save the token metadata to a JSON file with the edition number as the filename
        with open(os.path.join(metadata_path, f"{edition}.json"), "w") as f:
            json.dump(token.__dict__, f, indent=2)

        print(f'[GEN] Successfully generated token {edition}/{config.num_tokens}.')


if __name__ == "__main__":
    # Begin timer for logging purposes
    start_time = time.time_ns()

    # Load config files
    collections_config = load_collections_config("./config/collections.yml")
    layers_config = load_layers_config("config/layers.yml")

    # Attempt to generate a new collection
    generate_art(layers_config, collections_config)

    # End timer & log the total generation time to
    # the console in a pretty, easy-to-read format.
    end_time = time.time_ns()

    duration_in_seconds = (end_time - start_time) / 1_000_000_000
    days = duration_in_seconds // (24 * 3600)
    duration_in_seconds %= 24 * 3600
    hours = duration_in_seconds // 3600
    duration_in_seconds %= 3600
    minutes = duration_in_seconds // 60
    seconds = duration_in_seconds % 60

    time_components = []
    if days > 0:
        time_components.append(f'{int(days)} days')
    if hours > 0:
        time_components.append(f'{int(hours)} hours')
    if minutes > 0:
        time_components.append(f'{int(minutes)} minutes')
    if seconds > 0:
        time_components.append(f'{seconds:.2f} seconds')

    duration_str = ' '.join(time_components)
    print(f'Generation completed in {duration_str}')

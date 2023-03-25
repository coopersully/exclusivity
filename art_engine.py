import random
import time

from PIL import Image

from Token import Token
from utils import *

output_path = "output"
renders_path = os.path.join(output_path, "renders")
metadata_path = os.path.join(output_path, "metadata")


def generate_art(layers, config):
    unique_variations = calculate_unique_variations(layers)
    if unique_variations < config.num_tokens:
        print(
            f"[ERROR] Requested {config.num_tokens} images, but only {unique_variations} unique variations are possible.")
        return

    os.makedirs(renders_path, exist_ok=True)
    os.makedirs(metadata_path, exist_ok=True)

    if config.purge_on_generate:
        print('[PRE] Purging previous generative metadata and renders...')
        remove_files_from_directory(renders_path)
        remove_files_from_directory(metadata_path)
        print('[PRE] Purging previous generative metadata and renders... Done!')

    generated_dna = set()

    for edition in range(1, config.num_tokens + 1):
        while True:
            composite = None
            attributes = []

            for layer in layers:
                elements = get_images_in_dir(layer.path)
                element: str = random.choice(elements)
                img = Image.open(os.path.join(layer.path, element)).convert("RGBA")

                if config.strip_extensions:
                    elements = element.rsplit('.', 1)
                    element = elements[0]

                attributes.append({"name": layer.name, "element": element})

                if composite is None:
                    composite = Image.new("RGBA", img.size, (0, 0, 0, 0))

                composite.alpha_composite(img)

            dna = generate_dna(attributes)

            if dna not in generated_dna:
                generated_dna.add(dna)
                break

        token_name = f'{config.prefix}{edition}{config.suffix}'
        token = Token(token_name, edition, dna, attributes)

        composite.save(os.path.join(renders_path, f"{edition}.png"))

        with open(os.path.join(metadata_path, f"{edition}.json"), "w") as f:
            json.dump(token.__dict__, f, indent=2)

        print(f'[GEN] Successfully generated token {edition}/{config.num_tokens}.')


if __name__ == "__main__":
    start_time = time.time_ns()

    collections_config = load_collections_config("./config/collections.yml")
    layers_config = load_layers_config("config/layers.yml")

    generate_art(layers_config, collections_config)

    end_time = time.time_ns()
    print(f'Generation completed in {(end_time - start_time) / 1000000000}s')

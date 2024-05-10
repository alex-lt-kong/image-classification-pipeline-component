from typing import Any, Dict
from PIL import Image

import argparse
import helper
import json
import os
import random
import shutil
import threading
import time
import torchvision


curr_dir = os.path.dirname(os.path.abspath(__file__))


def apply_transform_and_save(
    source_dir: str, image_filename: str, target_dir: str, variant_no: int,
    transforms: torchvision.transforms.Compose
):

    # Load the image
    image_path = os.path.join(source_dir, image_filename)
    image = Image.open(image_path)
    try:
        transformed_image = transforms(image)
    except Exception as ex:
        print(f'Error transforming [{image_path}]: {ex}')
        return
    finally:
        image.close()

    # Save the transformed image to the target directory
    target_path = os.path.join(target_dir, image_filename)
    from torchvision.utils import save_image
    save_image(
        transformed_image,
        target_path + f'_{variant_no}.jpg'
    )


def prepare_files(
        input_dir: str,
        train_dir: str, val_dir: str,
        split_ratio: float, synthetic_multiplier: int, seed: int = 97381
) -> None:
    if os.path.exists(train_dir):
        print(
            f'[{train_dir}] exists '
            f'(file count: {len(os.listdir(train_dir)):,}), it will be removed'
        )
        shutil.rmtree(train_dir)
    os.makedirs(train_dir)
    if os.path.exists(val_dir):
        print(
            f'[{val_dir}] exists '
            f'(file count: {len(os.listdir(val_dir)):,}), it will be removed'
        )
        shutil.rmtree(val_dir)
    print('')
    os.makedirs(val_dir)

    files = os.listdir(input_dir)
    random.seed(seed)

    num_files = len(files)
    num_files_dir_1 = int(num_files * split_ratio)
    random.shuffle(files)

    for i, file in enumerate(files):
        for j in range(synthetic_multiplier):
            if i < num_files_dir_1:
                apply_transform_and_save(
                    input_dir, file, train_dir, j, helper.train_transforms
                )
            else:
                apply_transform_and_save(
                    input_dir, file, val_dir, j, helper.test_transforms
                )

    print(
        f'Splitting files from [{input_dir}] to '
        f'[{train_dir}]/[{val_dir}] completed successfully.\n'
        f'[{train_dir}] file count: {len(os.listdir(train_dir)):,}\n'
        f'[{val_dir}] file count: {len(os.listdir(val_dir)):,}\n'
    )


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument('--config-path', '-c', dest='config-path', required=True,
                    help='Config file path')
    ap.add_argument(
        '--split-ratio', '-r', help='Ratio of the training set',
        dest='split-ratio', type=float, default='0.9'
    )
    ap.add_argument(
        '--synthetic-multiplier', '-m',
        help=(
            'Number of raw samples times synthetic-multiplier will be the '
            'count of training+validation samples'
        ),
        dest='synthetic-multiplier', type=float, default='2'
    )
    args = vars(ap.parse_args())

    config = Dict[str, Any]
    with open(args['config-path']) as j:
        config = json.load(j)

    random_seed = 16888
    helper.init_transforms((
        config['model']['input_image_size']['height'],
        config['model']['input_image_size']['width']
    ))
    threads = []
    for cat in range(config['model']['num_classes']):
        cat = str(cat)
        input_dir = os.path.join(config["dataset"]['raw'], cat)
        training_dir = os.path.join(config["dataset"]['training'], cat)
        validation_dir = os.path.join(config["dataset"]['validation'], cat)
        thread = threading.Thread(target=prepare_files, args=(
            input_dir, training_dir, validation_dir,
            args['split-ratio'], int(args['synthetic-multiplier']), random_seed
        ))
        thread.start()
        threads.append(thread)
        time.sleep(10)

    for thread in threads:
        thread.join()


if __name__ == '__main__':
    main()
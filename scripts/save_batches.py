import time
from pathlib import Path

import click
import numpy as np

from wholeslidedata.iterators import create_batch_iterator


@click.command()
@click.option("--mode", type=str, required=True)
@click.option("--config", type=Path, required=True)
@click.option("--output_folder", type=Path, required=True)
@click.option("--cpus", type=int, required=True)
@click.option("--number_of_batches", type=int, required=True)
@click.option("--dtype", type=str, required=False, default="uint16")
def main(
    mode: str,
    config: Path,
    output_folder: Path,
    cpus: int,
    number_of_batches: int,
    dtype: str,
):
    t1_init_iterator = time.time()
    print("Initializing Batch Iterator...")
    with create_batch_iterator(
        mode=mode,
        user_config=config,
        number_of_batches=number_of_batches,
        cpus=cpus,
        buffer_dtype=dtype,
    ) as iterator:
        print("INIT iterator time:", time.time() - t1_init_iterator)

        t1_init_producers = time.time()

        output_folder = output_folder / mode
        print(f"Creating output folder: {output_folder}")
        output_folder.mkdir(exist_ok=True, parents=True)

        print("Initializing Batch Producers...")
        t1_batch_collection = None
        for index, (x_batch, y_batch, info) in enumerate(iterator):
            if index == 0:
                print("INIT producers time:", time.time() - t1_init_producers)
            t1_batch_collection = time.time()
            output_path = output_folder / f"{index}_batch.npz"
            print(f"Writing Batch {index}: {output_path}")
            np.savez(output_path, x_batch=x_batch, y_batch=y_batch, info=info)
        print("Batch collection time", time.time() - t1_batch_collection)


if __name__ == "__main__":
    main()

from pathlib import Path
import time

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
    print("Initializing Batch Iterator...")
    with create_batch_iterator(
        mode=mode,
        user_config=config,
        number_of_batches=number_of_batches,
        cpus=cpus,
        buffer_dtype=dtype,
    ) as iterator:

        output_folder = output_folder / mode
        print(f"Creating output folder: {output_folder}")
        output_folder.mkdir(exist_ok=True, parents=True)
        print("Initializing Batch Producers...")
        for index, (x_batch, y_batch, info) in enumerate(iterator):
            output_path = output_folder / f"{index}_batch.npz"
            print(f"Writing Batch {index}: {output_path}")
            np.savez(output_path, x_batch=x_batch, y_batch=y_batch, info=info)


if __name__ == "__main__":
    main()

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
    with create_batch_iterator(
        mode=mode,
        user_config=config,
        number_of_batches=number_of_batches,
        cpus=cpus,
        buffer_dtype=dtype,
    ) as iterator:

        output_folder = output_folder / mode
        output_folder.mkdir(exist_ok=True, parents=True)

        for index, (x_batch, y_batch, info) in enumerate(iterator):
            output_path = output_folder / f"{index}_batch.npz"
            np.savez(output_path, x_batch=x_batch, y_batch=y_batch, info=info)


if __name__ == "__main__":
    main()

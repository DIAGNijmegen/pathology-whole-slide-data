from pathlib import Path
import numpy as np
import click


@click.command()
@click.option("--batch_folder", type=Path, required=True)
def main(batch_folder: Path):
    batches = sorted(list(Path(batch_folder).glob('*.npz')))
    for batch in batches:
        loaded_batch = np.load(batch, allow_pickle=True)
        x_batch, y_batch, info = loaded_batch.values()

if __name__ == "__main__":
    main()
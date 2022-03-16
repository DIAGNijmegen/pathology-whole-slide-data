from wholeslidedata.samplers.utils import plot_mask
from matplotlib import pyplot as plt

###  plotting utilities
def init_plot(batches, batch_size, size=(20,5)):
    fig, axes = plt.subplots(batches, batch_size, figsize=size)
    return fig, axes

def show_plot(fig, r, fontsize=16):
    fig.suptitle(f'Batches (repeat={r})', fontsize=fontsize)
    plt.tight_layout()
    plt.show()

def plot_batch(axes, idx, x_batch, y_batch, alpha=0.4):
    for batch_index in range(len(x_batch)):
        axes[idx][batch_index].imshow(x_batch[batch_index])
        plot_mask(y_batch[batch_index], axes=axes[idx][batch_index], alpha=alpha)

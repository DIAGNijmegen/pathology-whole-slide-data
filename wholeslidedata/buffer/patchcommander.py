from concurrentbuffer.commander import Commander
import sys
class PatchCommander(Commander):
    def __init__(self, info_queue, x_dims: int, y_dims: int, spacing: float, tile_size: int = 1024):
        self._x_dims = x_dims
        self._y_dims = y_dims
        self._spacing = spacing
        self._tile_size = tile_size
        self._info_queue = info_queue
        self._messages = []

    def build(self):
        messages = []
        for row in range(0, self._y_dims, self._tile_size):
            for col in range(0, self._x_dims, self._tile_size):
                message = {
                    "x": col,
                    "y": row,
                    "tile_size": self._tile_size,
                    "spacing": self._spacing,
                }
                self._info_queue.put(message)
                messages.append(message)
        self._messages = iter(messages)

    
    def create_message(self) -> dict:
        try:
            return next(self._messages)
        except StopIteration:
            sys.exit()

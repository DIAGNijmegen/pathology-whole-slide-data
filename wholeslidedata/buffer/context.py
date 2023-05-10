import os

DEFAULT_CONTEXT = "spawn" if os.name=="nt" else "fork"
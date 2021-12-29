import multiprocessing
from concurrentbuffer.factory import BufferFactory
from concurrentbuffer.info import BufferInfo
from concurrentbuffer.state import BufferState
from concurrentbuffer.system import BufferSystem


# move to buffer lib
def create_buffer_factory(
    cpus,
    batch_commander,
    batch_producer,
    context,
    deterministic,
    buffer_shapes,
    buffer_dtype,
):

    count = cpus * len(BufferState)

    mp_context = multiprocessing.get_context(context)
    buffer_system = BufferSystem(
        cpus=cpus, context=mp_context, deterministic=deterministic
    )

    buffer_info = BufferInfo(count=count, shapes=buffer_shapes, dtype=buffer_dtype)

    return BufferFactory(
        buffer_system=buffer_system,
        buffer_info=buffer_info,
        commander=batch_commander,
        producer=batch_producer,
    )

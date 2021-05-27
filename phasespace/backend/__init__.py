import os
from enum import Enum, auto

__all__ = [
    "function",
    "function_jit",
    "function_jit_fixedshape",
    "get_shape",
    "random",
    "tnp",
]


class BackendType(Enum):
    TENSORFLOW = auto()

    @staticmethod
    def get_backend(backend: str) -> "BackendType":
        backend_formatted = backend.lower().strip()
        if backend_formatted in {"", "tf", "tensorflow"}:
            return BackendType.TENSORFLOW
        raise NotImplementedError(f'No backend implemented for "{backend}"')


BACKEND = BackendType.get_backend(os.environ.get("PHASESPACE_BACKEND", ""))
if BACKEND == BackendType.TENSORFLOW:
    import tensorflow as tf
    import tensorflow.experimental.numpy as tnp

    from . import _tf_random as random

    if int(tf.__version__.split(".")[1]) < 5:  # smaller than 2.5
        jit_compile_argname = "experimental_compile"
    else:
        jit_compile_argname = "jit_compile"
    function = tf.function(
        autograph=False,
        experimental_relax_shapes=True,
        **{jit_compile_argname: False},
    )
    function_jit = tf.function(
        autograph=False,
        experimental_relax_shapes=True,
        **{jit_compile_argname: True},
    )
    function_jit_fixedshape = tf.function(
        autograph=False,
        experimental_relax_shapes=False,
        **{jit_compile_argname: True},
    )

    get_shape = tf.shape  # get shape dynamically
    assert_equal = tf.assert_equal
    assert_greater_equal = tf.debugging.assert_greater_equal

    is_eager = bool(os.environ.get("PHASESPACE_EAGER"))
    tf.config.run_functions_eagerly(is_eager)
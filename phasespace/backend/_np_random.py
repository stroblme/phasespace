__all__ = [
    "Generator",
    "from_seed",
    "default_rng",
]

from typing import Optional, Type

from numpy.random import PCG64, BitGenerator, Generator, default_rng


def from_seed(
    seed,
    alg: Optional[Type[BitGenerator]] = None,
) -> Generator:
    """Function that mimicks `tf.random.Generator.from_seed`."""
    if alg is None:
        alg = PCG64
    bit_generator = alg(seed)
    return Generator(bit_generator)

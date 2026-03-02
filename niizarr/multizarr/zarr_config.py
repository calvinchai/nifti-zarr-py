"""Configuration related to output Zarr Archive."""
from dataclasses import field
from typing import List, Literal, Optional, Union

from ._typing import TypeAlias, dataclass


ZarrDriver: TypeAlias = Literal["zarr-python", "tensorstore", "zarrita"]
ZarrVersion: TypeAlias = Literal[2,3]

@dataclass
class ZarrConfig:
    """
    Configuration related to output Zarr Archive.

    Parameters
    ----------
    chunk
        Output chunk size.
        Behavior depends on the number of values provided:
        * one:   used for all spatial dimensions
        * three: used for spatial dimensions ([z, y, x])
        * four+:  used for channels and spatial dimensions ([c, z, y, x])
        If `"auto"`, find chunk size smaller than 1 MB (TODO: not implemented)
    zarr_version
        Zarr version to use. If `shard` is used, 3 is required.
    chunk_channels:
        Put channels in different chunk.
        If False, combine all channels in a single chunk.
    chunk_time :
        Put timepoints in different chunk.
        If False, combine all timepoints in a single chunk.
    shard
        Output shard size.
        Behavior same as chunk.
        If `"auto"`, find shard size that ensures files smaller than 2TB,
        assuming a compression ratio or 2.
    shard_channels:
        Put channels in different shards.
        If False, combine all channels in a single shard.
    shard_time:
        Put timepoints in different shards.
        If False, combine all timepoints in a single shard.
    dimension_separator:
        The separator placed between the dimensions of a chunk.
    order:
        Memory layout order for the data array.
    compressor
        Compression method
    compressor_opt
        Compression options
    no_time
        If True, indicates that the dataset does not have a time dimension.
        In such cases, any fourth dimension is interpreted as the channel dimension.
    no_pyramid_axis
        Spatial axis that should not be downsampled when generating pyramid levels.
        If None, downsampling is applied across all spatial axes.
    levels : int, optional
        Number of pyramid levels to generate.
        If set to -1, all possible levels are generated until the smallest level
        fits into one chunk.
    ome_version
        Version of the OME-Zarr specification to use
    overwrite
        when no name is supplied and using default output name, if overwrite is set,
        it won't ask if overwrite
    driver : {"zarr-python", "tensorstore", "zarrita"}
        library used for Zarr IO Operation
    """

    zarr_version: ZarrVersion = 3
    chunk: List[int] = (128,)
    chunk_channels: bool = False
    chunk_time: bool = True
    shard:  Union[Literal['auto'], List[int], None] = None
    shard_channels: bool = False
    shard_time: bool = False
    dimension_separator: Literal[".", "/"] = "/"
    order: Literal["C", "F"] = "C"
    compressor: Literal["blosc", "zlib", "none"] = "blosc"
    compressor_opt: dict = field(default_factory=dict)
    # Default fill value for created arrays; if None, backend defaults are used.
    fill_value: Optional[object] = None
    no_time: bool = False
    no_pyramid_axis: Union[str, int, None] = None
    levels: int = -1
    ome_version: Literal["0.4", "0.5"] = "0.4"
    overwrite: bool = False
    driver: ZarrDriver = "zarr-python"

    def __post_init__(self) -> None:
        """
        Perform post-initialization checks and adjustments.

        - Ensure that sharding options (shard, shard_channels, shard_time) are only
          used when zarr_version == 3; otherwise raise NotImplementedError.
        """
        if self.zarr_version == 2:
            if self.shard or self.shard_channels or self.shard_time:
                raise ValueError("Shard is not supported for Zarr 2.")


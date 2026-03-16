"""Factory module for creating/opening Zarr Nodes with different drivers."""

from __future__ import annotations

import importlib
import warnings
from os import PathLike
from typing import Literal, Optional, Union

from .abc import ZarrGroup, ZarrNode
from .zarr_config import ZarrDriver, ZarrConfig


class UnsupportedDriverError(ValueError):
    """Exception raised when an unsupported driver is specified."""

    def __init__(self, driver: Union[ZarrDriver, str]) -> None:
        super().__init__(f"Unsupported driver: {driver}")
        self.driver = driver


_DRIVER_ARRAY: dict[str, type] = {}
_DRIVER_GROUP: dict[str, type] = {}

# name -> (probe_module, array_path, group_path)
# where *_path is "pkg.module:ClassName"
_DRIVERS: dict[str, tuple[str, str, str]] = {
    "zarr-python": (
        "zarr",
        "niizarr.multizarr.drivers.zarr_python:ZarrPythonArray",
        "niizarr.multizarr.drivers.zarr_python:ZarrPythonGroup",
    ),
    "tensorstore": (
        "tensorstore",
        "niizarr.multizarr.drivers.tensorstore:ZarrTSArray",
        "niizarr.multizarr.drivers.tensorstore:ZarrTSGroup",
    ),
}


def _import_symbol(path: str) -> type:
    """Import a symbol given its full path as 'module:attr'."""
    mod_path, _, attr = path.partition(":")
    if not attr:
        raise ValueError(f"Expected 'module:attr' path, got {path!r}")
    module = importlib.import_module(mod_path)
    try:
        return getattr(module, attr)
    except AttributeError as e:
        raise ImportError(f"Cannot import '{attr}' from '{mod_path}'") from e


def _ensure_driver(driver_name: ZarrDriver) -> None:
    """Load and register a single driver if not already registered."""
    if _DRIVER_ARRAY.get(driver_name) is not None:
        return
    entry = _DRIVERS.get(driver_name)
    if entry is None:
        return
    probe_mod, array_path, group_path = entry
    if importlib.util.find_spec(probe_mod) is None:
        warnings.warn(
            f"{driver_name} driver not available: missing dependency '{probe_mod}'."
        )
        return
    try:
        arr_cls = _import_symbol(array_path)
        grp_cls = _import_symbol(group_path)
    except Exception as e:
        warnings.warn(f"{driver_name} driver failed to load: {e}")
        return
    _DRIVER_ARRAY[driver_name] = arr_cls
    _DRIVER_GROUP[driver_name] = grp_cls


def _get_default_driver() -> ZarrDriver:
    """Return the first available driver by trying each in _DRIVERS order."""
    for name in _DRIVERS:
        _ensure_driver(name)
        if _DRIVER_ARRAY.get(name) is not None:
            return name
    raise UnsupportedDriverError("No driver available (zarr-python or tensorstore)")


def open_array(
    path: Union[str, PathLike[str]],
    mode: Literal["r", "r+", "a", "w", "w-"] = "a",
    zarr_version: Literal[2, 3] = 3,
    driver: Optional[ZarrDriver] = None,
) -> ZarrNode:
    """Open a Zarr Node (Array or Group) based on the specified driver."""
    if driver is None:
        driver = _get_default_driver()
    _ensure_driver(driver)
    array_cls = _DRIVER_ARRAY.get(driver)
    if array_cls is None:
        raise UnsupportedDriverError(driver)
    return array_cls.open(path, mode=mode, zarr_version=zarr_version)


def open_group(
    path: Union[str, PathLike[str]],
    mode: Literal["r", "r+", "a", "w", "w-"] = "a",
    zarr_version: Literal[2, 3] = 3,
    driver: Optional[ZarrDriver] = None,
) -> ZarrGroup:
    """Open a Zarr Group based on the specified driver."""
    if driver is None:
        driver = _get_default_driver()
    _ensure_driver(driver)
    group_cls = _DRIVER_GROUP.get(driver)
    if group_cls is None:
        raise UnsupportedDriverError(driver)
    return group_cls.open(path, mode, zarr_version=zarr_version)


def from_config(out: Union[str, PathLike[str]], zarr_config: ZarrConfig) -> ZarrGroup:
    """Create a ZarrGroup from a ZarrConfig."""
    _ensure_driver(zarr_config.driver)
    group_cls = _DRIVER_GROUP.get(zarr_config.driver)
    if group_cls is None:
        raise UnsupportedDriverError(zarr_config.driver)
    return group_cls.from_config(out, zarr_config)

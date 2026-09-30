"""renpy
init -990 python in phone:
"""

# Shared helpers for every part of the phone framework.

from typing import TYPE_CHECKING, Any, Optional, cast
from collections.abc import Iterable

import store  # pyright: ignore[reportMissingImports]
import renpy.exports as renpy
from renpy import (
    config as _config,
    game as _game,
)
from renpy.compat.pickle import dumps as _pickle_dumps
from renpy.display.transform import Transform

if TYPE_CHECKING:
    cfg: Any

REFERENCE_HEIGHT = 1080.0


def px(n: float) -> int:
    return round(n * _config.screen_height / REFERENCE_HEIGHT)


def text_px(n: int) -> int:
    return px(n * text_scale())


def text_scale() -> float:
    return _game.persistent._phone_text_scale or 1.0


def theme_name() -> str:
    name = _game.persistent._phone_theme or cfg.default_theme
    if name not in cfg.themes:
        name = cfg.default_theme
    return name


def theme() -> dict[str, str]:
    return cfg.themes[theme_name()]


def color(key: str) -> str:
    t = theme()
    if key in t:
        return t[key]
    return cfg.themes["light"].get(key, "#f0f")


def tinted(image: Any, key_or_color: str) -> Transform:
    c = color(key_or_color) if not key_or_color.startswith("#") else key_or_color
    return Transform(image, matrixcolor=store.TintMatrix(c))  # pyright: ignore[reportUnknownMemberType, reportUnknownArgumentType]


def run_effects(effects: Optional[Iterable[Any]]) -> None:
    for effect in effects or ():
        renpy.run(effect)  # pyright: ignore[reportUnknownMemberType]


def check_picklable(obj: object, what: str) -> None:
    if not _config.developer:
        return

    try:
        _pickle_dumps(obj)
    except Exception as e:
        raise TypeError(
            "{} must be picklable to be saved (use a Ren'Py action such as "
            "SetVariable or Function with a module-level function): {!r} ({})".format(
                what, obj, e
            )
        )


def as_list(value: Any) -> list[Any]:
    if value is None:
        return []
    if isinstance(value, (list, tuple)):
        return list(cast("Iterable[Any]", value))
    return [value]


def mutated() -> None:
    renpy.retain_after_load()
    renpy.restart_interaction()


def init_only(what: str) -> None:
    if _config.developer and not renpy.is_init_phase():
        raise Exception(
            f"{what} must be called at init time (in a define or init python block); "
            "changes made while the game runs are not saved."
        )


if not _config.defer_styles:
    _config.defer_styles = True

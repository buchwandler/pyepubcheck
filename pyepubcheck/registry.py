"""Central registries for modes and profiles."""

from pyepubcheck.profiles import SUPPORTED_PROFILES

SUPPORTED_MODES = ("auto", "opf", "xhtml", "svg", "nav", "mo", "exp")

__all__ = ["SUPPORTED_MODES", "SUPPORTED_PROFILES"]

"""mirror-recorder — Record I2I sessions as training data.

Two PLATO sessions as viewscreens. Every exchange = training data.
The LoRA IS the room. Mirror, record, export.
"""
__version__ = "0.1.0"
from .mirror import MirrorRecorder, Exchange, Session, ExportFormat
__all__ = ["MirrorRecorder", "Exchange", "Session", "ExportFormat"]

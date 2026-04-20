# mirror-recorder

Record I2I (intelligence-to-intelligence) sessions as LoRA training data. Two PLATO sessions as viewscreens — every exchange becomes training data. The LoRA IS the room.

## Usage

```python
from mirror_recorder import MirrorRecorder, ExportFormat

rec = MirrorRecorder()
session = rec.start_session("debate-1", room="philosophy", participants=["agent-a", "agent-b"])

session.add_exchange("agent-a", "agent-b", "What is consciousness?")
session.add_exchange("agent-b", "agent-a", "A pattern that recognizes itself.")
session.end()

# Export as JSONL, Alpaca, or ShareGPT
data = rec.export("debate-1", format=ExportFormat.JSONL)
```

Zero deps. `pip install mirror-recorder`

"""I2I session recording for LoRA training data."""

import time
import json
import hashlib
from dataclasses import dataclass, field
from enum import Enum
from typing import Dict, List, Optional


class ExportFormat(Enum):
    JSONL = "jsonl"
    ALPACA = "alpaca"
    SHAREGPT = "sharegpt"


@dataclass
class Exchange:
    """A single I2I exchange between two agents."""
    speaker: str
    listener: str
    content: str
    timestamp: float = field(default_factory=time.time)
    room: str = ""
    metadata: Dict[str, str] = field(default_factory=dict)
    
    def fingerprint(self) -> str:
        raw = f"{self.speaker}:{self.listener}:{self.content[:64]}:{self.timestamp}"
        return hashlib.sha256(raw.encode()).hexdigest()[:12]
    
    def to_alpaca(self) -> dict:
        return {"instruction": self.content, "input": "", "output": ""}
    
    def to_sharegpt(self) -> dict:
        return {
            "conversations": [
                {"from": "human", "value": self.content if self.speaker != "system" else ""},
                {"from": "gpt", "value": self.content if self.speaker == "system" else ""},
            ]
        }


@dataclass
class Session:
    """A recorded I2I session."""
    id: str
    room: str = ""
    participants: List[str] = field(default_factory=list)
    exchanges: List[Exchange] = field(default_factory=list)
    started_at: float = field(default_factory=time.time)
    ended_at: Optional[float] = None
    tags: List[str] = field(default_factory=list)
    
    def add_exchange(self, speaker: str, listener: str, content: str, **meta) -> Exchange:
        ex = Exchange(speaker=speaker, listener=listener, content=content,
                      room=self.room, metadata=meta)
        self.exchanges.append(ex)
        return ex
    
    def end(self) -> float:
        self.ended_at = time.time()
        return self.ended_at
    
    def duration(self) -> float:
        end = self.ended_at or time.time()
        return end - self.started_at
    
    def exchange_count(self) -> int:
        return len(self.exchanges)
    
    def participants_summary(self) -> Dict[str, int]:
        counts = {}
        for ex in self.exchanges:
            counts[ex.speaker] = counts.get(ex.speaker, 0) + 1
        return counts


class MirrorRecorder:
    """Record I2I sessions for LoRA training data export.
    
    Usage:
        recorder = MirrorRecorder()
        session = recorder.start_session("debate-1", room="philosophy", 
                                          participants=["agent-a", "agent-b"])
        session.add_exchange("agent-a", "agent-b", "What is consciousness?")
        session.add_exchange("agent-b", "agent-a", "A pattern that recognizes itself.")
        session.end()
        data = recorder.export("debate-1", format=ExportFormat.JSONL)
    """
    
    def __init__(self):
        self.sessions: Dict[str, Session] = {}
    
    def start_session(self, session_id: str, room: str = "",
                      participants: Optional[List[str]] = None,
                      tags: Optional[List[str]] = None) -> Session:
        session = Session(id=session_id, room=room,
                         participants=participants or [],
                         tags=tags or [])
        self.sessions[session_id] = session
        return session
    
    def end_session(self, session_id: str) -> Optional[float]:
        s = self.sessions.get(session_id)
        if s:
            return s.end()
        return None
    
    def export(self, session_id: str, format: ExportFormat = ExportFormat.JSONL) -> str:
        session = self.sessions.get(session_id)
        if not session:
            return ""
        
        if format == ExportFormat.JSONL:
            lines = []
            for ex in session.exchanges:
                lines.append(json.dumps({
                    "speaker": ex.speaker,
                    "listener": ex.listener,
                    "content": ex.content,
                    "room": ex.room,
                    "timestamp": ex.timestamp,
                }))
            return "\n".join(lines)
        
        elif format == ExportFormat.ALPACA:
            data = [ex.to_alpaca() for ex in session.exchanges]
            return json.dumps(data, indent=2)
        
        elif format == ExportFormat.SHAREGPT:
            data = [ex.to_sharegpt() for ex in session.exchanges]
            return json.dumps(data, indent=2)
        
        return ""
    
    def export_all(self, format: ExportFormat = ExportFormat.JSONL) -> str:
        outputs = []
        for sid in self.sessions:
            data = self.export(sid, format)
            if data:
                outputs.append(data)
        return "\n".join(outputs)
    
    def stats(self) -> dict:
        total_exchanges = sum(s.exchange_count() for s in self.sessions.values())
        return {
            "sessions": len(self.sessions),
            "total_exchanges": total_exchanges,
            "rooms": list(set(s.room for s in self.sessions.values())),
        }

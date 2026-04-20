"""Tests for mirror-recorder."""
import json
import pytest
from mirror_recorder import MirrorRecorder, ExportFormat


def test_session_lifecycle():
    rec = MirrorRecorder()
    s = rec.start_session("s1", room="bridge", participants=["a", "b"])
    s.add_exchange("a", "b", "hello")
    s.add_exchange("b", "a", "hi back")
    s.end()
    assert s.exchange_count() == 2
    assert s.duration() > 0


def test_jsonl_export():
    rec = MirrorRecorder()
    s = rec.start_session("ex1")
    s.add_exchange("x", "y", "test message")
    data = rec.export("ex1", ExportFormat.JSONL)
    parsed = json.loads(data.split("\n")[0])
    assert parsed["speaker"] == "x"
    assert parsed["content"] == "test message"


def test_alpaca_export():
    rec = MirrorRecorder()
    s = rec.start_session("al1")
    s.add_exchange("human", "agent", "explain this")
    data = rec.export("al1", ExportFormat.ALPACA)
    parsed = json.loads(data)
    assert len(parsed) == 1
    assert "instruction" in parsed[0]


def test_participants_summary():
    rec = MirrorRecorder()
    s = rec.start_session("ps1")
    s.add_exchange("a", "b", "msg1")
    s.add_exchange("b", "a", "msg2")
    s.add_exchange("a", "b", "msg3")
    summary = s.participants_summary()
    assert summary["a"] == 2
    assert summary["b"] == 1


def test_exchange_fingerprint():
    from mirror_recorder import Exchange
    e1 = Exchange(speaker="a", listener="b", content="hello", timestamp=1000.0)
    e2 = Exchange(speaker="a", listener="b", content="hello", timestamp=1000.0)
    assert e1.fingerprint() == e2.fingerprint()


def test_export_all():
    rec = MirrorRecorder()
    rec.start_session("s1")
    rec.sessions["s1"].add_exchange("a", "b", "msg1")
    rec.start_session("s2")
    rec.sessions["s2"].add_exchange("c", "d", "msg2")
    data = rec.export_all(ExportFormat.JSONL)
    assert data.count("\n") == 1  # 2 lines separated by 1 newline

"""
Ancestral Memory — RMC Module 2
Memory with source ancestry, phase relation, confidence, and relevance tracking.
Every memory knows where it came from, what phase it belongs to, and how confident we are.
"""

import json
import uuid
from datetime import datetime, timezone
from typing import Dict, List, Optional
from pathlib import Path


class MemoryRecord:
    """A single memory with full ancestry tracking"""

    def __init__(self, content: str, phase: int, source: str,
                 confidence: float = 1.0, parent_id: Optional[str] = None,
                 tags: Optional[List[str]] = None):
        self.id = str(uuid.uuid4())[:8]
        self.content = content
        self.phase = phase
        self.source = source
        self.confidence = max(0.0, min(1.0, confidence))
        self.parent_id = parent_id      # ID of memory this came from
        self.tags = tags or []
        self.timestamp = datetime.now(timezone.utc).isoformat()
        self.access_count = 0

    def to_dict(self) -> Dict:
        return {
            'id': self.id,
            'content': self.content,
            'phase': self.phase,
            'source': self.source,
            'confidence': self.confidence,
            'parent_id': self.parent_id,
            'tags': self.tags,
            'timestamp': self.timestamp,
            'access_count': self.access_count,
        }

    @classmethod
    def from_dict(cls, d: Dict) -> 'MemoryRecord':
        m = cls(
            content=d['content'], phase=d['phase'],
            source=d['source'], confidence=d['confidence'],
            parent_id=d.get('parent_id'), tags=d.get('tags', [])
        )
        m.id = d['id']
        m.timestamp = d['timestamp']
        m.access_count = d.get('access_count', 0)
        return m


class AncestralMemory:
    """
    Memory store with ancestry tracking.
    Every memory knows its source, its phase, its parent memory, and its confidence.
    Retrieval is filtered by phase relevance and ranked by confidence.
    """

    def __init__(self, persist_path: Optional[str] = None):
        self.records: Dict[str, MemoryRecord] = {}
        self.persist_path = Path(persist_path) if persist_path else None
        if self.persist_path and self.persist_path.exists():
            self._load()

    # ── STORE ──────────────────────────────────────────────────────

    def store(self, content: str, phase: int, source: str,
              confidence: float = 1.0, parent_id: Optional[str] = None,
              tags: Optional[List[str]] = None) -> MemoryRecord:
        """Store a new memory record"""
        record = MemoryRecord(
            content=content, phase=phase, source=source,
            confidence=confidence, parent_id=parent_id, tags=tags
        )
        self.records[record.id] = record
        if self.persist_path:
            self._save()
        return record

    # ── RETRIEVE ───────────────────────────────────────────────────

    def retrieve(self, query: str, phase: Optional[int] = None,
                 min_confidence: float = 0.0,
                 limit: int = 5) -> List[MemoryRecord]:
        """
        Retrieve memories filtered by phase and confidence.
        Ranked by: phase match > confidence > recency.
        """
        query_lower = query.lower()
        candidates = []

        for record in self.records.values():
            # Confidence filter
            if record.confidence < min_confidence:
                continue
            # Text relevance — simple keyword match
            relevance = self._relevance(query_lower, record.content.lower())
            if relevance == 0:
                continue
            # Phase match bonus
            phase_match = (phase is not None and record.phase == phase)
            score = (relevance * record.confidence) + (0.3 if phase_match else 0)
            candidates.append((score, record))

        candidates.sort(key=lambda x: x[0], reverse=True)

        results = []
        for _, record in candidates[:limit]:
            record.access_count += 1
            results.append(record)

        return results

    def retrieve_by_phase(self, phase: int,
                          min_confidence: float = 0.0,
                          limit: int = 10) -> List[MemoryRecord]:
        """Retrieve all memories for a specific phase"""
        results = [
            r for r in self.records.values()
            if r.phase == phase and r.confidence >= min_confidence
        ]
        results.sort(key=lambda r: r.confidence, reverse=True)
        return results[:limit]

    def retrieve_ancestry(self, record_id: str) -> List[MemoryRecord]:
        """Get the full ancestry chain for a memory (parent → grandparent → ...)"""
        chain = []
        current_id = record_id
        seen = set()
        while current_id and current_id not in seen:
            seen.add(current_id)
            record = self.records.get(current_id)
            if not record:
                break
            chain.append(record)
            current_id = record.parent_id
        return chain

    def retrieve_descendants(self, record_id: str) -> List[MemoryRecord]:
        """Get all memories that descend from a given memory"""
        return [r for r in self.records.values() if r.parent_id == record_id]

    # ── UTILITY ────────────────────────────────────────────────────

    def get(self, record_id: str) -> Optional[MemoryRecord]:
        """Get a specific memory by ID"""
        return self.records.get(record_id)

    def all_records(self) -> List[MemoryRecord]:
        """Return all stored memories"""
        return list(self.records.values())

    def count(self) -> int:
        return len(self.records)

    def summary(self) -> Dict:
        """Summary of memory store state"""
        by_phase = {}
        for r in self.records.values():
            by_phase[r.phase] = by_phase.get(r.phase, 0) + 1
        return {
            'total': self.count(),
            'by_phase': by_phase,
            'avg_confidence': (
                sum(r.confidence for r in self.records.values()) / self.count()
                if self.records else 0.0
            )
        }

    # ── PERSISTENCE ────────────────────────────────────────────────

    def _save(self):
        if not self.persist_path:
            return
        self.persist_path.parent.mkdir(parents=True, exist_ok=True)
        data = {rid: r.to_dict() for rid, r in self.records.items()}
        self.persist_path.write_text(json.dumps(data, indent=2), encoding='utf-8')

    def _load(self):
        try:
            data = json.loads(self.persist_path.read_text(encoding='utf-8'))
            self.records = {rid: MemoryRecord.from_dict(d) for rid, d in data.items()}
        except Exception:
            self.records = {}

    # ── INTERNAL ───────────────────────────────────────────────────

    def _relevance(self, query: str, content: str) -> float:
        """Simple keyword relevance score (0.0 to 1.0)"""
        if not query.strip():
            return 0.0
        words = [w for w in query.split() if len(w) > 2]
        if not words:
            return 0.5 if query in content else 0.0
        matches = sum(1 for w in words if w in content)
        return matches / len(words)


if __name__ == "__main__":
    print("=== Ancestral Memory — Quick Test ===\n")

    mem = AncestralMemory()

    # Store a chain of related memories
    r1 = mem.store("User wants to build a web app", phase=3, source="session_1", confidence=0.9)
    r2 = mem.store("User is stuck on the login error", phase=4, source="session_1",
                   confidence=0.8, parent_id=r1.id)
    r3 = mem.store("User fixed the login error with JWT", phase=6, source="session_1",
                   confidence=0.95, parent_id=r2.id)
    mem.store("Project named: WebApp v1", phase=7, source="session_1", confidence=1.0)
    mem.store("User deployed to production", phase=8, source="session_2", confidence=0.9)

    print(f"Stored {mem.count()} memories\n")

    # Retrieve by query
    print("Query: 'login error'")
    results = mem.retrieve("login error", limit=3)
    for r in results:
        print(f"  [{r.id}] Phase {r.phase} | {r.confidence:.2f} | {r.content}")

    # Retrieve by phase
    print("\nAll Phase 3 (Desire) memories:")
    for r in mem.retrieve_by_phase(3):
        print(f"  [{r.id}] {r.content}")

    # Show ancestry chain
    print(f"\nAncestry of '{r3.content[:30]}...':")
    for r in mem.retrieve_ancestry(r3.id):
        print(f"  [{r.id}] Phase {r.phase} | {r.content}")

    # Summary
    print(f"\nMemory summary: {mem.summary()}")

"""
Output Renderer — RMC Module 5
Language is ONE projection of a manifest. Not the whole truth.

Takes a Manifest (from Module 4) and renders it into an output modality.
The renderer cannot invent meaning — it can only express what the manifest contains.

Modalities:
    language  — human-readable text (default)
    code      — executable code snippet
    glyph     — symbolic phase notation
    packet    — machine-readable JSON
    status    — dashboard state update
"""

from typing import Dict, Optional
from datetime import datetime, timezone


# ── RENDER RESULT ──────────────────────────────────────────────────

class RenderResult:
    """The output of rendering a manifest into a modality"""

    def __init__(self, modality: str, content: str,
                 manifest_id: str, faithful: bool,
                 faithfulness_note: str = ""):
        self.modality = modality
        self.content = content
        self.manifest_id = manifest_id
        self.faithful = faithful          # Does this render preserve the manifest?
        self.faithfulness_note = faithfulness_note
        self.timestamp = datetime.now(timezone.utc).isoformat()

    def to_dict(self) -> Dict:
        return {
            'modality': self.modality,
            'content': self.content,
            'manifest_id': self.manifest_id,
            'faithful': self.faithful,
            'faithfulness_note': self.faithfulness_note,
            'timestamp': self.timestamp,
        }


# ── LANGUAGE RENDERER ──────────────────────────────────────────────

class LanguageRenderer:
    """
    Renders a manifest into human-readable text.
    Applies phase-appropriate framing without changing the conclusion.
    """

    PHASE_FRAMES = {
        1: "{conclusion}",
        2: "Considering both sides: {conclusion}",
        3: "The goal here is: {conclusion}",
        4: "The issue is: {conclusion}",
        5: "There is significant uncertainty: {conclusion}",
        6: "Correction applied: {conclusion}",
        7: "Defined: {conclusion}",
        8: "{conclusion}",
        9: "Moving forward: {conclusion}",
    }

    DRIFT_PREFIXES = {
        "ALLOW": "",
        "WARN":  "[note: drift detected] ",
        "BLOCK": "[blocked] ",
    }

    def render(self, manifest: Dict) -> RenderResult:
        if manifest.get('projection_status') == 'BLOCKED':
            return RenderResult(
                modality="language",
                content="[output blocked — drift severity too high to render]",
                manifest_id=manifest.get('id', ''),
                faithful=True,
                faithfulness_note="Block preserved faithfully"
            )

        conclusion  = manifest.get('conclusion', '')
        phase       = manifest.get('phase', 1)
        drift       = manifest.get('drift_verdict', 'ALLOW')
        claim_type  = manifest.get('claim_type', 'assertion')
        confidence  = manifest.get('confidence', 1.0)

        # Apply phase frame
        frame = self.PHASE_FRAMES.get(phase, "{conclusion}")
        text = frame.format(conclusion=conclusion)

        # Apply drift prefix
        prefix = self.DRIFT_PREFIXES.get(drift, "")
        text = prefix + text

        # Low confidence qualifier
        if confidence < 0.5:
            text = f"[low confidence: {confidence:.2f}] {text}"

        # Check faithfulness — did we preserve the core conclusion?
        faithful = conclusion.split('[')[0].strip()[:30] in text
        note = "conclusion preserved" if faithful else "conclusion may have shifted"

        return RenderResult(
            modality="language",
            content=text,
            manifest_id=manifest.get('id', ''),
            faithful=faithful,
            faithfulness_note=note
        )


# ── CODE RENDERER ──────────────────────────────────────────────────

class CodeRenderer:
    """
    Renders a manifest into a code comment + stub.
    Used when the manifest's claim_type is 'instruction' or phase is 8.
    """

    def render(self, manifest: Dict) -> RenderResult:
        if manifest.get('projection_status') == 'BLOCKED':
            return RenderResult(
                modality="code",
                content="# [blocked — cannot render code from blocked manifest]",
                manifest_id=manifest.get('id', ''),
                faithful=True,
                faithfulness_note="Block preserved"
            )

        conclusion = manifest.get('conclusion', '')
        phase      = manifest.get('phase', 1)
        drift      = manifest.get('drift_verdict', 'ALLOW')
        mid        = manifest.get('id', 'unknown')

        drift_note = f"# drift: {drift}" if drift != "ALLOW" else ""

        code = (
            f"# Manifest: {mid} | Phase: {phase}\n"
            f"{drift_note}\n"
            f"# Conclusion: {conclusion}\n"
            f"def execute():\n"
            f"    # TODO: implement — {conclusion[:60]}\n"
            f"    pass\n"
        ).strip()

        return RenderResult(
            modality="code",
            content=code,
            manifest_id=mid,
            faithful=True,
            faithfulness_note="manifest id and conclusion preserved in comments"
        )


# ── GLYPH RENDERER ─────────────────────────────────────────────────

class GlyphRenderer:
    """
    Renders a manifest into symbolic phase notation.
    Compact symbolic representation for logging and analysis.
    Format: Φ{phase}[{drift}|{confidence:.1f}] → {conclusion_snippet}
    """

    PHASE_SYMBOLS = {
        1: "⊕",   # Initiation — spark
        2: "⇌",   # Polarity — bidirectional
        3: "→",   # Desire — direction
        4: "⊗",   # Friction — blocked
        5: "≈",   # Entropy — chaotic
        6: "↻",   # Grace — return
        7: "◉",   # Naming — sealed
        8: "⇑",   # Power — projection
        9: "∞",   # Evolution — recursive
    }

    DRIFT_SYMBOLS = {
        "ALLOW": "✓",
        "WARN":  "⚠",
        "BLOCK": "✗",
    }

    def render(self, manifest: Dict) -> RenderResult:
        phase      = manifest.get('phase', 1)
        drift      = manifest.get('drift_verdict', 'ALLOW')
        confidence = manifest.get('confidence', 1.0)
        conclusion = manifest.get('conclusion', '')
        mid        = manifest.get('id', '?')
        status     = manifest.get('projection_status', 'READY')

        phase_sym = self.PHASE_SYMBOLS.get(phase, "?")
        drift_sym = self.DRIFT_SYMBOLS.get(drift, "?")
        snippet   = conclusion[:40] + ('…' if len(conclusion) > 40 else '')

        glyph = f"Φ{phase}{phase_sym}[{drift_sym}|{confidence:.2f}|{status}] → {snippet}"

        return RenderResult(
            modality="glyph",
            content=glyph,
            manifest_id=mid,
            faithful=True,
            faithfulness_note="symbolic notation preserves phase, drift, confidence, conclusion"
        )


# ── PACKET RENDERER ────────────────────────────────────────────────

class PacketRenderer:
    """
    Renders a manifest as a machine-readable JSON packet.
    Used for inter-system communication and audit trails.
    """

    def render(self, manifest: Dict) -> RenderResult:
        import json
        packet = {
            'rmc_packet': True,
            'manifest_id': manifest.get('id'),
            'phase': manifest.get('phase'),
            'phase_name': manifest.get('phase_name'),
            'conclusion': manifest.get('conclusion'),
            'confidence': manifest.get('confidence'),
            'drift_verdict': manifest.get('drift_verdict'),
            'projection_status': manifest.get('projection_status'),
            'claim_type': manifest.get('claim_type'),
            'timestamp': manifest.get('timestamp'),
        }
        return RenderResult(
            modality="packet",
            content=json.dumps(packet, indent=2),
            manifest_id=manifest.get('id', ''),
            faithful=True,
            faithfulness_note="lossless manifest projection"
        )


# ── OUTPUT RENDERER (MAIN) ─────────────────────────────────────────

class OutputRenderer:
    """
    Main renderer — dispatches to the correct modality renderer.
    Default modality is language. Falls back to language if unknown.
    """

    def __init__(self):
        self.renderers = {
            'language': LanguageRenderer(),
            'code':     CodeRenderer(),
            'glyph':    GlyphRenderer(),
            'packet':   PacketRenderer(),
        }

    def render(self, manifest: Dict,
               modality: Optional[str] = None) -> RenderResult:
        """
        Render a manifest into the specified modality.
        If modality is None, uses manifest's first output_modality or language.
        """
        if modality is None:
            modalities = manifest.get('output_modalities', ['language'])
            modality = modalities[0] if modalities else 'language'

        renderer = self.renderers.get(modality, self.renderers['language'])
        return renderer.render(manifest)

    def render_all(self, manifest: Dict) -> Dict[str, RenderResult]:
        """Render a manifest in all available modalities"""
        results = {}
        for modality, renderer in self.renderers.items():
            results[modality] = renderer.render(manifest)
        return results


if __name__ == "__main__":
    print("=== Output Renderer — Quick Test ===\n")

    renderer = OutputRenderer()

    manifests = [
        {
            'id': 'abc001', 'phase': 3, 'phase_name': 'Desire',
            'conclusion': 'User wants to build a web application',
            'confidence': 0.87, 'drift_verdict': 'ALLOW',
            'projection_status': 'READY', 'claim_type': 'assertion',
            'output_modalities': ['language'], 'timestamp': '2026-01-01T00:00:00+00:00'
        },
        {
            'id': 'abc002', 'phase': 8, 'phase_name': 'Power',
            'conclusion': 'Deploy the application to production',
            'confidence': 0.9, 'drift_verdict': 'ALLOW',
            'projection_status': 'READY', 'claim_type': 'instruction',
            'output_modalities': ['code'], 'timestamp': '2026-01-01T00:00:00+00:00'
        },
        {
            'id': 'abc003', 'phase': 8, 'phase_name': 'Power',
            'conclusion': 'ship it now',
            'confidence': 0.4, 'drift_verdict': 'BLOCK',
            'projection_status': 'BLOCKED', 'claim_type': 'instruction',
            'output_modalities': ['language'], 'timestamp': '2026-01-01T00:00:00+00:00'
        },
        {
            'id': 'abc004', 'phase': 5, 'phase_name': 'Entropy',
            'conclusion': 'System state is unclear and drifting',
            'confidence': 0.45, 'drift_verdict': 'WARN',
            'projection_status': 'READY', 'claim_type': 'observation',
            'output_modalities': ['language'], 'timestamp': '2026-01-01T00:00:00+00:00'
        },
    ]

    for m in manifests:
        result = renderer.render(m)
        glyph  = renderer.render(m, modality='glyph')
        print(f"[{m['id']}] {glyph.content}")
        print(f"  → {result.content}")
        print(f"  faithful: {result.faithful}")
        print()

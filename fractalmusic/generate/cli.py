"""CLI: generate music from a fractal request and write MIDI + web JSON.

Usage:

    uv run python -m fractalmusic.generate.cli --tonic A --mode "Eólico" --length 16
"""

import argparse
import json
from pathlib import Path

from fractalmusic.generate.adapters import to_midi
from fractalmusic.generate.loop import JsonCorpus, StubExpert, research_loop
from fractalmusic.generate.types import GenerationRequest


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--tonic", required=True)
    parser.add_argument("--mode", required=True)
    parser.add_argument("--length", type=int, default=16)
    parser.add_argument(
        "--flavor", default="free", choices=["free", "penta-walk", "carta-progression"]
    )
    parser.add_argument("--corpus", default="patterns")
    parser.add_argument("--out", default="web/public/generated")
    parser.add_argument("--bpm", type=int, default=96)
    args = parser.parse_args()

    request = GenerationRequest(
        tonic=args.tonic,
        mode=args.mode,
        length_events=args.length,
        flavor=args.flavor,
    )
    corpus = JsonCorpus(root=Path(args.corpus))
    result = research_loop(request=request, expert=StubExpert(), corpus=corpus)

    out_dir = Path(args.out)
    out_dir.mkdir(parents=True, exist_ok=True)
    slug = f"{request.tonic}-{request.mode}-{request.flavor}".replace(" ", "")
    json_path = out_dir / f"{slug}.json"
    midi_path = out_dir / f"{slug}.mid"

    json_path.write_text(json.dumps(result.web_payload, ensure_ascii=False, indent=2))
    to_midi(events=result.events, path=midi_path, bpm=args.bpm)

    print(
        f"score={result.score.total:.3f} band={result.score.band} "
        f"events={len(result.events)} json={json_path} midi={midi_path}"
    )


if __name__ == "__main__":
    main()

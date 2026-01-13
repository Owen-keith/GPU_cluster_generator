import argparse
import json
import sys

from .spec_lookup import lookup_or_model


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        prog="gpu-cluster-generator",
        description="Prototype CLI: outputs strict JSON GPU specs for a given GPU model name.",
    )
    parser.add_argument(
        "--gpu",
        required=True,
        help='GPU model name, e.g. "NVIDIA H100" or "A100".',
    )
    args = parser.parse_args(argv)

    try:
        spec = lookup_or_model(args.gpu)
        # Print strict JSON only
        print(spec.model_dump_json(indent=2))
        return 0
    except Exception as e:
        # Still output JSON (so callers can rely on JSON always)
        err = {"error": str(e)}
        print(json.dumps(err, indent=2))
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
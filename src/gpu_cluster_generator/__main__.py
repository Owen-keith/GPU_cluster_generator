from __future__ import annotations

import argparse
import json
import sys

from .catalog_loader import load_networking_defaults, load_ra_patterns
from .ra_engine import recommend_pattern
from .spec_lookup import lookup_or_model


def _print_json(obj) -> None:
    print(json.dumps(obj, indent=2))


def cmd_gpu_spec(args: argparse.Namespace) -> int:
    spec = lookup_or_model(args.gpu)
    # GPUSpec is a Pydantic model -> dump to dict then print strict JSON
    _print_json(spec.model_dump())
    return 0


def cmd_ra_list(args: argparse.Namespace) -> int:
    catalog = load_ra_patterns()
    patterns = []
    for p in catalog.patterns:
        patterns.append(
            {
                "id": p.id,
                "c": p.c,
                "g": p.g,
                "n": p.n,
                "b_gbps_per_gpu": p.b_gbps_per_gpu,
                "node_count": {"min": p.node_count.min, "max": p.node_count.max},
                "tags": p.tags,
                "workload_fit": p.workload_fit,
            }
        )
    _print_json({"patterns": patterns})
    return 0


def cmd_ra_recommend(args: argparse.Namespace) -> int:
    ra_catalog = load_ra_patterns()
    net = load_networking_defaults()

    defaults = net.defaults or {}
    fabric = defaults.get("fabric", "ethernet")
    platform = defaults.get("platform", "spectrum-x")

    rec = recommend_pattern(
        ra_catalog.patterns,
        total_gpus=args.gpus,
        workload=args.workload,
        fabric=fabric,
        platform=platform,
    )

    _print_json(
        {
            "input": {"gpus": args.gpus, "workload": args.workload},
            "recommendation": {
                "pattern_id": rec.pattern_id,
                "nodes": rec.nodes,
                "gpus_per_node": rec.gpus_per_node,
                "b_gbps_per_gpu": rec.b_gbps_per_gpu,
                "fabric": rec.fabric,
                "platform": rec.platform,
            },
            "notes": rec.notes,
        }
    )
    return 0


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="gpu-cluster-generator",
        description="Prototype CLI: strict JSON outputs for GPU specs and RA pattern selection.",
    )
    sub = parser.add_subparsers(dest="command", required=True)

    # gpu ...
    p_gpu = sub.add_parser("gpu", help="GPU-related commands")
    sub_gpu = p_gpu.add_subparsers(dest="gpu_cmd", required=True)

    p_gpu_spec = sub_gpu.add_parser("spec", help="Lookup GPU specs (strict JSON).")
    p_gpu_spec.add_argument("--gpu", required=True, help='GPU model name, e.g. "NVIDIA H100".')
    p_gpu_spec.set_defaults(func=cmd_gpu_spec)

    # ra ...
    p_ra = sub.add_parser("ra", help="Reference-architecture related commands")
    sub_ra = p_ra.add_subparsers(dest="ra_cmd", required=True)

    p_ra_list = sub_ra.add_parser("list", help="List available RA patterns (strict JSON).")
    p_ra_list.set_defaults(func=cmd_ra_list)

    p_ra_rec = sub_ra.add_parser("recommend", help="Recommend an RA pattern for a GPU count (strict JSON).")
    p_ra_rec.add_argument("--gpus", type=int, required=True, help="Total GPUs desired, e.g. 128")
    p_ra_rec.add_argument(
        "--workload",
        choices=["training", "finetune", "inference"],
        required=True,
        help="Workload type",
    )
    p_ra_rec.set_defaults(func=cmd_ra_recommend)

    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)

    try:
        return int(args.func(args))
    except Exception as e:
        # Always JSON on stderr? We'll keep stdout JSON-only for callers.
        _print_json({"error": str(e)})
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
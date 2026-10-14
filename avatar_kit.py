#!/usr/bin/env python3
"""Local ComfyUI helper; does NOT include or implement the MultiTalk model.

This library is authored independently and uses only Python's standard library.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import time
import urllib.error
import urllib.request
import uuid

IMAGE_EXTENSIONS = {".png", ".jpg", ".jpeg"}
AUDIO_EXTENSIONS = {".wav", ".mp3"}


class AvatarKitError(ValueError):
    pass


def verify_file(path: Path, kind: str) -> Path:
    path = path.expanduser().resolve(strict=True)
    if not path.is_file() or path.stat().st_size == 0:
        raise AvatarKitError(f"Dosya bos veya normal dosya degil: {path}")
    ext = path.suffix.lower()
    allowed = IMAGE_EXTENSIONS if kind == "image" else AUDIO_EXTENSIONS
    if ext not in allowed:
        raise AvatarKitError(f"{kind} icin desteklenmeyen uzanti: {ext}; desteklenen: {sorted(allowed)}")
    with path.open("rb") as file:
        head = file.read(32)
    if kind == "image":
        if ext == ".png":
            ok = head.startswith(b"\x89PNG\r\n\x1a\n")
        else:
            ok = head.startswith(b"\xff\xd8\xff")
    else:
        if ext == ".wav":
            ok = head[:4] == b"RIFF" and head[8:12] == b"WAVE"
        else:
            ok = head.startswith(b"ID3") or (len(head) >= 2 and head[0] == 0xFF and (head[1] & 0xE0) == 0xE0)
    if not ok:
        raise AvatarKitError(f"Dosya basligi {ext} formatiyla uyusmuyor: {path}")
    return path


def media_info(path: Path, kind: str) -> dict:
    checked = verify_file(path, kind)
    info = {"file": str(checked), "kind": kind, "bytes": checked.stat().st_size}
    ffprobe = shutil.which("ffprobe")
    if ffprobe:
        process = subprocess.run(
            [ffprobe, "-v", "error", "-show_entries", "format=duration", "-of", "default=nokey=1:noprint_wrappers=1", str(checked)],
            capture_output=True, text=True, timeout=20, check=False,
        )
        if process.returncode == 0 and process.stdout.strip():
            try:
                info["duration_seconds"] = round(float(process.stdout.strip()), 2)
            except ValueError:
                pass
    return info


def stage_file(source: Path, input_dir: Path, kind: str) -> str:
    """Copies a file into local ComfyUI/input without touching upstream code."""
    checked = verify_file(source, kind)
    input_dir = input_dir.resolve()
    if not input_dir.is_dir():
        raise AvatarKitError(f"ComfyUI input klasoru bulunamadi: {input_dir}")
    digest = hashlib.sha256(checked.read_bytes()).hexdigest()[:12]
    filename = f"avatar_kit_{kind}_{digest}{checked.suffix.lower()}"
    destination = input_dir / filename
    if not destination.exists():
        shutil.copy2(checked, destination)
    return filename


def load_api_workflow(path: Path) -> dict:
    with path.expanduser().open("r", encoding="utf-8") as file:
        graph = json.load(file)
    if not isinstance(graph, dict) or not graph or "nodes" in graph:
        raise AvatarKitError("ComfyUI 'API format' workflow JSON gerekli; normal arayuz JSON'u degil.")
    for node_id, node in graph.items():
        if not isinstance(node, dict) or not isinstance(node.get("inputs"), dict) or not node.get("class_type"):
            raise AvatarKitError(f"API workflow dugumu gecersiz: {node_id}")
    return graph


def describe_workflow(graph: dict) -> list[str]:
    return [f"{key}: {value['class_type']} | inputs: {', '.join(value['inputs'])}" for key, value in graph.items()]


def apply_media(graph: dict, node_id: str, field: str, filename: str) -> None:
    if not node_id:
        raise AvatarKitError("Gerekli node ID belirtilmedi")
    if node_id not in graph:
        raise AvatarKitError(f"Workflow'da node bulunamadi: {node_id}")
    if field not in graph[node_id]["inputs"]:
        raise AvatarKitError(f"Node {node_id} icinde '{field}' alani yok. Alanlar: {list(graph[node_id]['inputs'])}")
    graph[node_id]["inputs"][field] = filename


def request_json(url: str, *, payload: dict | None = None, timeout: float = 15.0) -> dict:
    raw = None if payload is None else json.dumps(payload).encode("utf-8")
    req = urllib.request.Request(url, data=raw, headers={"Content-Type": "application/json"} if raw else {}, method="POST" if raw else "GET")
    with urllib.request.urlopen(req, timeout=timeout) as response:
        result = json.load(response)
    if not isinstance(result, dict):
        raise AvatarKitError("ComfyUI API beklenen JSON nesnesini dondurmedi")
    return result


def local_api_base(value: str) -> str:
    from urllib.parse import urlsplit
    parsed = urlsplit(value)
    if parsed.scheme != "http" or parsed.hostname not in {"localhost", "127.0.0.1", "::1"} or parsed.username or parsed.password or parsed.query or parsed.fragment or parsed.path not in {"", "/"}:
        raise AvatarKitError("Guvenlik icin yalnizca yerel http://127.0.0.1:8188 gibi bir adres kabul edilir")
    return value.rstrip("/")


def run(args: argparse.Namespace) -> int:
    if args.command == "check":
        print(json.dumps([media_info(Path(args.image), "image"), media_info(Path(args.audio), "audio")], ensure_ascii=False, indent=2))
        return 0

    if args.command == "inspect-workflow":
        for line in describe_workflow(load_api_workflow(Path(args.workflow))):
            print(line)
        return 0

    if args.command != "queue":
        raise AvatarKitError("Bilinmeyen komut")
    # Validate graph and *all* paths before file copying or network calls.
    graph = load_api_workflow(Path(args.workflow))
    image = verify_file(Path(args.image), "image")
    audio = verify_file(Path(args.audio), "audio")
    audio2 = verify_file(Path(args.audio2), "audio") if args.audio2 else None
    if (args.audio2 is None) != (args.audio2_node is None):
        raise AvatarKitError("Ikinci ses icin --audio2 ve --audio2-node birlikte gerekli")
    for node_id, field in [(args.image_node, args.image_field), (args.audio_node, args.audio_field)]:
        if node_id not in graph or field not in graph[node_id]["inputs"]:
            raise AvatarKitError(f"Node/alan eslesmesi yok: {node_id}:{field}")
    if audio2 and (args.audio2_node not in graph or args.audio2_field not in graph[args.audio2_node]["inputs"]):
        raise AvatarKitError(f"Node/alan eslesmesi yok: {args.audio2_node}:{args.audio2_field}")
    input_dir = Path(args.comfy_root).expanduser().resolve() / "input"
    image_name = stage_file(image, input_dir, "image")
    audio_name = stage_file(audio, input_dir, "audio")
    apply_media(graph, args.image_node, args.image_field, image_name)
    apply_media(graph, args.audio_node, args.audio_field, audio_name)
    if audio2:
        audio2_name = stage_file(audio2, input_dir, "audio")
        apply_media(graph, args.audio2_node, args.audio2_field, audio2_name)
    if args.dry_run:
        print(json.dumps({"staged": [image_name, audio_name], "workflow": graph}, ensure_ascii=False, indent=2))
        return 0
    base = local_api_base(args.url)
    result = request_json(base + "/prompt", payload={"prompt": graph, "client_id": str(uuid.uuid4())})
    prompt_id = result.get("prompt_id")
    if not prompt_id:
        raise AvatarKitError(f"ComfyUI prompt ID donmedi: {result}")
    print(f"Queue'ya eklendi: {prompt_id}")
    if not args.wait:
        return 0
    end = time.monotonic() + args.timeout
    while time.monotonic() < end:
        history = request_json(base + "/history/" + str(prompt_id))
        if str(prompt_id) in history:
            entry = history[str(prompt_id)]
            print(json.dumps({"prompt_id": prompt_id, "status": entry.get("status"), "outputs": entry.get("outputs")}, ensure_ascii=False, indent=2))
            if entry.get("status", {}).get("status_str") == "error":
                return 2
            return 0
        time.sleep(2)
    raise AvatarKitError(f"Zaman asimi: {args.timeout}s. Islem ComfyUI uzerinde suruyor olabilir; prompt_id: {prompt_id}")


def make_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="MultiTalk + ComfyUI icin yerel yardimci (model dahil degildir)")
    commands = parser.add_subparsers(dest="command", required=True)
    check = commands.add_parser("check", help="Goruntu ve ses dosyalarinin temel formatini kontrol et")
    check.add_argument("--image", required=True)
    check.add_argument("--audio", required=True)
    inspect = commands.add_parser("inspect-workflow", help="API export JSON node ve alanlarini yazdir")
    inspect.add_argument("--workflow", required=True)
    queue = commands.add_parser("queue", help="Yerel input dosyalarini kopyala ve ComfyUI workflow calistir")
    for option in ("workflow", "comfy-root", "image", "audio", "image-node", "audio-node"):
        queue.add_argument("--" + option, required=True)
    queue.add_argument("--image-field", default="image")
    queue.add_argument("--audio-field", default="audio")
    queue.add_argument("--audio2")
    queue.add_argument("--audio2-node")
    queue.add_argument("--audio2-field", default="audio")
    queue.add_argument("--url", default="http://127.0.0.1:8188")
    queue.add_argument("--dry-run", action="store_true")
    queue.add_argument("--wait", action="store_true")
    queue.add_argument("--timeout", type=int, default=1200)
    return parser


def main() -> int:
    try:
        return run(make_parser().parse_args())
    except (AvatarKitError, FileNotFoundError, OSError, urllib.error.URLError, json.JSONDecodeError, subprocess.TimeoutExpired) as exc:
        print(f"Hata: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())

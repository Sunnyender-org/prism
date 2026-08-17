#!/usr/bin/env python3
"""Prism local kernel: validate seeds, compile prose, harvest cards, self-check."""

from __future__ import annotations

import argparse
import base64
import json
import os
import random
import sys
import time
import urllib.error
import urllib.request
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SCHEMA = ROOT / "schema"
FIXTURES = ROOT / "evals" / "fixtures"
VAULT = ROOT / "vault" / "cards.jsonl"
DEMO_VAULT = ROOT / "vault" / "demo-cards.jsonl"
ENV_PATH = ROOT / ".env"
RENDERS = ROOT / "evals" / "renders"
DEFAULT_IMAGE_MODEL = "gpt-image-2"
DEFAULT_VISION_MODEL = "gpt-5.5"
DEFAULT_BASE_URL = "https://beefapi.com/v1"
DECODE_DIR = ROOT / "evals" / "decodes"
VISION_PREFERENCE = (
    "gpt-5.5",
    "gpt-5.4",
    "gpt-5.4-mini",
    "gpt-5.5-openai-compact",
    "gpt-5.6-sol",
    "gpt-5.6-luna",
    "gpt-5.6-terra",
)
IMAGE_MIME = {
    ".png": "image/png",
    ".jpg": "image/jpeg",
    ".jpeg": "image/jpeg",
    ".webp": "image/webp",
}
TYPE_ALIASES = {
    "人像": "portrait",
    "写真": "portrait",
    "海报": "poster",
    "版式": "poster",
    "字体": "poster",
    "产品": "product",
    "包装": "product",
    "静物": "product",
    "插画": "illustration",
    "动漫": "illustration",
    "二次元": "illustration",
    "赛璐璐": "illustration",
    "场景": "scene",
    "山水": "scene",
    "风景": "scene",
    "宫苑": "scene",
    "通用": "generic",
}
DECODE_SYSTEM = """你是 Prism 拆图器。只根据看见的画面填写视觉合同。
规则：
- 只输出 JSON，不要解释，不要 Markdown。
- 每个字段必须改变画面。禁止 8k、masterpiece、best quality、ultra detailed。
- 看不清的字写成「不可辨小字」，不许编品牌、价格或题跋全文。
- 脸部风格与总风格分开写。
- 动态负向必须以「避免」开头。
- 媒介写清绘画、摄影、三维或赛璐璐；不要写「电影静帧」。
- 可见的品牌名和标题按原样抄写。"""
AXES_PATH = SCHEMA / "axes.json"
TYPES_PATH = SCHEMA / "types.json"

FIELD_ORDER = [
    "frame_carrier",
    "core_style_contract",
    "image_type",
    "composition_rhythm",
    "subject_identity",
    "face_archetype",
    "face_shape",
    "eye_design",
    "body_silhouette",
    "pose_expression",
    "line_brush",
    "clothing_material",
    "material_print",
    "typography",
    "brand_mood",
    "lighting_color",
    "color_system",
    "clarity_occlusion",
    "face_negative_constraints",
    "dynamic_negative_constraints",
]

AXIS_FROM_FIELD = {
    "core_style_contract": "style",
    "brand_mood": "style",
    "line_brush": "style",
    "subject_identity": "subject",
    "face_archetype": "subject",
    "face_shape": "subject",
    "eye_design": "subject",
    "body_silhouette": "subject",
    "pose_expression": "motion",
    "composition_rhythm": "composition",
    "frame_carrier": "composition",
    "typography": "composition",
    "lighting_color": "color",
    "color_system": "color",
    "clothing_material": "style",
    "material_print": "style",
}

BANNED = ("8k", "masterpiece", "best quality", "ultra detailed", "trending on artstation")
LOCK_FIELDS = (
    "frame_carrier",
    "core_style_contract",
    "subject_identity",
    "face_archetype",
    "eye_design",
    "pose_expression",
    "line_brush",
    "typography",
)
NEGATIVE_FIELDS = ("face_negative_constraints", "dynamic_negative_constraints")


class PrismError(Exception):
    pass


def load_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def types_doc() -> dict:
    return load_json(TYPES_PATH)


def axes_doc() -> dict:
    return load_json(AXES_PATH)


def type_ids() -> list[str]:
    return [item["id"] for item in types_doc()["types"]]


def type_entry(type_id: str) -> dict:
    for item in types_doc()["types"]:
        if item["id"] == type_id:
            return item
    raise PrismError(f"unknown type: {type_id}")


def validate_seed(data: dict) -> dict:
    if not isinstance(data, dict) or "type" not in data or "fields" not in data:
        raise PrismError("seed must have type and fields")
    entry = type_entry(str(data["type"]))
    fields = data["fields"]
    if not isinstance(fields, dict):
        raise PrismError("fields must be an object")
    missing = [key for key in entry["fields"] if not str(fields.get(key) or "").strip()]
    if missing:
        raise PrismError(f"{entry['id']} missing fields: {', '.join(missing)}")
    return {"type": entry["id"], "fields": {k: str(v).strip() for k, v in fields.items() if str(v).strip()}}


def compile_fields(fields: dict[str, str]) -> str:
    body: list[str] = []
    negatives: list[str] = []
    for key in FIELD_ORDER:
        value = (fields.get(key) or "").strip()
        if not value:
            continue
        value = value.rstrip("。；;")
        if key in NEGATIVE_FIELDS:
            negatives.append(value)
        else:
            body.append(value)
    locks = []
    for key in LOCK_FIELDS:
        value = (fields.get(key) or "").strip()
        if value:
            locks.append(value.rstrip("。；;"))
    if locks:
        body.append("必须守住：" + "；".join(locks))
    chunks = body + negatives
    text = "。".join(chunks)
    if text and not text.endswith("。"):
        text += "。"
    lower = text.lower()
    if any(token in lower for token in BANNED):
        raise PrismError("compile refused: SD quality soup is banned")
    if "避免" not in text:
        raise PrismError("compile refused: missing 避免 / failure risks")
    return text


def harvest_cards(fields: dict[str, str], source: str = "") -> list[dict]:
    cards = []
    for key, axis in AXIS_FROM_FIELD.items():
        text = (fields.get(key) or "").strip()
        if not text:
            continue
        cards.append({"axis": axis, "text": text.rstrip("。"), "source": source, "field": key})
    return cards


def emit(payload: dict, as_json: bool) -> None:
    if as_json:
        print(json.dumps(payload, ensure_ascii=False, indent=2))
        return
    if "prompt" in payload:
        print(payload["prompt"])
        return
    print(json.dumps(payload, ensure_ascii=False, indent=2))


def cmd_types(_: argparse.Namespace) -> int:
    for item in types_doc()["types"]:
        print(f"{item['id']}\t{item['zh']}\t{len(item['fields'])} fields")
    return 0


def cmd_fields(args: argparse.Namespace) -> int:
    entry = type_entry(args.type)
    labels = types_doc()["field_labels"]
    print(f"{entry['id']} {entry['zh']}")
    for key in entry["fields"]:
        print(f"- {key}\t{labels.get(key, key)}")
    return 0


def load_seed(args: argparse.Namespace) -> tuple[dict, str]:
    if args.fixture:
        path = Path(args.fixture)
        return load_json(path), str(path)
    path = Path(args.json)
    return load_json(path), str(path)


def cmd_compile(args: argparse.Namespace) -> int:
    raw, source = load_seed(args)
    seed = validate_seed(raw)
    prompt = compile_fields(seed["fields"])
    cards = harvest_cards(seed["fields"], source=source)
    emit({"type": seed["type"], "source": source, "prompt": prompt, "cards": cards}, args.json)
    return 0


def cmd_validate(args: argparse.Namespace) -> int:
    raw, source = load_seed(args)
    seed = validate_seed(raw)
    compile_fields(seed["fields"])
    print(f"ok\t{seed['type']}\t{source}")
    return 0


def write_card(record: dict, vault: Path) -> None:
    vault.parent.mkdir(parents=True, exist_ok=True)
    with vault.open("a", encoding="utf-8") as handle:
        handle.write(json.dumps(record, ensure_ascii=False) + "\n")


def cmd_card_add(args: argparse.Namespace) -> int:
    axis_ids = {item["id"] for item in axes_doc()["axes"]}
    if args.axis not in axis_ids:
        raise PrismError(f"axis must be one of {sorted(axis_ids)}")
    record = {
        "axis": args.axis,
        "text": args.text.strip(),
        "source": args.source or "",
        "field": "",
        "created_at": datetime.now(timezone.utc).isoformat(),
    }
    write_card(record, Path(args.vault) if args.vault else VAULT)
    print(json.dumps(record, ensure_ascii=False))
    return 0


def cmd_harvest(args: argparse.Namespace) -> int:
    raw, source = load_seed(args)
    seed = validate_seed(raw)
    cards = harvest_cards(seed["fields"], source=source)
    vault = Path(args.vault) if args.vault else VAULT
    stamped = []
    for card in cards:
        card = {**card, "created_at": datetime.now(timezone.utc).isoformat()}
        if not args.dry_run:
            write_card(card, vault)
        stamped.append(card)
    emit({"count": len(stamped), "vault": str(vault), "cards": stamped}, True)
    return 0


def read_cards(vault: Path) -> list[dict]:
    if not vault.exists():
        return []
    cards = []
    for line in vault.read_text(encoding="utf-8").splitlines():
        if line.strip():
            cards.append(json.loads(line))
    return cards


def cmd_draw(args: argparse.Namespace) -> int:
    vault = Path(args.vault) if args.vault else VAULT
    cards = read_cards(vault)
    wanted = [part.strip() for part in args.axes.split(",") if part.strip()]
    if not wanted:
        wanted = [item["id"] for item in axes_doc()["axes"]]
    rng = random.Random(args.seed)
    picked = []
    missing = []
    for axis in wanted:
        pool = [card for card in cards if card.get("axis") == axis]
        if not pool:
            missing.append(axis)
            continue
        picked.append(rng.choice(pool))
    if args.json:
        emit({"picked": picked, "empty_axes": missing}, True)
        return 0 if picked else 1
    for card in picked:
        print(f"{card['axis']}\t{card['text']}")
    for axis in missing:
        print(f"{axis}\t(empty)", file=sys.stderr)
    return 0 if picked else 1


def fixture_paths() -> list[Path]:
    return sorted(FIXTURES.glob("*.json"))


def cmd_check(_: argparse.Namespace) -> int:
    errors: list[str] = []
    expected = ("portrait", "poster", "product", "illustration")
    counts: Counter[str] = Counter()
    for path in fixture_paths():
        try:
            seed = validate_seed(load_json(path))
            prompt = compile_fields(seed["fields"])
        except PrismError as exc:
            errors.append(f"{path.name}: {exc}")
            continue
        counts[seed["type"]] += 1
        if len(prompt) < 40:
            errors.append(f"{path.name}: prompt too short")
        cards = harvest_cards(seed["fields"])
        if len(cards) < 3:
            errors.append(f"{path.name}: harvest produced {len(cards)} cards")
    hard_dir = ROOT / "evals" / "hard-set"
    hard_jsons = sorted(hard_dir.glob("H*.json"))
    for path in hard_jsons:
        try:
            seed = validate_seed(load_json(path))
            compile_fields(seed["fields"])
        except PrismError as exc:
            errors.append(f"hard-set {path.name}: {exc}")
    for type_id in expected:
        if counts[type_id] < 5:
            errors.append(f"{type_id} fixtures {counts[type_id]} < 5")
    if errors:
        print("FAIL")
        for item in errors:
            print(item)
        return 1
    print("PASS")
    print(f"types={len(type_ids())} fixtures={sum(counts.values())} " + " ".join(f"{k}={counts[k]}" for k in expected))
    return 0


def load_image_creds() -> dict:
    if not ENV_PATH.exists():
        raise PrismError("missing .env (do not paste the key in chat)")
    raw = ENV_PATH.read_text(encoding="utf-8").strip()
    key = ""
    url = DEFAULT_BASE_URL
    model = DEFAULT_IMAGE_MODEL
    vision = DEFAULT_VISION_MODEL
    if raw.startswith("{"):
        obj = json.loads(raw)
        key = str(obj.get("key") or obj.get("api_key") or "")
        url = str(obj.get("url") or obj.get("base_url") or url)
        vision = str(obj.get("vision") or obj.get("vision_model") or vision)
        if obj.get("model") and "image" in str(obj.get("model")):
            model = str(obj.get("model"))
    else:
        for line in raw.splitlines():
            line = line.strip()
            if not line or line.startswith("#") or "=" not in line:
                continue
            name, value = line.split("=", 1)
            value = value.strip().strip('"').strip("'")
            if name in {"PRISM_IMAGE_API_KEY", "OPENAI_API_KEY", "BEEFAPI_API_KEY", "key"}:
                key = value
            elif name in {"PRISM_IMAGE_BASE_URL", "OPENAI_BASE_URL", "url"}:
                url = value
            elif name in {"PRISM_IMAGE_MODEL", "model"}:
                model = value
            elif name in {"PRISM_VISION_MODEL", "vision"}:
                vision = value
    if not key:
        raise PrismError(".env has no API key field")
    url = url.rstrip("/")
    if not url.endswith("/v1"):
        url = url + "/v1"
    return {
        "key": key,
        "base": url,
        "model": model or DEFAULT_IMAGE_MODEL,
        "vision": vision or DEFAULT_VISION_MODEL,
    }


def infer_size(seed: dict) -> str:
    blob = " ".join([seed.get("type", ""), *seed.get("fields", {}).values()]).lower()
    if any(token in blob for token in ("16:9", "超宽", "横版", "横幅", "横向", "宽幅", "宽画幅", "4:3")):
        return "1536x1024"
    if any(token in blob for token in ("9:16", "2:3", "3:4", "竖版")):
        return "1024x1536"
    return "1024x1536"


def api_request(creds: dict, path: str, payload: dict | None = None, timeout: int = 30, retries: int = 2) -> dict:
    url = creds["base"] + path
    data = None if payload is None else json.dumps(payload).encode("utf-8")
    req = urllib.request.Request(
        url,
        data=data,
        method="GET" if payload is None else "POST",
        headers={
            "Authorization": "Bearer " + creds["key"],
            "Content-Type": "application/json",
            "User-Agent": "prism-eval/0.1",
            "Accept": "application/json",
        },
    )
    try:
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            body = resp.read().decode("utf-8")
            return json.loads(body)
    except urllib.error.HTTPError as exc:
        detail = exc.read().decode("utf-8", "replace")[:400]
        if retries > 0 and exc.code in {502, 503, 504, 520, 522, 524}:
            time.sleep(3)
            return api_request(creds, path, payload, timeout=timeout, retries=retries - 1)
        raise PrismError(f"HTTP {exc.code} {path}: {detail}") from exc
    except (urllib.error.URLError, TimeoutError) as exc:
        if retries > 0:
            time.sleep(3)
            return api_request(creds, path, payload, timeout=timeout, retries=retries - 1)
        raise PrismError(f"network {path}: {exc}") from exc


def list_model_ids(creds: dict) -> list[str]:
    models = api_request(creds, "/models")
    ids = []
    for item in models.get("data") or []:
        mid = item.get("id") if isinstance(item, dict) else None
        if mid:
            ids.append(mid)
    return ids


def extract_json_object(text: str) -> dict:
    raw = (text or "").strip()
    if not raw:
        raise PrismError("empty model response")
    if raw.startswith("```"):
        lines = raw.splitlines()
        if lines and lines[0].startswith("```"):
            lines = lines[1:]
        if lines and lines[-1].strip().startswith("```"):
            lines = lines[:-1]
        raw = "\n".join(lines).strip()
    try:
        obj = json.loads(raw)
        if isinstance(obj, dict):
            return obj
    except json.JSONDecodeError:
        pass
    start = raw.find("{")
    end = raw.rfind("}")
    if start >= 0 and end > start:
        try:
            obj = json.loads(raw[start : end + 1])
        except json.JSONDecodeError as exc:
            raise PrismError("model response is not a JSON object") from exc
        if isinstance(obj, dict):
            return obj
    raise PrismError("model response is not a JSON object")


def normalize_type_id(value: str) -> str:
    text = (value or "").strip().lower()
    known = set(type_ids())
    if text in known:
        return text
    for token, type_id in TYPE_ALIASES.items():
        if token in text:
            return type_id
    return "generic"


def encode_image(path: Path) -> tuple[str, str]:
    path = path.expanduser()
    if not path.is_file():
        raise PrismError(f"image not found: {path}")
    mime = IMAGE_MIME.get(path.suffix.lower())
    if not mime:
        raise PrismError(f"unsupported image type: {path.suffix}")
    data = path.read_bytes()
    if len(data) > 900_000:
        data, mime = downscale_image(path)
    return base64.b64encode(data).decode("ascii"), mime


def downscale_image(path: Path) -> tuple[bytes, str]:
    import subprocess
    import tempfile

    handle, tmp = tempfile.mkstemp(suffix=".jpg")
    os.close(handle)
    dest = Path(tmp)
    try:
        subprocess.run(
            ["sips", "-Z", "1536", "-s", "format", "jpeg", str(path), "--out", str(dest)],
            check=True,
            capture_output=True,
        )
        data = dest.read_bytes()
        if not data:
            raise PrismError("sips produced empty jpeg")
        return data, "image/jpeg"
    except (FileNotFoundError, subprocess.CalledProcessError) as exc:
        data = path.read_bytes()
        mime = IMAGE_MIME.get(path.suffix.lower(), "image/png")
        if len(data) > 4_000_000:
            raise PrismError("image too large and resize failed") from exc
        return data, mime
    finally:
        dest.unlink(missing_ok=True)


def message_text(result: dict) -> str:
    choice = (result.get("choices") or [None])[0] or {}
    message = choice.get("message") or {}
    content = message.get("content")
    if isinstance(content, str):
        return content
    if isinstance(content, list):
        parts = []
        for item in content:
            if isinstance(item, str):
                parts.append(item)
            elif isinstance(item, dict):
                parts.append(str(item.get("text") or ""))
        return "".join(parts)
    return ""


def chat_vision(creds: dict, prompt: str, image_b64: str, mime: str, model: str) -> str:
    payload = {
        "model": model,
        "messages": [
            {"role": "system", "content": DECODE_SYSTEM},
            {
                "role": "user",
                "content": [
                    {"type": "text", "text": prompt},
                    {
                        "type": "image_url",
                        "image_url": {"url": f"data:{mime};base64,{image_b64}"},
                    },
                ],
            },
        ],
    }
    result = api_request(creds, "/chat/completions", payload, timeout=180)
    text = message_text(result).strip()
    if not text:
        raise PrismError("vision response empty")
    return text


def field_spec(type_id: str) -> str:
    entry = type_entry(type_id)
    labels = types_doc()["field_labels"]
    return "\n".join(f"- {key}：{labels.get(key, key)}" for key in entry["fields"])


def classify_prompt() -> str:
    ids = ", ".join(type_ids())
    return (
        "判断这张图的主类型。只从这些 id 里选一个："
        f"{ids}。\n"
        "portrait=真人时尚写真，不是动画；poster=文字是结构；product=商品主体；"
        "illustration=插画/动漫/赛璐璐，即使是脸部特写也选这个；"
        "scene=风景/宫苑/大场景；generic=都不像。\n"
        '只输出 JSON：{"type":"...","reason":"..."}'
    )


def fill_prompt(type_id: str) -> str:
    return (
        f"按类型 {type_id} 填写字段。每个值用中文短语，一两句。\n"
        "image_type 必须写明竖版或横版，以及 9:16 / 2:3 / 3:4 / 4:3 / 16:9 之一。\n"
        f"{field_spec(type_id)}\n"
        "dynamic_negative_constraints 必须以「避免」开头。"
        "face_negative_constraints 若存在也必须以「避免」开头。\n"
        f'只输出 JSON：{{"type":"{type_id}","fields":{{...}},"notes":"..."}}'
    )


def repair_prompt(type_id: str, error: str) -> str:
    return (
        f"上一份 JSON 不能通过校验：{error}。\n"
        f"按类型 {type_id} 补全缺失字段，删掉空值。\n"
        f"{field_spec(type_id)}\n"
        f'只输出完整 JSON：{{"type":"{type_id}","fields":{{...}}}}'
    )


def coerce_seed(raw: dict, fallback_type: str) -> dict:
    reserved = {"type", "notes", "reason"}
    if isinstance(raw.get("fields"), dict):
        fields = raw["fields"]
    else:
        fields = {key: value for key, value in raw.items() if key not in reserved}
    cleaned = {}
    for key, value in fields.items():
        if isinstance(value, str):
            text = value.strip()
        else:
            text = json.dumps(value, ensure_ascii=False)
        if text:
            cleaned[key] = text
    return {"type": normalize_type_id(str(raw.get("type") or fallback_type)), "fields": cleaned}


def resolve_image_path(args: argparse.Namespace) -> Path:
    if getattr(args, "image", None):
        path = Path(args.image)
        return path if path.is_absolute() else ROOT / path
    raw = load_json(Path(args.fixture))
    source = raw.get("source_image")
    if not source:
        raise PrismError("fixture has no source_image")
    path = Path(str(source))
    return path if path.is_absolute() else ROOT / path


def decode_image(path: Path, type_id: str = "auto", model: str | None = None) -> dict:
    creds = load_image_creds()
    vision = model or creds.get("vision") or DEFAULT_VISION_MODEL
    image_b64, mime = encode_image(path)
    notes = ""
    chosen = (type_id or "auto").strip().lower()
    if chosen in {"", "auto"}:
        classified = extract_json_object(chat_vision(creds, classify_prompt(), image_b64, mime, vision))
        chosen = normalize_type_id(str(classified.get("type") or ""))
        notes = str(classified.get("reason") or "")
    else:
        chosen = normalize_type_id(chosen)
    filled = extract_json_object(chat_vision(creds, fill_prompt(chosen), image_b64, mime, vision))
    seed = coerce_seed(filled, chosen)
    try:
        seed = validate_seed(seed)
        compile_fields(seed["fields"])
    except PrismError as exc:
        repaired = extract_json_object(
            chat_vision(creds, repair_prompt(chosen, str(exc)), image_b64, mime, vision)
        )
        seed = validate_seed(coerce_seed(repaired, chosen))
        compile_fields(seed["fields"])
    prompt = compile_fields(seed["fields"])
    try:
        rel = str(path.resolve().relative_to(ROOT))
    except ValueError:
        rel = str(path)
    return {
        "type": seed["type"],
        "fields": seed["fields"],
        "prompt": prompt,
        "notes": notes,
        "vision": vision,
        "source_image": rel,
    }


def cmd_doctor(_: argparse.Namespace) -> int:
    creds = load_image_creds()
    ids = list_model_ids(creds)
    has_image = creds["model"] in ids or any("image-2" in mid for mid in ids)
    has_vision = creds["vision"] in ids or any(mid in ids for mid in VISION_PREFERENCE)
    print(f"base={creds['base']}")
    print(f"model={creds['model']} visible={has_image} listed={len(ids)}")
    print(f"vision={creds['vision']} visible={has_vision}")
    if not has_image:
        print("warning: gpt-image-2 not in /v1/models", file=sys.stderr)
        return 2
    if not has_vision:
        print("warning: vision model not in /v1/models", file=sys.stderr)
        return 2
    return 0


def cmd_decode(args: argparse.Namespace) -> int:
    path = resolve_image_path(args)
    result = decode_image(path, type_id=args.type, model=args.model or None)
    seed = {
        "type": result["type"],
        "source_image": result["source_image"],
        "fields": result["fields"],
    }
    if args.out:
        dest = Path(args.out)
        dest.parent.mkdir(parents=True, exist_ok=True)
        dest.write_text(json.dumps(seed, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        result["out"] = str(dest if dest.is_absolute() else dest)
    emit(
        {
            "type": result["type"],
            "vision": result["vision"],
            "notes": result["notes"],
            "source_image": result["source_image"],
            "fields": result["fields"],
            "prompt": result["prompt"],
            "out": result.get("out", ""),
        },
        args.json,
    )
    return 0


def save_generation(result: dict, dest: Path) -> Path:
    dest.parent.mkdir(parents=True, exist_ok=True)
    data = (result.get("data") or [None])[0] or {}
    if data.get("b64_json"):
        dest.write_bytes(base64.b64decode(data["b64_json"]))
        return dest
    url = data.get("url")
    if not url:
        raise PrismError("image response missing b64_json and url")
    req = urllib.request.Request(url)
    with urllib.request.urlopen(req, timeout=60) as resp:
        dest.write_bytes(resp.read())
    return dest


def render_seed(path: Path, dest: Path | None = None, quality: str = "medium") -> dict:
    seed = validate_seed(load_json(path))
    prompt = compile_fields(seed["fields"])
    creds = load_image_creds()
    size = infer_size(seed)
    payload = {
        "model": creds["model"],
        "prompt": prompt,
        "n": 1,
        "size": size,
        "quality": quality,
    }
    result = api_request(creds, "/images/generations", payload, timeout=180)
    if dest is None:
        dest = RENDERS / (path.stem + ".png")
    saved = save_generation(result, dest)
    return {"id": saved.stem, "type": seed["type"], "size": size, "out": str(saved.relative_to(ROOT))}


def cmd_render(args: argparse.Namespace) -> int:
    if args.all_hard:
        paths = sorted((ROOT / "evals" / "hard-set").glob("H*.json"))
    else:
        paths = [Path(args.fixture)]
    suffix = args.suffix or ""
    if suffix and not suffix.startswith(("-", "_")):
        suffix = "-" + suffix
    rows = []
    for path in paths:
        dest = RENDERS / f"{path.stem}{suffix}.png" if suffix else None
        print(f"render {path.name} -> {path.stem}{suffix or ''}.png ...", flush=True)
        row = render_seed(path, dest=dest, quality=args.quality)
        print(f"  -> {row['out']} {row['size']}", flush=True)
        rows.append(row)
    emit({"renders": rows}, True)
    return 0


def cmd_demo_vault(_: argparse.Namespace) -> int:
    cards: list[dict] = []
    for path in fixture_paths():
        seed = validate_seed(load_json(path))
        cards.extend(harvest_cards(seed["fields"], source=str(path.relative_to(ROOT))))
    DEMO_VAULT.parent.mkdir(parents=True, exist_ok=True)
    DEMO_VAULT.write_text(
        "".join(json.dumps(card, ensure_ascii=False) + "\n" for card in cards),
        encoding="utf-8",
    )
    print(f"wrote {len(cards)} cards -> {DEMO_VAULT.relative_to(ROOT)}")
    return 0


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="prism")
    sub = parser.add_subparsers(dest="cmd", required=True)

    sub.add_parser("types").set_defaults(func=cmd_types)

    fields = sub.add_parser("fields")
    fields.add_argument("type")
    fields.set_defaults(func=cmd_fields)

    def add_source(cmd: argparse.ArgumentParser) -> None:
        source = cmd.add_mutually_exclusive_group(required=True)
        source.add_argument("--fixture")
        source.add_argument("--json")

    compile_cmd = sub.add_parser("compile")
    add_source(compile_cmd)
    compile_cmd.add_argument("--as-json", action="store_true", dest="json")
    compile_cmd.set_defaults(func=cmd_compile)

    validate_cmd = sub.add_parser("validate")
    add_source(validate_cmd)
    validate_cmd.set_defaults(func=cmd_validate)

    add = sub.add_parser("card-add")
    add.add_argument("--axis", required=True)
    add.add_argument("--text", required=True)
    add.add_argument("--source", default="")
    add.add_argument("--vault", default="")
    add.set_defaults(func=cmd_card_add)

    harvest = sub.add_parser("harvest")
    add_source(harvest)
    harvest.add_argument("--vault", default="")
    harvest.add_argument("--dry-run", action="store_true")
    harvest.set_defaults(func=cmd_harvest)

    draw = sub.add_parser("draw")
    draw.add_argument("--axes", default="style,subject,composition,color,motion")
    draw.add_argument("--seed", type=int, default=None)
    draw.add_argument("--vault", default="")
    draw.add_argument("--as-json", action="store_true", dest="json")
    draw.set_defaults(func=cmd_draw)

    sub.add_parser("check").set_defaults(func=cmd_check)
    sub.add_parser("demo-vault").set_defaults(func=cmd_demo_vault)
    sub.add_parser("doctor").set_defaults(func=cmd_doctor)

    decode = sub.add_parser("decode")
    decode_src = decode.add_mutually_exclusive_group(required=True)
    decode_src.add_argument("--image")
    decode_src.add_argument("--fixture")
    decode.add_argument("--type", default="auto")
    decode.add_argument("--model", default="")
    decode.add_argument("--out", default="")
    decode.add_argument("--as-json", action="store_true", dest="json")
    decode.set_defaults(func=cmd_decode)

    render = sub.add_parser("render")
    source = render.add_mutually_exclusive_group(required=True)
    source.add_argument("--fixture")
    source.add_argument("--all-hard", action="store_true")
    render.add_argument("--quality", default="medium", choices=["low", "medium", "high"])
    render.add_argument("--suffix", default="", help="append to output stem, e.g. v2 -> -v2.png")
    render.set_defaults(func=cmd_render)
    return parser


def main() -> int:
    try:
        args = build_parser().parse_args()
        return args.func(args)
    except PrismError as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())

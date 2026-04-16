# -*- coding: utf-8 -*-
"""
Tesseract OCR: default is balanced speed (2 preprocess × 2 PSM). Set TESSERACT_FULL_OCR=1
for 4×3 max-recall passes. TESSERACT_FAST=1 is single-pass (fastest, lowest recall).
"""

from __future__ import annotations

import os
import re
import shutil
import subprocess
from typing import Callable

import numpy as np
from PIL import Image

# Defaults (override with env)
_DEFAULT_DPI = 400
_DEFAULT_LANGS_TRY = ("sin+eng", "sin", "eng")


def _env_int(name: str, default: int) -> int:
    try:
        return int(os.getenv(name, str(default)).strip())
    except ValueError:
        return default


def _env_truthy(name: str, default: bool = False) -> bool:
    v = (os.getenv(name) or "").strip().lower()
    if not v:
        return default
    return v in ("1", "true", "yes", "on")


def resolve_tesseract_cmd() -> str | None:
    """tesseract on PATH, or TESSERACT_CMD / TESSERACT_PATH, or legacy installer paths."""
    env = (os.getenv("TESSERACT_CMD") or os.getenv("TESSERACT_PATH") or "").strip()
    if env and os.path.isfile(env):
        return env
    path = shutil.which("tesseract")
    if path:
        return path
    legacy = os.path.join(os.environ.get("LOCAL_DEPS_DIR", r"D:\PROJECTS\New folder"), "tesseract.exe")
    if os.path.isfile(legacy):
        return legacy
    return None


def resolve_poppler_path() -> str | None:
    p = (os.getenv("POPPLER_PATH") or "").strip()
    if p and os.path.isdir(p):
        return p
    legacy = os.path.join(os.environ.get("LOCAL_DEPS_DIR", r"D:\PROJECTS\New folder"), r"poppler-24.02.0\Library\bin")
    if os.path.isdir(legacy):
        return legacy
    return None


def list_tesseract_langs(tesseract_exe: str) -> set[str]:
    try:
        kwargs: dict = {
            "capture_output": True,
            "text": True,
            "timeout": 15,
        }
        if os.name == "nt" and hasattr(subprocess, "CREATE_NO_WINDOW"):
            kwargs["creationflags"] = subprocess.CREATE_NO_WINDOW
        r = subprocess.run([tesseract_exe, "--list-langs"], **kwargs)
        if r.returncode != 0:
            return set()
        lines = (r.stdout or r.stderr or "").strip().splitlines()
        out = set()
        for line in lines:
            line = line.strip()
            if line and not line.startswith("List of available"):
                out.add(line)
        return out
    except Exception:
        return set()


def pick_lang_string(tesseract_exe: str) -> str:
    available = list_tesseract_langs(tesseract_exe)
    for cand in _DEFAULT_LANGS_TRY:
        parts = cand.split("+")
        if all(p in available for p in parts):
            return cand
    if "sin" in available:
        return "sin"
    if "eng" in available:
        return "eng"
    return "eng"


def resolve_lang_for_ocr(tesseract_exe: str, language: str | None) -> str:
    """TESSERACT_LANG env wins; else explicit `language`; else best combo (sin+eng)."""
    env = (os.getenv("TESSERACT_LANG") or "").strip()
    if env:
        return env
    if language and str(language).strip().lower() not in ("", "auto"):
        return language.strip()
    return pick_lang_string(tesseract_exe)


def _upscale_gray(gray: np.ndarray, scale: float) -> np.ndarray:
    import cv2

    if scale <= 1.001:
        return gray
    h, w = gray.shape[:2]
    return cv2.resize(gray, (int(w * scale), int(h * scale)), interpolation=cv2.INTER_CUBIC)


def preprocess_variants_speed(rgb: Image.Image, upscale: float) -> list[tuple[str, Image.Image]]:
    """Two fast preprocess paths (~4 Tesseract calls with 2 PSMs vs 12+ for full)."""
    import cv2

    arr = np.array(rgb.convert("RGB"))
    bgr = cv2.cvtColor(arr, cv2.COLOR_RGB2BGR)
    gray = cv2.cvtColor(bgr, cv2.COLOR_BGR2GRAY)
    gray = _upscale_gray(gray, upscale)
    den = cv2.fastNlMeansDenoising(gray, None, 10, 7, 21)
    ath = cv2.adaptiveThreshold(
        den, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY, 15, 3
    )
    clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8, 8))
    mild = clahe.apply(gray)
    return [
        ("adaptive_bw", Image.fromarray(ath)),
        ("gray_clahe", Image.fromarray(mild)),
    ]


def preprocess_variants(rgb: Image.Image, upscale: float) -> list[tuple[str, Image.Image]]:
    """Named preprocess pipelines for diverse scans (faint ink, noise, photos)."""
    import cv2

    arr = np.array(rgb.convert("RGB"))
    bgr = cv2.cvtColor(arr, cv2.COLOR_RGB2BGR)
    gray = cv2.cvtColor(bgr, cv2.COLOR_BGR2GRAY)
    gray = _upscale_gray(gray, upscale)

    variants: list[tuple[str, Image.Image]] = []

    # 1) Adaptive (current pipeline style)
    den = cv2.fastNlMeansDenoising(gray, None, 10, 7, 21)
    ath = cv2.adaptiveThreshold(
        den, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY, 15, 3
    )
    variants.append(("adaptive_bw", Image.fromarray(ath)))

    # 2) Otsu global threshold — sometimes recovers text adaptive blurs out
    _, otsu = cv2.threshold(den, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
    variants.append(("otsu_bw", Image.fromarray(otsu)))

    # 3) Mild contrast + no harsh binarization — thin strokes / light print
    clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8, 8))
    mild = clahe.apply(gray)
    variants.append(("gray_clahe", Image.fromarray(mild)))

    # 4) Inverted adaptive — white text / dark background regions
    inv = cv2.bitwise_not(ath)
    variants.append(("inv_adaptive", Image.fromarray(inv)))

    return variants


def _tesseract_psm_variants(speed: bool) -> list[str]:
    """PSM modes; speed mode uses fewer passes."""
    raw = (os.getenv("TESSERACT_PSM_LIST") or "").strip()
    if raw:
        return [x.strip() for x in raw.split(",") if x.strip()]
    if speed:
        return ["6", "4"]
    return ["6", "4", "3"]


def merge_ocr_lines(primary: str, *others: str) -> str:
    """Keep order from longest block; append lines only seen in other passes (catch misses)."""
    texts = [primary] + list(others)
    texts = [t for t in texts if t and t.strip()]
    if not texts:
        return ""
    base = max(texts, key=len)
    seen = {ln.strip() for ln in base.splitlines() if ln.strip()}
    extra: list[str] = []
    for t in texts:
        if t == base:
            continue
        for ln in t.splitlines():
            s = ln.strip()
            if len(s) < 2:
                continue
            if s in seen:
                continue
            # skip near-duplicates: same line with minor OCR noise
            if any(_line_similar(s, x) for x in seen):
                continue
            seen.add(s)
            extra.append(ln.rstrip())
    if not extra:
        return base
    return base.rstrip() + "\n" + "\n".join(extra)


def _line_similar(a: str, b: str) -> bool:
    if a == b:
        return True
    if len(a) < 4 or len(b) < 4:
        return False
    shorter, longer = (a, b) if len(a) < len(b) else (b, a)
    return shorter in longer or _ratio_common_prefix(a, b) > 0.92


def _ratio_common_prefix(a: str, b: str) -> float:
    n = min(len(a), len(b))
    if n == 0:
        return 0.0
    same = sum(1 for i in range(n) if a[i] == b[i])
    return same / n


def ocr_pil_image_max_recall(
    pil: Image.Image,
    pytesseract_module,
    lang: str,
    tesseract_cmd: str | None,
    log: Callable[[str], None] | None = None,
) -> str:
    """
    Merge outputs from multiple preprocess × PSM runs.
    - TESSERACT_FAST=1: one pass (fastest).
    - Default: 2×2 balanced (TESSERACT_FULL_OCR unset).
    - TESSERACT_FULL_OCR=1: full 4×3 recall.
    """
    if tesseract_cmd:
        pytesseract_module.pytesseract.tesseract_cmd = tesseract_cmd

    if _env_truthy("TESSERACT_FAST", False):
        import cv2

        arr = np.array(pil.convert("RGB"))
        bgr = cv2.cvtColor(arr, cv2.COLOR_RGB2BGR)
        gray = cv2.cvtColor(bgr, cv2.COLOR_BGR2GRAY)
        den = cv2.fastNlMeansDenoising(gray, None, 10, 7, 21)
        ath = cv2.adaptiveThreshold(
            den, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY, 15, 3
        )
        pil_one = Image.fromarray(ath)
        oem = os.getenv("TESSERACT_OEM", "3")
        return pytesseract_module.image_to_string(
            pil_one, lang=lang, config=f"--oem {oem} --psm 6"
        )

    # Default: speed OCR (2×2 passes). Set TESSERACT_FULL_OCR=1 for 4×3 max-recall.
    full_ocr = _env_truthy("TESSERACT_FULL_OCR", False)
    speed = not full_ocr
    default_up = "1.0" if speed else "1.25"
    try:
        upscale = float(os.getenv("TESSERACT_UPSCALE", default_up))
    except ValueError:
        upscale = float(default_up)
    oem = os.getenv("TESSERACT_OEM", "3")
    variants = (
        preprocess_variants_speed(pil, upscale) if speed else preprocess_variants(pil, upscale)
    )
    psms = _tesseract_psm_variants(speed)
    outputs: list[str] = []

    for vname, vpil in variants:
        for psm in psms:
            cfg = f"--oem {oem} --psm {psm}"
            extra = (os.getenv("TESSERACT_EXTRA_CONFIG") or "").strip()
            if extra:
                cfg = f"{cfg} {extra}"
            try:
                txt = pytesseract_module.image_to_string(vpil, lang=lang, config=cfg)
                if txt and txt.strip():
                    outputs.append(txt)
            except Exception as e:
                if log:
                    log(f"[Tesseract] skip {vname} psm={psm}: {e}")

    if not outputs:
        return ""

    # Merge pairwise from longest downward
    outputs.sort(key=len, reverse=True)
    merged = outputs[0]
    for o in outputs[1:]:
        merged = merge_ocr_lines(merged, o)
    return merged


def run_tesseract_on_pdf_pages(
    pdf_path: str,
    language: str | None = None,
    progress_callback=None,
) -> list[str]:
    """
    PDF → images → robust Tesseract per page. Returns list of page strings.
    """
    import pytesseract
    from pdf2image import convert_from_path

    dpi = _env_int("TESSERACT_DPI", _DEFAULT_DPI)
    tesseract_cmd = resolve_tesseract_cmd()
    if not tesseract_cmd:
        raise RuntimeError("Tesseract executable not found. Set TESSERACT_CMD or install Tesseract and add to PATH.")

    lang = resolve_lang_for_ocr(tesseract_cmd, language)
    poppler = resolve_poppler_path()

    kw = {"dpi": dpi, "fmt": "png"}
    if poppler:
        kw["poppler_path"] = poppler

    if progress_callback:
        progress_callback(f"[OCR] PDF → images @ {dpi} DPI (Tesseract)...")

    images = convert_from_path(pdf_path, **kw)
    n = len(images)
    workers = max(1, _env_int("TESSERACT_PAGE_WORKERS", 2))

    def log(msg: str):
        print(msg)

    def run_one(idx_img: tuple[int, Image.Image]) -> tuple[int, str]:
        i, img = idx_img
        if progress_callback:
            tag = "full multi-pass" if _env_truthy("TESSERACT_FULL_OCR", False) else "balanced"
            progress_callback(f"[OCR] Tesseract page {i + 1}/{n} ({tag})...")
        text = ocr_pil_image_max_recall(img, pytesseract, lang, tesseract_cmd, log=log)
        return i, text or ""

    if workers > 1 and n > 1:
        from concurrent.futures import ThreadPoolExecutor

        with ThreadPoolExecutor(max_workers=min(workers, n)) as ex:
            ordered = sorted(ex.map(run_one, list(enumerate(images))), key=lambda x: x[0])
        pages = [t for _, t in ordered]
    else:
        pages = []
        for i, img in enumerate(images):
            _, t = run_one((i, img))
            pages.append(t)

    if progress_callback:
        progress_callback(f"[OCR] Tesseract complete: {n} page(s).")
    return pages

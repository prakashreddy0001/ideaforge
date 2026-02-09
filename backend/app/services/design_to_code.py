"""Design-to-code service.

Accepts an image (as bytes) and an output format, sends the image to
OpenAI's vision-capable model with a format-specific system prompt,
and returns production-ready code.
"""

import base64
import logging
import re
from typing import Optional

from app.providers.openai_provider import get_provider

logger = logging.getLogger(__name__)

# ── Supported output formats ────────────────────────────────────────

SUPPORTED_FORMATS = {"mui", "tailwind", "html"}

OUTPUT_FORMATS = {
    "mui": {
        "label": "MUI (Material UI) + React",
        "language": "jsx",
    },
    "tailwind": {
        "label": "Tailwind CSS + React",
        "language": "jsx",
    },
    "html": {
        "label": "HTML / CSS / JavaScript",
        "language": "html",
    },
}

# ── System prompts ──────────────────────────────────────────────────

_BASE_SYSTEM = """\
You are an expert frontend developer who converts UI design screenshots \
into clean, production-ready code.

Analyse the design carefully and identify:
- Layout grid and structure (rows, columns, sections)
- Spacing system (padding, margins, gaps)
- Colour palette (extract exact hex values where possible)
- Typography hierarchy (headings, body, captions, font weights)
- Interactive elements (buttons, inputs, dropdowns, toggles)
- Images and icons (use placeholder <img> or SVG icon comments)
- Responsive behaviour (infer sensible breakpoints)

Rules:
- Match the design as closely as possible.
- Use semantic HTML elements.
- Add concise inline comments explaining non-obvious layout or styling decisions.
- Return ONLY the code. No markdown fences, no explanations before or after.
- Do NOT wrap the output in ```jsx or ```html or any other markdown code block.\
"""

_MUI_ADDENDUM = """
Technology: React with MUI (Material UI) v5+.

Requirements:
- Use React functional component with hooks.
- Import each MUI component explicitly (e.g. import Button from '@mui/material/Button').
- Use the sx prop for one-off styles; extract repeated colours into a createTheme() call.
- Wrap the root in <ThemeProvider> with a theme whose palette matches the design's colours.
- Use MUI layout primitives: Box, Stack, Grid, Container, Paper, Card.
- Use MUI typography variants (h1-h6, body1, body2, caption, overline).
- For forms use TextField, Select, Checkbox, Switch, Radio.
- Export a single default component named DesignComponent.
- Include all necessary imports at the top of the file.\
"""

_TAILWIND_ADDENDUM = """
Technology: React with Tailwind CSS.

Requirements:
- Use a React functional component with hooks.
- Use Tailwind CSS utility classes for all styling (no inline styles, no CSS modules).
- Place a configuration comment at the very top showing which tailwind.config.js \
colours, fonts, and spacing tokens would be needed.
- Use responsive prefixes (sm:, md:, lg:, xl:) for layout changes across breakpoints.
- Prefer semantic elements (<nav>, <main>, <section>, <article>, <aside>, <footer>).
- For dark backgrounds use dark: prefix utilities where appropriate.
- Group related utilities logically (layout → spacing → typography → colour → effects).
- Export a single default component named DesignComponent.
- Include all necessary imports at the top of the file.\
"""

_HTML_ADDENDUM = """
Technology: Plain HTML, CSS, and JavaScript (no frameworks, no build tools).

Requirements:
- Output a single self-contained HTML file with <!DOCTYPE html>.
- Put CSS in a <style> block in <head> using CSS custom properties (--color-primary, etc.) \
for the design's colour palette.
- Put JavaScript in a <script> block before </body>.
- Use modern CSS: CSS Grid, Flexbox, clamp(), custom properties, gap.
- No external CDN links or dependencies whatsoever.
- Use semantic HTML5 elements.
- Add :hover and :focus states for interactive elements.
- Include a simple CSS reset at the top of the <style> block.\
"""


def _get_system_prompt(output_format: str) -> str:
    addendum = {
        "mui": _MUI_ADDENDUM,
        "tailwind": _TAILWIND_ADDENDUM,
        "html": _HTML_ADDENDUM,
    }[output_format]
    return _BASE_SYSTEM + "\n" + addendum


# ── Helpers ─────────────────────────────────────────────────────────

_FENCE_RE = re.compile(
    r"^```[\w]*\n?(.*?)```$",
    re.DOTALL,
)


def _strip_markdown_fences(text: str) -> str:
    """Remove wrapping ```lang ... ``` fences if the model added them."""
    text = text.strip()
    m = _FENCE_RE.match(text)
    if m:
        return m.group(1).strip()
    # Also handle case where fence doesn't close at the very end
    if text.startswith("```"):
        first_newline = text.index("\n") if "\n" in text else 3
        text = text[first_newline + 1 :]
        if text.endswith("```"):
            text = text[:-3]
        return text.strip()
    return text


# ── Public API ──────────────────────────────────────────────────────


def generate_code_from_design(
    image_bytes: bytes,
    mime_type: str,
    output_format: str,
    additional_instructions: str = "",
) -> dict:
    """Generate code from a UI design image.

    Returns {"code": str, "language": str, "format_label": str}.
    Raises ValueError on validation or AI failures.
    """
    if output_format not in SUPPORTED_FORMATS:
        raise ValueError(
            f"Invalid output format '{output_format}'. Choose: {', '.join(sorted(SUPPORTED_FORMATS))}"
        )

    fmt = OUTPUT_FORMATS[output_format]
    system_prompt = _get_system_prompt(output_format)

    # Build vision user message
    image_b64 = base64.b64encode(image_bytes).decode("ascii")

    user_text = "Convert this UI design into code following the system instructions."
    if additional_instructions:
        user_text += f"\n\nAdditional instructions from the user:\n{additional_instructions}"

    user_content = [
        {"type": "text", "text": user_text},
        {
            "type": "image_url",
            "image_url": {
                "url": f"data:{mime_type};base64,{image_b64}",
                "detail": "high",
            },
        },
    ]

    provider = get_provider()

    try:
        raw = provider.generate_with_vision(
            system_prompt=system_prompt,
            user_content=user_content,
            max_tokens=8192,
            temperature=0.3,
        )
    except Exception:
        logger.exception("OpenAI vision call failed")
        raise ValueError(
            "AI service temporarily unavailable. Please try again in a moment."
        )

    if not raw or not raw.strip():
        raise ValueError(
            "Failed to generate code from the design. Please try a clearer image."
        )

    code = _strip_markdown_fences(raw)

    return {
        "code": code,
        "language": fmt["language"],
        "format_label": fmt["label"],
    }

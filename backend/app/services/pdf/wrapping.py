"""Line wrapping shared by the clinical and educational PDF renderers."""
from collections.abc import Callable


def wrap_text(text: str, width: float, measure: Callable[[str], float]) -> list[str]:
    """Fit every line, including URLs/identifiers without spaces, without hyphens."""
    if width <= 0:
        raise ValueError("Text width must be positive")
    lines: list[str] = []
    for paragraph in text.split("\n"):
        current = ""
        for word in paragraph.split():
            candidate = f"{current} {word}" if current else word
            if measure(candidate) <= width:
                current = candidate
                continue
            if current:
                lines.append(current)
                current = ""
            for character in word:
                if current and measure(current + character) > width:
                    lines.append(current)
                    current = ""
                current += character
        lines.append(current)
    return lines

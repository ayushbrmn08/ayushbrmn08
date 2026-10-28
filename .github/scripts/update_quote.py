"""Pick a random dev quote, render it as a green terminal-style SVG card, and point README.md at it."""
import hashlib
import html
import random
import re
import textwrap
from pathlib import Path

QUOTES = [
    ("Talk is cheap. Show me the code.", "Linus Torvalds"),
    ("Programs must be written for people to read, and only incidentally for machines to execute.", "Harold Abelson"),
    ("Premature optimization is the root of all evil.", "Donald Knuth"),
    ("Simplicity is prerequisite for reliability.", "Edsger W. Dijkstra"),
    ("Any fool can write code that a computer can understand. Good programmers write code that humans can understand.", "Martin Fowler"),
    ("First, solve the problem. Then, write the code.", "John Johnson"),
    ("Make it work, make it right, make it fast.", "Kent Beck"),
    ("Everyone knows that debugging is twice as hard as writing a program in the first place.", "Brian Kernighan"),
    ("The best way to predict the future is to invent it.", "Alan Kay"),
    ("Code is like humor. When you have to explain it, it's bad.", "Cory House"),
    ("Controlling complexity is the essence of computer programming.", "Brian Kernighan"),
    ("The only way to learn a new programming language is by writing programs in it.", "Dennis Ritchie"),
    ("Before software can be reusable it first has to be usable.", "Ralph Johnson"),
    ("Good code is its own best documentation.", "Steve McConnell"),
    ("Deleted code is debugged code.", "Jeff Sickel"),
    ("Don't comment bad code, rewrite it.", "Brian Kernighan and P.J. Plauger"),
    ("Optimism is an occupational hazard of programming; feedback is the treatment.", "Kent Beck"),
    ("Perfection is achieved, not when there is nothing more to add, but when there is nothing left to take away.", "Antoine de Saint-Exupery"),
]

START = "<!-- QUOTE:START -->"
END = "<!-- QUOTE:END -->"
SVG_PATH = Path("assets/quote.svg")

# Terminal green palette
BG = "#0d1117"
BAR = "#161b22"
BORDER = "#0f5132"
TEXT = "#c9d1d9"
GREEN = "#00ff9c"
GREEN_DIM = "#39d353"
MUTED = "#8b949e"
WIDTH = 760
FONT = "'JetBrains Mono', 'Fira Code', 'SFMono-Regular', Consolas, 'Courier New', monospace"


def render_svg(quote: str, author: str) -> str:
    lines = textwrap.wrap(quote, width=60)
    bar_h = 40
    line_h = 28
    prompt_y = bar_h + 34
    first_y = prompt_y + 38
    last_y = first_y + (len(lines) - 1) * line_h
    author_y = last_y + 40
    height = author_y + 30

    text_rows = "\n".join(
        f'    <text x="40" y="{first_y + i * line_h}" font-size="18" fill="{TEXT}">{html.escape(line)}</text>'
        for i, line in enumerate(lines)
    )

    return f"""<svg xmlns="http://www.w3.org/2000/svg" width="{WIDTH}" height="{height}" viewBox="0 0 {WIDTH} {height}" role="img" aria-label="{html.escape(quote)} - {html.escape(author)}">
  <defs>
    <clipPath id="card"><rect x="1" y="1" width="{WIDTH - 2}" height="{height - 2}" rx="12"/></clipPath>
  </defs>
  <rect x="1" y="1" width="{WIDTH - 2}" height="{height - 2}" rx="12" fill="{BG}" stroke="{BORDER}" stroke-width="2"/>
  <g clip-path="url(#card)">
    <rect x="1" y="1" width="{WIDTH - 2}" height="{bar_h}" fill="{BAR}"/>
    <rect x="1" y="{bar_h}" width="{WIDTH - 2}" height="1" fill="{BORDER}"/>
  </g>
  <circle cx="28" cy="21" r="6" fill="{BORDER}"/>
  <circle cx="50" cy="21" r="6" fill="{GREEN_DIM}" opacity="0.7"/>
  <circle cx="72" cy="21" r="6" fill="{GREEN}"/>
  <g font-family="{FONT}">
    <text x="{WIDTH // 2}" y="26" font-size="13" text-anchor="middle" fill="{MUTED}">fortune.sh</text>
    <text x="40" y="{prompt_y}" font-size="16" fill="{GREEN}">$ <tspan fill="{MUTED}">fortune --dev</tspan></text>
{text_rows}
    <text x="40" y="{author_y}" font-size="16" font-weight="700" fill="{GREEN}">// <tspan fill="{GREEN_DIM}">{html.escape(author)}</tspan></text>
    <rect x="{40 + (len(author) + 4) * 9.6:.0f}" y="{author_y - 14}" width="9" height="17" fill="{GREEN}" opacity="0.85"/>
  </g>
</svg>
"""


def main() -> None:
    readme = Path("README.md")
    text = readme.read_text(encoding="utf-8")

    current = re.search(re.escape(START) + r"(.*?)" + re.escape(END), text, re.S)
    if not current:
        raise SystemExit("Quote markers not found in README.md")

    # Avoid repeating the quote that is already showing.
    choices = [q for q in QUOTES if html.escape(q[0], quote=True) not in html.escape(current.group(1), quote=True)] or QUOTES
    quote, author = random.choice(choices)

    SVG_PATH.parent.mkdir(parents=True, exist_ok=True)
    SVG_PATH.write_text(render_svg(quote, author), encoding="utf-8")

    # Query string busts GitHub's image cache whenever the quote changes.
    version = hashlib.md5(quote.encode("utf-8")).hexdigest()[:8]
    alt = html.escape(f"{quote} - {author}", quote=True)
    block = (
        f"{START}\n"
        f'<p align="center"><img src="assets/quote.svg?v={version}" alt="{alt}"/></p>\n'
        f"{END}"
    )
    readme.write_text(text[: current.start()] + block + text[current.end():], encoding="utf-8")


if __name__ == "__main__":
    main()

Short answer: it’s “okay but leaky.” It double-counts work, it only looks for **ASCII** control characters in the first check, and it leans on `str.isprintable()` in the second pass (which already flags *all* control/format chars, not just ASCII) — so the first pass is both incomplete and largely redundant.

Here’s a quick audit:

* **Two O(n) passes:** Not a correctness bug, just unnecessary. You can do it in one pass and early-exit when a threshold is exceeded.
* **ASCII-only control check:** `ord(c) < 32` misses `DEL` (0x7F), C1 controls (0x80–0x9F), and all the non-ASCII Unicode control/format characters (e.g., U+200B ZERO WIDTH SPACE, U+2066 LRI, U+202E RLO, U+FEFF BOM). If you care about terminal/printer safety, these matter.
* **`str.isprintable()` behavior:**

  * Returns `False` for ASCII control chars **including** `'\n'`, `'\r'`, `'\t'`.
  * Returns `False` for most Unicode **control/format** characters (general categories `Cc` and `Cf`), so it already catches far more than the ASCII pass.
  * Returns `True` for regular letters, punctuation, symbols, emoji, spaces, etc.
    Your code re-allows `\t\n\r` by hand — which is fine if that’s your policy — but the separate ASCII control count becomes even more redundant because those same characters would otherwise fail `isprintable()` and reduce the printable ratio.
* **What really matters for terminals/printers:** The **ESC** character (`\x1b`) and friends. If the goal is “never spew escape sequences,” treat ESC (and optionally the entire C1 range) as a **hard fail** or strip them before counting. Unicode **bidi controls** (e.g., U+202A..U+202E, U+2066..U+2069) can also be security-relevant and are `Cf`, so you likely want to disallow them by default.

### A tighter, single-pass version (configurable, terminal-safe by default)

```python
import unicodedata

# Characters we explicitly allow even though isprintable()==False
_DEFAULT_ALLOWED_WS = {'\n', '\r', '\t'}

# Characters that should never appear in terminal-safe text
# (You can widen this if desired to include C1 controls 0x80–0x9F.)
_HARD_BAN = {'\x1b'}  # ESC

def is_probably_terminal_text(
    s: str,
    *,
    min_printable_ratio: float = 0.95,   # require >=95% printable
    max_control_ratio: float = 0.0,      # allow 0% disallowed controls by default
    allowed_ws = _DEFAULT_ALLOWED_WS,
    hard_ban = _HARD_BAN,
    ban_bidi_controls: bool = True       # disallow Cf by default (safer for terminals)
) -> bool:
    """
    Heuristically decide if `s` is safe/meaningful to print to a terminal.

    - Treat ESC (and any `hard_ban`) as immediate reject.
    - Count printable vs nonprintable using Unicode categories.
    - Allow common whitespace (\\n, \\r, \\t) even though isprintable()==False.
    - Optionally ban all Unicode format chars (Cf), which include bidi controls.
    """
    if not s:
        return False

    n = len(s)
    printable = 0
    disallowed_controls = 0

    # local lookups (a small but real micro-optimization in Python)
    category = unicodedata.category
    allowed_ws = set(allowed_ws)
    hard_ban = set(hard_ban)

    # Early thresholds as integers to avoid repeated multiplication
    max_controls_allowed = int(max_control_ratio * n)
    min_printables_needed = int(min_printable_ratio * n)

    for i, ch in enumerate(s):
        # Hard ban: immediate failure (prevents ANSI/OSC sequences)
        if ch in hard_ban:
            return False

        if ch in allowed_ws:
            printable += 1
        else:
            cat = category(ch)  # e.g., 'Ll', 'Zs', 'Cc', 'Cf', etc.

            # All 'C*' categories (Cc, Cf, Cs, Co, Cn) are nonprintable for terminals.
            if cat[0] == 'C':
                # explicitly treat Cf as disallowed unless configured otherwise
                if (cat == 'Cf' and not ban_bidi_controls) and ch.isprintable():
                    printable += 1
                else:
                    disallowed_controls += 1
                    if disallowed_controls > max_controls_allowed:
                        return False
            else:
                # Everything else (letters, marks, numbers, punctuation, symbols, separators)
                # counts as printable.
                printable += 1

        # Optional early-exit: if even making all remaining chars printable
        # can't reach the min_printable threshold, fail early.
        remaining = n - (i + 1)
        if printable + remaining < min_printables_needed:
            return False

    return printable >= min_printables_needed
```

**Why this is better**

* **Single pass** with **early exits** (same big-O, less work).
* Uses **Unicode categories** so you catch *all* controls and format characters, not just ASCII `< 32`.
* **Configurable thresholds** and **policy knobs** (allowed whitespace, hard bans, bidi control policy).
* Treats **ESC** as hard fail by default, which is the main terminal-safety concern.

### Optional: sanitizer for display

If you’d rather *show* questionable content safely than reject it, sanitize instead:

```python
import re

# Strip ANSI CSI/OSC sequences (common patterns).
_ANSI_RE = re.compile(r'(?:\x1b\[[0-?]*[ -/]*[@-~])|(?:\x1b\][^\x07]*\x07)')

def sanitize_for_terminal(s: str) -> str:
    s = _ANSI_RE.sub('', s)
    # Replace remaining nonprintables with escaped hex
    return ''.join(ch if ch.isprintable() or ch in _DEFAULT_ALLOWED_WS
                   else f'\\x{ord(ch):02x}' for ch in s)
```

### Notes on `str.isprintable()` vs categories

* `isprintable()` already rejects ASCII controls **and** most Unicode controls/format chars (categories `Cc` and `Cf`). That’s why your second pass does most of the heavy lifting while the first pass misses many non-ASCII cases.
* You *re-allow* `\t`, `\n`, `\r` manually — which is reasonable — but then an explicit ASCII control ratio isn’t doing much for you anymore. If you want a control ratio check, base it on **all** of Unicode (`category(ch).startswith('C')`), minus your explicit allow-list.

### About thresholds

Make them knobs; good defaults depend on your risk tolerance:

* **Terminal-safe default** (recommendation): `min_printable_ratio=0.95`, `max_control_ratio=0.0`, `allowed_ws={'\n','\r','\t'}`, `ban_bidi_controls=True`, `hard_ban={'\x1b'}`.
  This keeps anything that could produce escape sequences or bidi spoofing out of your output.
* **Lenient** (for OCR dumps, etc.): lower printable ratio to 0.8 and allow a small control ratio (e.g., 0.02).

### TL;DR

* Your current function “mostly works,” but the **ASCII-only** control pass is incomplete and redundant, and it still lets some risky Unicode controls slip by.
* Prefer a **single-pass** Unicode-aware approach with a **hard ban on ESC**, and make thresholds & allowances **configurable**. That gives you both better coverage and better performance with early exits.

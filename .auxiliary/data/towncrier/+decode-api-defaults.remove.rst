API: Remove ``charset_default``, ``mimetype_default``, and
``mimetype_supplement`` parameters from ``decode`` so decoding follows
decode-or-error semantics instead of fallback-return inference semantics.

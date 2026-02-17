API: Report UTF charset results from BOM provenance rather than decode codec
choice so ``utf-8-sig`` is returned only when a UTF-8 BOM is present, and
apply the same provenance normalization to UTF-16/UTF-32 reporting across
decode, detection, and inference surfaces.

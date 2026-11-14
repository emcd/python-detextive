API: Honor ``Behaviors.charset_detect`` in the decode path so disabled
detection is not silently bypassed, restoring strict-mode rejection of
BOM-less generic UTF-16 and UTF-32 content from HTTP charset hints.

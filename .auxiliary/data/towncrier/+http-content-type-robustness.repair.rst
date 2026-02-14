Fix malformed ``http_content_type`` parameter parsing so inference no longer
raises raw ``ValueError`` for invalid header parameter syntax.
Also include the resolved MIME type value in ``TextualMimetypeInvalidity``
messages.

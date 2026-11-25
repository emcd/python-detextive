API: Ignore unknown and undecodable charset names during trial-codec
collection so bogus header hints and supplements (such as unknown names,
the always-failing ``undefined`` codec, or non-text codecs) fall back to
standard trials instead of leaking standard library exceptions.

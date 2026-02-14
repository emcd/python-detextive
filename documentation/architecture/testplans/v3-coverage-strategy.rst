.. vim: set fileencoding=utf-8:
.. -*- coding: utf-8 -*-
.. +--------------------------------------------------------------------------+
   |                                                                          |
   | Licensed under the Apache License, Version 2.0 (the "License");          |
   | you may not use this file except in compliance with the License.         |
   | You may obtain a copy of the License at                                  |
   |                                                                          |
   |     http://www.apache.org/licenses/LICENSE-2.0                           |
   |                                                                          |
   | Unless required by applicable law or agreed to in writing, software      |
   | distributed under the License is distributed on an "AS IS" BASIS,        |
   | WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. |
   | See the License for the specific language governing permissions and      |
   | limitations under the License.                                           |
   |                                                                          |
   +--------------------------------------------------------------------------+


*******************************************************************************
V3 Coverage Strategy
*******************************************************************************

Goal
===============================================================================

Maintain full line/branch coverage for v3 behavior while keeping
tests readable and representative of user workflows.

Testing split
===============================================================================

Common usage paths (user-facing)
-------------------------------------------------------------------------------

- Prefer doctests in ``documentation/examples``.
- Cover stable API entry points and common data flows.
- Keep examples readable and copy/paste friendly.

Edge and failure paths (engineering-facing)
-------------------------------------------------------------------------------

- Prefer pytest in ``tests/test_000_detextive``.
- Cover boundary and error behaviors.
- Use dependency injection surfaces (detector registries, behavior arguments)
  instead of monkey-patching internals.

Component focus areas
===============================================================================

Detection and Inference
-------------------------------------------------------------------------------

- Detector ordering and fallback behavior.
- Header/location context handling.
- Default-vs-error policy behavior with confidence expectations.

Decoding
-------------------------------------------------------------------------------

- Trial decode sequencing and validator interactions.
- HTTP Content-Type charset behavior, including non-textual rejection.
- ``decode_inform`` textual MIME guarantees and metadata shape.

Validation
-------------------------------------------------------------------------------

- Profile behavior for reasonable vs unreasonable text.
- Confidence-threshold behavior and validation gating.

Coverage workflow
===============================================================================

1. Run ``hatch --env develop run testers`` for the combined coverage view.
2. Use ``hatch --env develop run coverage report --show-missing`` to identify
   exact uncovered lines/branches.
3. Add/adjust doctests for common user-facing paths.
4. Add/adjust pytest cases for edge/error branches.
5. Re-run ``testers`` and verify coverage remains at target.

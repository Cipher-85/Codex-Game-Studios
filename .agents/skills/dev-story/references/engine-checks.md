# Engine review and execution evidence

After the programmer returns, verify each claimed artifact exists, inspect the
actual diff against approved paths, and identify missing or unrelated outputs.
For code stories, spawn the configured engine specialist as a read-only reviewer
using the exact custom role and runtime identity checks from the project contract.
Give it the changed file paths, story criteria, actual engine/version and matching
`docs/engine-reference/<engine>/` sections. Ask for file, line, problem and fix;
it must edit nothing. This is an implementation review, not a director gate:
full/lean/solo director filtering does not waive it.

Return criterion-breaking findings to the programmer within already approved
paths, then re-review the corrected files. Scope expansion requires approval.
Unresolved required findings, missing artifacts or unavailable specialist evidence
prevent an implementation-complete claim. Keep advisory findings in the summary.

Run the applicable approved engine/test checks using
`.codex/docs/coding-standards.md`; report their exact commands and results.
For visible criteria follow `.codex/docs/verification-integrity.md`: launch,
reach the required state, open retained screenshots, and record criterion-linked
observations. Build/import success alone is not visual proof. Missing access or
unrun criteria are NOT ASSESSED. Preserve existing checks and user-owned feel
judgments; never infer a subjective sign-off.

Include evidence doc, capture and `stamp.json` paths in the approved capture scope.
Only after a new observed capture run `bash .codex/lib/review-receipts.sh hash`
with the covered project-relative code/scene/data/asset paths and save its
successful JSON output to `production/qa/evidence/<story-slug>/stamp.json`.
Do not stamp an old capture or claim the receipt proves a test passed.

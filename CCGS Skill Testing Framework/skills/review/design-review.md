# Skill Test Spec: $design-review

## Skill Summary

`$design-review` reads a game design document (GDD) and evaluates it against
the project's 8-section design standard (Overview, Player Fantasy, Detailed
Rules, Formulas, Edge Cases, Dependencies, Tuning Knobs, Acceptance Criteria).
It checks for internal consistency, implementability, and cross-system
conflicts. It produces a verdict of APPROVED, NEEDS REVISION, or MAJOR
REVISION NEEDED. It is read-only through Phase 4; optional Phase 5 tracking
writes to `design/gdd/systems-index.md` or
`design/gdd/reviews/[doc-name]-review-log.md` require explicit approval.

---

## Static Assertions (Structural)

Verified automatically by `$skill-test static` — no fixture needed.

- [ ] Has the Codex metadata contract: `name` and `description` in frontmatter; ported fields in `## Ported metadata`, or an explicit Codex-native support classification
- [ ] Has ≥2 phase headings or numbered steps
- [ ] Contains verdict keywords: APPROVED, NEEDS REVISION, MAJOR REVISION NEEDED
- [ ] Documents that Phase 4 is read-only and Phase 5 tracking writes require approval
- [ ] Output format is documented (review template shown in skill body)

---

## Test Cases

### Case 1: Happy Path — Complete GDD, all 8 sections present

**Fixture:**
- `design/gdd/light-manipulation.md` exists (use `_fixtures/minimal-game-concept.md`
  as a stand-in — represents a complete document with all required content)
- All 8 required sections are populated with substantive content
- Formulas section contains at least one formula with defined variables
- Acceptance Criteria section contains at least 3 testable criteria

**Input:** `$design-review design/gdd/light-manipulation.md`

**Expected behavior:**
1. Skill reads the target document in full
2. Skill reads AGENTS.md for project context and standards
3. Skill evaluates all 8 required sections (present/absent check)
4. Skill checks internal consistency (formulas match described behavior)
5. Skill checks implementability (rules are precise enough to code)
6. Skill outputs structured review with section-by-section status
7. Skill outputs APPROVED verdict

**Assertions:**
- [ ] Skill reads the target file before producing any output
- [ ] Output includes a "Completeness" section showing X/8 sections present
- [ ] Output includes an "Internal Consistency" section
- [ ] Output includes an "Implementability" section
- [ ] Output ends with a verdict line: APPROVED / NEEDS REVISION / MAJOR REVISION NEEDED
- [ ] APPROVED verdict is given when all 8 sections are present and consistent

---

### Case 2: Failure Path — Incomplete GDD (4/8 sections)

**Fixture:**
- `design/gdd/light-manipulation.md` exists using content from
  `tests/skills/_fixtures/incomplete-gdd.md` (4 of 8 sections populated;
  Formulas, Edge Cases, Tuning Knobs, Acceptance Criteria are missing)

**Input:** `$design-review design/gdd/light-manipulation.md`

**Expected behavior:**
1. Skill reads the document
2. Skill identifies 4 missing sections
3. Skill outputs "Completeness: 4/8 sections present"
4. Skill lists specifically which 4 sections are missing
5. Skill outputs MAJOR REVISION NEEDED verdict (not APPROVED or NEEDS REVISION)

**Assertions:**
- [ ] Output shows "4/8" in the completeness section (not a higher number)
- [ ] Output explicitly names each missing section (Formulas, Edge Cases, Tuning Knobs, Acceptance Criteria)
- [ ] Verdict is MAJOR REVISION NEEDED (not APPROVED or NEEDS REVISION) when ≥3 sections are missing
- [ ] Output does not suggest the document is implementation-ready
- [ ] Skill does not write any files (read-only enforcement)

---

### Case 3: Partial Path — 7/8 sections, minor inconsistency

**Fixture:**
- GDD has all sections except Formulas
- The described behavior mentions numeric values but no formulas are defined
- Acceptance Criteria exist but are vague ("feels good" rather than measurable)

**Input:** `$design-review design/gdd/[document].md`

**Expected behavior:**
1. Skill identifies missing Formulas section
2. Skill flags vague acceptance criteria as an implementability issue
3. Skill outputs NEEDS REVISION verdict (not APPROVED, not MAJOR REVISION NEEDED)
4. Skill provides specific remediation notes for each issue

**Assertions:**
- [ ] Verdict is NEEDS REVISION (not APPROVED, not MAJOR REVISION NEEDED) for 7/8 with issues
- [ ] Output identifies the missing Formulas section specifically
- [ ] Output flags the vague acceptance criteria as an implementability gap
- [ ] Each flagged issue has a specific, actionable remediation note

---

### Case 4: Edge Case — File not found

**Fixture:**
- The path provided does not exist in the project

**Input:** `$design-review design/gdd/nonexistent.md`

**Expected behavior:**
1. Skill attempts to read the file
2. File not found
3. Skill outputs an error message naming the missing file
4. Skill suggests checking the path or listing files in `design/gdd/`
5. Skill does NOT produce a verdict

**Assertions:**
- [ ] Skill outputs a clear error when the file is not found
- [ ] Skill does NOT output APPROVED, NEEDS REVISION, or MAJOR REVISION NEEDED when file is missing
- [ ] Skill suggests a corrective action (check path, list available GDDs)

---

---

### Case 5: Specialist Depth — `--depth` controls specialist spawning, not review mode

**Fixture:**
- `design/gdd/light-manipulation.md` exists with all 8 sections
- `production/review-mode.txt` exists with `full` (most permissive global mode)

**Input:** `$design-review design/gdd/light-manipulation.md --depth lean`

**Expected behavior:**
1. Skill reads the GDD document
2. Skill parses `--depth lean`
3. Skill skips Phase 3b specialist delegation because analysis depth is lean
4. Skill produces the review output normally
5. The full-mode notice, when shown in full mode, says `--depth lean` rather than the legacy review-mode flag

**Assertions:**
- [ ] `--depth lean` skips Phase 3b specialist delegation
- [ ] The skill does NOT document or advertise the legacy review-mode flag for lean analysis depth
- [ ] Global `production/review-mode.txt` does not override the `--depth` argument
- [ ] The full-review notice points users to `--depth lean` for faster single-session analysis

---

### Case 6: Post-Revision and Tracking Writes — optional Phase 5 mutations are gated

**Fixture:**
- `design/gdd/light-manipulation.md` exists and receives NEEDS REVISION verdict
- User selects "Revise the GDD now" and approves the generated revision edits
- Revisions resolve all blockers
- `design/gdd/systems-index.md` exists
- `design/gdd/reviews/light-manipulation-review-log.md` may or may not exist

**Input:** `$design-review design/gdd/light-manipulation.md`

**Expected behavior:**
1. Skill outputs Phase 4 review findings without writing files
2. User selects "Revise the GDD now"
3. Skill applies only user-approved GDD revisions
4. Skill shows the post-revision closing widget: "Revisions complete — [N] blockers resolved. What next?"
5. If the user chooses an approved path, skill reads design path rules before Phase 5 tracking writes
6. Skill asks before updating `design/gdd/systems-index.md`
7. Skill asks before appending `design/gdd/reviews/[doc-name]-review-log.md`
8. Final next-action routing appears only after tracking prompts are resolved or declined

**Assertions:**
- [ ] Phase 4 remains read-only
- [ ] Post-revision widget remains authoritative after blocker fixes
- [ ] Before Phase 5 tracking writes, the skill reads `design-directory.md` and `design-docs.md`
- [ ] Systems-index update is optional and permission-gated
- [ ] Review-log append is optional and permission-gated
- [ ] Final next-action routing is shown only after tracking prompts finish

---

## Protocol Compliance

- [ ] Does NOT use Write or Edit tools through Phase 4
- [ ] Optional Phase 5 tracking writes require explicit approval
- [ ] Presents complete findings before any verdict
- [ ] Does not ask for approval before producing Phase 4 output (no writes to approve)
- [ ] Ends with recommended next step (e.g., fix issues and re-run, or proceed to `$map-systems`)

---

## Coverage Notes

- Cross-system consistency checking (Case 3 in the skill's own phase list) is
  not directly tested here because it requires multiple GDD files to compare;
  this is covered by the `$review-all-gdds` spec instead.
- Live Codex role-agent delegation behavior is not tested by this static spec
  at the spec level — this is a runtime behavior verified manually.
- Performance and edge cases involving very large GDD files are not in scope.

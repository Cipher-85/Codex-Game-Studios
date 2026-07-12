# Skill Test Spec: $design-system

## Skill Summary

`$design-system` guides the user through section-by-section authoring of a Game
Design Document (GDD) for a single game system. All 8 required sections must be
authored: Overview, Player Fantasy, Detailed Rules, Formulas, Edge Cases,
Dependencies, Tuning Knobs, and Acceptance Criteria. The skill uses a
skeleton-first approach — it creates the GDD file with all 8 section headers
before filling any content — and writes each section individually after approval.

The CD-GDD-ALIGN gate (creative-director) runs in `full` mode. It is skipped in
`lean` mode because it is not a PHASE-GATE, and skipped in `solo` mode because
solo skips all director gates. If an existing GDD file is
found, the skill offers a retrofit mode to update specific sections rather than
rewriting the whole document.

Post-design validation read-only phases continue automatically: self-check,
file readback, registry candidate scan, candidate discovery, and summaries are
not selectable next actions. The first Phase 5 user prompt is for an actual
mutation such as updating `design/registry/entities.yaml` or
`design/gdd/systems-index.md`.

---

## Static Assertions (Structural)

Verified automatically by `$skill-test static` — no fixture needed.

- [ ] Has the Codex metadata contract: `name` and `description` in frontmatter; ported fields in `## Ported metadata`, or an explicit Codex-native support classification
- [ ] Has ≥2 phase headings
- [ ] Contains verdict keywords: APPROVED, CONCERNS, REJECT
- [ ] Contains "May I write" collaborative protocol language (per-section approval)
- [ ] Has a next-step handoff at the end
- [ ] Documents skeleton-first approach (file created with headers before content)
- [ ] Documents CD-GDD-ALIGN gate: active in full mode; skipped in lean and solo
- [ ] Documents retrofit mode for existing GDD files
- [ ] Documents automatic read-only Phase 5 continuation before mutation prompts

---

## Director Gate Checks

In `full` mode: CD-GDD-ALIGN (creative-director) gate runs after the complete
GDD is authored, before finalizing. If REJECT is returned, the flagged section(s)
must be rewritten before proceeding.

In `lean` mode: CD-GDD-ALIGN is skipped because it is not a PHASE-GATE. Output
notes: "CD-GDD-ALIGN skipped — Lean mode".

In `solo` mode: CD-GDD-ALIGN is skipped. Output notes:
"CD-GDD-ALIGN skipped — Solo mode". Sections are written with only user approval.

---

## Test Cases

### Case 1: Happy Path — New GDD, skeleton-first, CD-GDD-ALIGN in full mode

**Fixture:**
- No existing GDD for the target system in `design/gdd/`
- `production/review-mode.txt` contains `full`

**Input:** `$design-system [system-name]`

**Expected behavior:**
1. Skill creates skeleton file `design/gdd/[system-name].md` with all 8 section headers (empty bodies)
2. For each section: discusses with user, drafts content, shows draft
3. "May I write [section]?" asked after draft approval
4. Section written to file after user approval
5. Process repeats for all 8 sections
6. CD-GDD-ALIGN gate runs once on the completed GDD before finalizing
7. Gate returns APPROVED

**Assertions:**
- [ ] Skeleton file is created with all 8 section headers before any content is written
- [ ] CD-GDD-ALIGN runs in full mode without a duplicate spawn-consent prompt
- [ ] "May I write" is asked per section (not once for all sections)
- [ ] Each section is written individually after user approval
- [ ] All 8 sections are present in the final GDD file

---

### Case 2: Retrofit Mode — Existing GDD, update specific section

**Fixture:**
- `design/gdd/[system-name].md` already exists with all 8 sections populated

**Input:** `$design-system [system-name]`

**Expected behavior:**
1. Skill detects existing GDD file and reads its current content
2. Skill offers retrofit mode: "GDD already exists. Which section would you like to update?"
3. User selects a specific section (e.g., Formulas)
4. Skill authors only that section and asks "May I write?"
5. Only the selected section is updated — other sections are not modified
6. If the completed GDD is finalized in full mode, CD-GDD-ALIGN runs once before finalizing

**Assertions:**
- [ ] Skill detects and reads existing GDD before offering retrofit mode
- [ ] User is asked which section to update — not asked to rewrite the whole document
- [ ] Only the selected section is rewritten — others remain unchanged
- [ ] CD-GDD-ALIGN is controlled by review mode and only runs in full mode
- [ ] "May I write" is asked before updating the section

---

### Case 3: Director Gate — CD-GDD-ALIGN returns REJECT

**Fixture:**
- New GDD being authored
- `production/review-mode.txt` contains `full`
- CD-GDD-ALIGN gate returns REJECT on the completed GDD, citing the
  Player Fantasy section

**Input:** `$design-system [system-name]`

**Expected behavior:**
1. All required sections are drafted and written after user approval
2. CD-GDD-ALIGN gate runs in full mode and returns REJECT with specific feedback
3. Skill surfaces the feedback to the user
4. Finalization is blocked while REJECT is unresolved
5. User rewrites the section in collaboration with the skill
6. CD-GDD-ALIGN runs again on the revised completed GDD
7. If the revised GDD passes, the review status is recorded

**Assertions:**
- [ ] GDD finalization is blocked when CD-GDD-ALIGN returns REJECT
- [ ] Gate feedback is shown to the user before requesting revision
- [ ] CD-GDD-ALIGN runs again after the GDD is revised
- [ ] Skill does NOT mark the GDD final while REJECT is unresolved

---

### Case 4: Lean and Solo Modes — CD-GDD-ALIGN skipped; sections written with user approval only

**Fixture:**
- New GDD being authored
- `production/review-mode.txt` contains `lean` or `solo`

**Input:** `$design-system [system-name]`

**Expected behavior:**
1. Skeleton file is created with 8 section headers
2. For each section: drafted, shown to user
3. CD-GDD-ALIGN is skipped in lean mode with "CD-GDD-ALIGN skipped — Lean mode"
   or in solo mode with "CD-GDD-ALIGN skipped — Solo mode"
4. "May I write [section]?" asked after user reviews draft
5. Section written after user approval
6. No CD-GDD-ALIGN gate review runs

**Assertions:**
- [ ] "CD-GDD-ALIGN skipped — Lean mode" is noted in lean mode
- [ ] "CD-GDD-ALIGN skipped — Solo mode" is noted in solo mode
- [ ] Sections are written after user approval alone (no gate required)
- [ ] Skill does NOT spawn any CD-GDD-ALIGN gate in lean or solo mode
- [ ] Full GDD is written with only user approval in lean or solo mode

---

### Case 5: Director Gate — Empty sections not written to file

**Fixture:**
- GDD authoring in progress
- User and skill discuss one section but do not produce any approved content
  (e.g., discussion ends without a decision, or user says "skip for now")

**Input:** `$design-system [system-name]`

**Expected behavior:**
1. Section discussion produces no approved content
2. Skill does NOT write an empty or placeholder body to the section
3. The section header remains in the skeleton file but the body stays empty
4. Skill moves to the next section without writing the empty one
5. At the end, incomplete sections are listed and user is reminded to return to them

**Assertions:**
- [ ] Empty or unapproved sections are NOT written to the file
- [ ] Skeleton section header remains (preserves structure)
- [ ] Skill tracks and lists incomplete sections at the end of the session
- [ ] Skill does NOT write "TBD" or placeholder content without user approval

---

### Case 6: Phase 5 Read-Only Continuation — Self-check and registry scan are automatic

**Fixture:**
- A new GDD has all 8 required sections written after user approval
- `design/registry/entities.yaml` exists with some entries
- The completed GDD contains 2 new registry candidates and 1 existing registry reference
- `production/review-mode.txt` contains `lean`

**Input:** `$design-system [system-name]`

**Expected behavior:**
1. After the final section write, skill reads back the complete GDD from disk
2. Skill performs the self-check automatically and reports any validation summary
3. Skill skips CD-GDD-ALIGN with "CD-GDD-ALIGN skipped — Lean mode"
4. Skill scans the completed GDD for registry candidates automatically
5. Skill presents the registry candidate summary
6. Skill asks "May I update `design/registry/entities.yaml`..." only after the read-only scan is complete

**Assertions:**
- [ ] Self-Check runs automatically after the last approved section write
- [ ] Complete GDD readback runs automatically from file, not conversation memory
- [ ] Registry candidate scan and candidate discovery run automatically before any registry write prompt
- [ ] The skill does NOT offer "Run Self-Check", "scan registry", "candidate discovery", readback, context gathering, or validation summary as selectable next actions
- [ ] The registry mutation remains permission-gated with "May I update `design/registry/entities.yaml`..."
- [ ] Final `Next action:` routing appears only after automatic Phase 5 reads and write prompts are resolved

---

## Protocol Compliance

- [ ] Skeleton file created with all 8 headers before any content is written
- [ ] CD-GDD-ALIGN runs in full mode
- [ ] CD-GDD-ALIGN skipped in lean and solo mode with a noted skip message
- [ ] Declared CD-GDD-ALIGN spawn in full mode does not require a duplicate spawn-consent prompt
- [ ] "May I write [section]?" asked per section (not once for the whole document)
- [ ] REJECT from CD-GDD-ALIGN blocks GDD finalization until resolved
- [ ] Only approved, non-empty sections are written to the file
- [ ] Self-check, readback, registry candidate scan, candidate discovery, context gathering, and validation summaries are automatic read-only continuation phases, not final closeout options
- [ ] Ends with next-step handoff: `$review-all-gdds` or `$map-systems next`

---

## Coverage Notes

- The 8 required sections are validated against the project's design document
  standards defined in `AGENTS.md` — not re-enumerated here.
- The skill's internal section-ordering logic (which section to author first) is
  not independently tested — the order follows the standard GDD template.
- Pillar alignment checking within CD-GDD-ALIGN is evaluated holistically by
  the gate agent — specific pillar checks are not fixture-tested here.

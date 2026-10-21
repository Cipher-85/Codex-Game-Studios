# Scene and Resource Files

Applies to `**/*.tscn`, `**/*.tres`, `**/*.uid`, `**/*.unity`,
`**/*.prefab`, `Assets/**/*.asset`, `**/*.uasset`, and `**/*.umap`.

Prefer the engine editor or its connected tooling. Preview the intended change
and follow the project's existing write approval rules.

## Godot

- Preserve scene/resource format versions and existing resource IDs.
- Never invent a `uid://` identifier. Let the project's pinned editor generate it.
- Preserve each script/shader's `.uid` when moving or renaming it.
- When duplicating a node, do not duplicate its `unique_id` where that field is
  supported by the pinned engine.
- Edit encoded TileMapLayer/GridMap cell data through the editor.
- After a text edit, import with the pinned engine and open or run the affected
  scene. An import alone does not prove the scene behaves correctly.

## Unity

- Use the editor when it is open on the project or accessible through connected
  tools. Hand editing its YAML can conflict with the editor's in-memory copy.
- Preserve `fileID`, GUID, and `.meta` relationships. Never fabricate identifiers.
- If an editor is unavailable, report that limitation, keep any approved text
  edit narrow, and leave editor load validation explicitly owed.

## Unreal

- `.uasset` and `.umap` are binary assets. Do not edit them as text.
- Use the editor or supported engine tooling; report missing tooling as a blocker
  for the asset edit.

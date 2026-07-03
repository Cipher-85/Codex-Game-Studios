# Shader Code Standards

---
paths:
  - "assets/shaders/**"
---

All shader files in `assets/shaders/` must maintain visual quality,
performance, and cross-platform compatibility.

## Naming

- File naming: `[type]_[category]_[name].[ext]`.
- Godot example: `spatial_env_water.gdshader`.
- Unity Shader Graph example: `SG_Env_Water`.
- Unreal material example: `M_Env_Water`.
- Prefix with shader type: `spatial_`, `canvas_`, `particles_`, or `post_`.

## Code Quality

- All uniforms and parameters need descriptive names and appropriate hints.
- Group related parameters.
- Comment non-obvious calculations, especially math-heavy sections.
- Avoid magic numbers; use named constants or documented uniform values.
- Include authorship and purpose comments at the top of each shader file.

## Performance

- Document target platform and complexity budget.
- Use appropriate precision on mobile where full precision is unnecessary.
- Minimize texture samples in fragment shaders.
- Avoid dynamic branching in fragment shaders; prefer `step()`, `mix()`, and
  `smoothstep()`.
- Do not read textures inside loops.
- Use two-pass blur effects.

## Cross-Platform

- Test shaders on minimum spec target hardware.
- Provide fallbacks or simplified versions for lower quality tiers.
- Document the target render pipeline.
- Do not mix shaders from different render pipelines in one directory.

# Style Guide

Python style for this project. Formatting and lint rules are enforced by [ruff.toml](ruff.toml) and not repeated here.

## Code Organization

- Declare `__all__` in modules with a public API, and keep package `__init__.py` files to re-exports.
- Separate the public interface from implementation: a clean public entry point that dispatches to private `_`-prefixed helpers.
- Credit code derived from other projects in a short header comment (source, license, copyright).

## Naming and Typing

- Standard Python naming: `snake_case` functions, `PascalCase` classes, `UPPER_CASE` constants, `_leading_underscore` for private helpers.
- Prefer descriptive domain names over abbreviations; short names are fine in tight loops.
- Annotate public function signatures using modern type syntax (`X | None`, `list[Tensor]`) rather than `typing.Optional`/`Union`/`List`.

## Function Signatures

- For functions with many parameters, keep the primary data arguments positional and make configuration keyword-only. Pass by keyword at call sites when there are more than a few arguments.
- A `None` default works well for "auto-detect" behavior, resolved internally.

## Docstrings

- Google convention: a one-line imperative summary, then args documented by name with defaults noted as `(default: X)`. Types belong in the signature, not the docstring.
- Mention requirements and incompatibilities where the relevant argument is documented.
- Private helpers need a docstring only when the name and signature don't tell the story.

## Comments

Comment only where the code isn't self-explanatory: non-obvious tricks, invariants, and workarounds (with the symptom they avoid). Don't narrate steps the code already states..

## Errors and Warnings

- Validate arguments eagerly at entry points and include the offending value in the message.
- Make messages actionable: state the fix, not just the problem.
- Use `warnings.warn` with an explicit category for deprecations and likely misconfigurations.

## Dependencies and Compatibility

- Probe optional imports once at module load (`try`/`except ImportError` into a `HAS_X` flag) and gate dependent code on it.
- Resolve version checks into module-level constants instead of inline comparisons.

## Tests

- Parametrize with pytest, giving cases readable ids and marks so subsets are selectable.
- Centralize skip logic and shared configuration rather than scattering them through test files.

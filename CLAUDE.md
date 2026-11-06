# 3d-models

See README.md for the layout, how to write a model and how to build.

## Previews

Show what a model looks like whenever you can.

- Every model calls `preview(part, __file__)` from `common/preview.py`, so
  `make` writes `models/<name>/preview.png`. Commit it, and show it at the top
  of the model's README.
- Rebuild before committing a change to a model's shape, so its preview
  matches. Look at the image yourself before relying on it.
- A pull request that adds or changes a model embeds its preview in the body.
  The repository is private, so a relative path will not resolve: link the
  image at the pushed commit,
  `https://github.com/prsimp/3d-models/blob/<sha>/models/<name>/preview.png?raw=true`.
  Use the full SHA, so the image stays put when the branch moves on.
- When one view cannot show the change, such as a variant, a test piece or a
  detail hidden in the default views, render extra views with `preview(...,
  views=...)` to a scratch file and attach those too, or say what they would
  have shown.

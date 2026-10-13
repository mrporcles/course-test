# Contributing

1. Branch from `main`; edit lesson prose in `metadata/lms/**/content.md` and metadata in the JSON files.
2. Run `make check` before opening a PR (CI runs the same check).
3. New lessons: copy a sibling directory, use an id that starts with its module's id, and keep every
   module at two or more lessons. Don't add overview/summary lessons; intro text belongs in the
   course `summary.md` and the wrap-up in `conclusion.md`.
4. Merging to `main` deploys to staging. Production is a manual `deploy-production` run against a release tag.
5. A problem that persists after a clean staging deploy (site doesn't reflect the metadata, API errors)
   is a backend issue: raise a 1.Support Wolken ticket rather than working around it here.

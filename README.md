# Spring Framework Essentials (modernized)

LMS metadata and lesson content for the *Spring Framework Essentials (modernized)* course on
[Spring Academy](https://spring.academy). It is a **metadata-only** course: every lesson is an
article, there is no lab image and no Educates workshop.

## Layout

```
metadata/lms/
  course.template.json   course metadata; ${VAR} placeholders are filled in at deploy time
  summary.md, description.md, conclusion.md
  deploy.sh              wraps `penguinctl apply course`
  NN-module/             module.json + NN-lesson/ (lesson.json, description.md, summary.md, content.md, images/)
scripts/check-metadata.py   offline validation (penguinctl only validates server-side)
Makefile                    targets below
.github/workflows/          validate, deploy-staging, deploy-production
```

## Make targets

| Target | What it does |
|---|---|
| `make check` | Validate JSON, ids/slugs, id prefixes, module sizes and image links. No credentials needed. |
| `make render` | Print the `course.json` that would be deployed. |
| `make deploy-lms-dry-run` | `penguinctl apply course --dry-run`. |
| `make deploy-lms` (alias `deploy`) | Apply the course to the LMS. |

Deploying needs `PENGUINCTL_APIURL` and `PENGUINCTL_APITOKEN` in the environment (staging and
production use different pairs). Nothing is hard-coded; never commit tokens. By default
`penguinctl` runs from the `ghcr.io/vmware-tanzu-learning/penguinctl` Docker image; set
`PENGUIN_USEDOCKER=false` to use a locally installed binary (`brew install
vmware-tanzu-learning/tap/penguinctl`).

Note: `apply course --dry-run` fails with `404 Not Found` on the first nested create if the
course does not exist yet. For a brand-new course the first real staging deploy is the test.

## Deployment flow

- **Staging:** pushes to `main` that touch `metadata/**` run `deploy-staging` (also runnable by hand).
- **Production:** always manual. Create a release (`gh release create vX.Y.Z --target main
  --latest --generate-notes`), then run `deploy-production` against that tag.
- Required secrets (org-level in `spring-academy`, otherwise set per repo):
  `PENGUINCTL_APIURL_STAGING`, `PENGUINCTL_APITOKEN_STAGING`, `PENGUINCTL_APIURL_PROD`,
  `PENGUINCTL_APITOKEN_PROD`. Production runs under the `prod` GitHub Environment.

## Images

Course diagrams live next to their lessons in `images/` and are drawn in the Spring Academy
style. Regenerate them with the `spring-academy-images` skill in `.claude/skills/`.

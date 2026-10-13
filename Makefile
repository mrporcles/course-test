#!make
# Spring Framework Essentials (modernized) - LMS metadata deploy tooling.
# Metadata-only course: no lab image, no Educates workshop. See README.md.

.DEFAULT_GOAL := help
.PHONY: help check render deploy-lms-dry-run deploy-lms deploy deploy-local clean

help: ## Show this help
	@grep -E '^[a-zA-Z_-]+:.*## ' $(MAKEFILE_LIST) | awk 'BEGIN {FS = ":.*## "}; {printf "  %-20s %s\n", $$1, $$2}'

check: ## Validate metadata (JSON, ids, slugs, image links) - no credentials needed
	python3 scripts/check-metadata.py

render: ## Print the course.json that would be deployed (placeholders filled in)
	metadata/lms/deploy.sh render

deploy-lms-dry-run: check ## penguinctl apply --dry-run (needs PENGUINCTL_APIURL/APITOKEN)
	metadata/lms/deploy.sh dry-run

deploy-lms: check ## penguinctl apply course (needs PENGUINCTL_APIURL/APITOKEN)
	metadata/lms/deploy.sh deploy-all

deploy: deploy-lms ## Alias for deploy-lms (what CI runs)

deploy-local: deploy-lms ## Alias for deploy-lms; set PENGUIN_USEDOCKER=false to use a local penguinctl

clean: ## Remove generated files
	rm -f metadata/lms/course.json

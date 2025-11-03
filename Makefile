COMPOSE_FILE ?= infra/compose/compose.staging.yaml
ROLLBACK_LOCK ?= infra/releases/staging.lock

.PHONY: rollback-staging
rollback-staging:
	@if [ ! -f "$(ROLLBACK_LOCK)" ]; then \
		echo "Rollback lock file $(ROLLBACK_LOCK) not found" >&2; \
		exit 1; \
	fi
	@TAG_LINE=$$(grep '^TAG=' "$(ROLLBACK_LOCK)" || true); \
	if [ -z "$$TAG_LINE" ]; then \
		echo "TAG entry missing in $(ROLLBACK_LOCK)" >&2; \
		exit 1; \
	fi; \
	echo "Using $$TAG_LINE for rollback"; \
	export $$TAG_LINE; \
	docker compose -f "$(COMPOSE_FILE)" down; \
	docker compose -f "$(COMPOSE_FILE)" up -d

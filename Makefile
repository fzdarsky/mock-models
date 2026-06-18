MODELS := mocklm

.PHONY: lint test build push manifest

lint test build push manifest:
	@for m in $(MODELS); do echo "==> $$m $@"; $(MAKE) -C $$m $@; done

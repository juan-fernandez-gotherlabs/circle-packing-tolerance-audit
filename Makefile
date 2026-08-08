.PHONY: verify refine search-layer1

verify:
	./verify_all.sh

refine:
	python3 scripts/refine_exact.py

search-layer1:
	python3 scripts/run_search.py --depth 1

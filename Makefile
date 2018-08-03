# Rule to create an oracle for each training example.
# Requires GNU Parallel to be installed.
oracles.json : data/geo880-train
	# HACK: delete training example 529 which our current algorithm can't
	# handle
	cat $< | sed '529d' | parallel --gnu --pipe --keep-order --max-args 1 --halt now,fail=1 --joblog oracles.log python3 -m oracles > $@

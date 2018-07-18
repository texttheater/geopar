# Rule to create an oracle for each training example.
# Requires GNU Parallel to be installed.
oracles.txt : data/geo880-train
	cat $< | parallel --gnu --pipe --keep-order --max-args 1 --halt now,fail=1 python3 -m oracles > $@

geopar
======

Stub of a simple semantic parser for the GeoQuery domain, for teaching
purposes.

Made available under the GPLv2 license.

The data included is also GPLv2 and was obtained from
http://www.cs.utexas.edu/users/ml/nldata/geoquery.html. The split into training
and testing portions is the same as in Tom Kwiatkowski’s UBL system.

Exercise
--------

The (quite challenging) exercise is to implement the missing parts of GeoPar so
that the test suite passes and you can train a simple model.

A solution for peeking is available at
https://github.com/texttheater/geopar/tree/solution.

How to Run the Test Suite
-------------------------

    python3 -m unittest

How to Train a Simple Model
---------------------------

    python3 -m train

During training, validation accuracies are displayed. Try to get these above
0.8 by implementing suitable features.

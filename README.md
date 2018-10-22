geopar
======

Stub of a simple semantic parser for the GeoQuery domain, for teaching
purposes.

Made available under the GPLv2 license.

The data included is also GPLv2 and was obtained from
http://www.cs.utexas.edu/users/ml/nldata/geoquery.html. The split into training
and testing portions is the same as in Tom Kwiatkowski’s UBL system.

Usage
-----

Run the test suite:

    python3 -m unittest

Train a semantic parsing model for GeoQuery, using the same training and
validation data as Zettlemoyer and Collins (2005):

    python train.py

The model is saved as `model.pickle`.

Evaluate on the test data:

    python3 test.py

Converting visible wavelengths to (r, g, b)
###########################################

:date: 2017-09-17
:tags: python, wavelength, RGB
:author: Roland Smith

.. Last modified: 2018-04-17T19:50:43+0200

The ``rgb`` module contains a function that converts from a wavelength in nm
to an 3-tuple of (R,G,B) values, each in the range 0--255.

.. PELICAN_END_SUMMARY

License
-------

The ``gentable.py`` script is licensed under the MIT licensce.
Its output ``rgb.py`` is automatically generated and thus not copyrightable.


Notes
-----

The algorithm is based on `Dan Bruton's work`_. The first time I came across
it was in a Pascal translation of the original Fortran code.

.. _Dan Bruton's work: http://www.physics.sfasu.edu/astro/color/spectra.html

Since the conversion uses a fixed function over a relatively small range of
values, I pre-compute the results for every integer value of the wavelength
between 380 and 780 nm and record them in a ``bytes`` object. Three bytes are
used for a single wavelength in the sequence red, green, blue.
This ``bytes`` object is compressed with zlib and then encoded in base64.

The code is generated as follows.

.. code-block:: console

    python3 gentable.py > rgb.py

The compression reduces the amount of data approximately by half. Encoding
adds to the length, but the encoded string is significantly shorter than the
compressed data in string form.

.. code-block:: python

    In [1]: from gentable import wavelen2rgb

    In [2]: clrs = []

    In [3]: for wl in range(380, 781):
        ...:     clrs += wavelen2rgb(wl)
        ...:

    In [4]: raw = bytes(clrs)

    In [5]: len(raw)
    Out[5]: 1203

    In [6]: import zlib

    In [7]: compressed = zlib.compress(raw, 9)

    In [8]: len(compressed)
    Out[8]: 653

    In [9]: import base64

    In [10]: enc = base64.b64encode(compressed)

    In [11]: len(enc)
    Out[11]: 872

    In [12]: len(str(compressed))
    Out[12]: 1811

    In [13]: len(str(enc))
    Out[13]: 875

There is a one-time cost for decoding the table. As can be seen below, this
cost is not very high.

.. code-block:: python

    In [14]: %timeit -r 1 -n 1 zlib.decompress(base64.b64decode(enc))
    1 loop, best of 1: 132 µs per loop

The table look-up is significantly faster than doing the conversion directly.

.. code-block:: python

    In [1]: from rgb import rgb

    In [2]: %timeit [rgb(n) for n in range(400, 501)]
    1000 loops, best of 3: 205 µs per loop

    In [3]: from gentable import wavelen2rgb

    In [4]: %timeit [wavelen2rgb(n) for n in range(400, 501)]
    1000 loops, best of 3: 592 µs per loop



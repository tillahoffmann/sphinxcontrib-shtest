🧪 shtest
=========

shtest tests shell commands in your Sphinx documentation. The :code:`shtest` directive supports the usual `doctest <https://www.sphinx-doc.org/en/master/usage/extensions/doctest.html>`_ syntax. It offers two options: specifying the expected return code (defaults to 0) and choosing the stream to compare with (defaults to stdout).

Examples
--------

.. shtest::

    # Obligatory hello world example.
    $ echo hello world
    hello world

.. shtest::
    :stream: stderr

    # Read from stderr instead of stdout.
    $ echo message on stderr >&2
    message on stderr

.. shtest::
    :returncode: 1

    # Use a non-zero expected return code.
    $ false

.. shtest::

    # Run multiple tests in one directive.
    $ echo hello
    hello
    $ echo world
    world

Installation
------------

Run :code:`pip install sphinxcontrib-shtest` to install the package and add :code:`"sphinxcontrib-shtest"` to your :code:`extensions` list in :code:`conf.py` (see `here <https://www.sphinx-doc.org/en/master/usage/configuration.html#confval-extensions>`__ for details). Then execute :code:`sphinx-build -b shtest /path/to/source/directory /path/to/output/directory`.

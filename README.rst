🧪 shtest
=========

.. image:: https://github.com/tillahoffmann/sphinxcontrib-shtest/actions/workflows/main.yaml/badge.svg
    :target: https://github.com/tillahoffmann/sphinxcontrib-shtest/
.. image:: https://img.shields.io/pypi/v/sphinxcontrib-shtest
    :target: https://pypi.org/project/sphinxcontrib-shtest/
.. image:: https://readthedocs.org/projects/sphinxcontrib-shtest/badge/?version=latest
    :target: https://sphinxcontrib-shtest.readthedocs.io/en/latest/?badge=latest

:code:`shtest` tests shell commands in your Sphinx documentation.

The :code:`shtest` directive supports the usual `doctest <https://www.sphinx-doc.org/en/master/usage/extensions/doctest.html>`_ syntax. The following example renders as shown below during a normal documentation build and runs the test when executed using the :code:`shtest` builder (see `Installation and Usage`_ for details).

.. code-block:: rst

    .. shtest::

        # Obligatory hello world example.
        $ echo hello world
        hello world

.. shtest::

    # Obligatory hello world example.
    $ echo hello world
    hello world

The directive offers the following options:

- :code:`:returncode: [integer]` specifies the expected return code (defaults to 0).
- adding the :code:`:stderr:` flag compares results with the :code:`stderr` rather than :code:`stdout` stream.
- :code:`:cwd: [relative path]` specifies the working directory relative to the source of the document (defaults to the directory containing the source document).
- :code:`:tempdir:` executes the test in a temporary directory.

Installation and Usage
----------------------

1. Run :code:`pip install sphinxcontrib-shtest` to install the package.
2. Add :code:`"sphinxcontrib.shtest"` to your :code:`extensions` list in :code:`conf.py` to enable the extension (see `here <https://www.sphinx-doc.org/en/master/usage/configuration.html#confval-extensions>`__ for details).
3. Execute :code:`sphinx-build -b shtest /path/to/source/directory /path/to/output/directory`. The :code:`-b shtest` flag executes the shell tests; run without the :code:`-b shtest` flag to build your documentation as usual.

Examples
--------

.. code-block:: rst

    .. shtest::
        :stderr:

        # Read from stderr instead of stdout.
        $ echo message on stderr >&2
        message on stderr

.. shtest::
    :stderr:

    # Read from stderr instead of stdout.
    $ echo message on stderr >&2
    message on stderr

.. code-block:: rst

    .. shtest::
        :returncode: 1

        # Use a non-zero expected return code.
        $ false

.. shtest::
    :returncode: 1

    # Use a non-zero expected return code.
    $ false

.. code-block:: rst

    .. shtest::

        # Run multiple tests in one directive.
        $ echo hello
        hello
        $ echo world
        world

.. shtest::

    # Run multiple tests in one directive.
    $ echo hello
    hello
    $ echo world
    world

.. code-block:: rst

    .. shtest::
        :cwd: tests

        # Run a test in a particular working directory relative to the document.
        $ cat hello.txt
        world

.. shtest::
    :cwd: tests

    # Run a test in a particular working directory relative to the document.
    $ cat hello.txt
    world

.. code-block:: rst

    .. shtest::
        :tempdir:

        # Run a test in a temporary directory.
        $ echo hello > world.txt

.. shtest::
    :tempdir:

    # Run a test in a temporary directory.
    $ echo hello > world.txt

.. code-block:: rst

    .. sh:: ls -l

.. sh:: ls -l

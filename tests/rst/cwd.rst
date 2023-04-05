.. shtest::

    $ mkdir hello
    $ echo hello world > hello/world.txt

.. shtest::
    :cwd: hello

    $ cat world.txt
    hello world

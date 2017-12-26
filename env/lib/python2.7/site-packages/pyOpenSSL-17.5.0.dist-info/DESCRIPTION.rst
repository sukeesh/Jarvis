========================================================
pyOpenSSL -- A Python wrapper around the OpenSSL library
========================================================

.. image:: https://readthedocs.org/projects/pyopenssl/badge/?version=stable
   :target: https://pyopenssl.org/en/stable/
   :alt: Stable Docs

.. image:: https://travis-ci.org/pyca/pyopenssl.svg?branch=master
   :target: https://travis-ci.org/pyca/pyopenssl
   :alt: Build status

.. image:: https://codecov.io/github/pyca/pyopenssl/branch/master/graph/badge.svg
   :target: https://codecov.io/github/pyca/pyopenssl
   :alt: Test coverage


High-level wrapper around a subset of the OpenSSL library.  Includes

* ``SSL.Connection`` objects, wrapping the methods of Python's portable sockets
* Callbacks written in Python
* Extensive error-handling mechanism, mirroring OpenSSL's error codes

... and much more.

You can find more information in the documentation_.
Development takes place on GitHub_.


Discussion
==========

If you run into bugs, you can file them in our `issue tracker`_.

We maintain a cryptography-dev_ mailing list for both user and development discussions.

You can also join ``#cryptography-dev`` on Freenode to ask questions or get involved.


.. _documentation: https://pyopenssl.org/
.. _`issue tracker`: https://github.com/pyca/pyopenssl/issues
.. _cryptography-dev: https://mail.python.org/mailman/listinfo/cryptography-dev
.. _GitHub: https://github.com/pyca/pyopenssl


Release Information
===================

17.5.0 (2017-11-30)
-------------------


Backward-incompatible changes:
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

* The minimum ``cryptography`` version is now 2.1.4.


Deprecations:
^^^^^^^^^^^^^

*none*


Changes:
^^^^^^^^

- Fixed a potential use-after-free in the verify callback and resolved a memory leak when loading PKCS12 files with ``cacerts``.
  `#723 <https://github.com/pyca/pyopenssl/pull/723>`_
- Added ``Connection.export_keying_material`` for RFC 5705 compatible export of keying material.
  `#725 <https://github.com/pyca/pyopenssl/pull/725>`_

----



17.4.0 (2017-11-21)
-------------------


Backward-incompatible changes:
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

*none*


Deprecations:
^^^^^^^^^^^^^

*none*


Changes:
^^^^^^^^


- Re-added a subset of the ``OpenSSL.rand`` module.
  This subset allows conscientious users to reseed the OpenSSL CSPRNG after fork.
  `#708 <https://github.com/pyca/pyopenssl/pull/708>`_
- Corrected a use-after-free when reusing an issuer or subject from an ``X509`` object after the underlying object has been mutated.
  `#709 <https://github.com/pyca/pyopenssl/pull/709>`_

----


17.3.0 (2017-09-14)
-------------------


Backward-incompatible changes:
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

- Dropped support for Python 3.3.
  `#677 <https://github.com/pyca/pyopenssl/pull/677>`_
- Removed the deprecated ``OpenSSL.rand`` module.
  This is being done ahead of our normal deprecation schedule due to its lack of use and the fact that it was becoming a maintenance burden.
  ``os.urandom()`` should be used instead.
  `#675 <https://github.com/pyca/pyopenssl/pull/675>`_


Deprecations:
^^^^^^^^^^^^^

- Deprecated ``OpenSSL.tsafe``.
  `#673 <https://github.com/pyca/pyopenssl/pull/673>`_

Changes:
^^^^^^^^

- Fixed a memory leak in ``OpenSSL.crypto.CRL``.
  `#690 <https://github.com/pyca/pyopenssl/pull/690>`_
- Fixed a memory leak when verifying certificates with ``OpenSSL.crypto.X509StoreContext``.
  `#691 <https://github.com/pyca/pyopenssl/pull/691>`_

`Full changelog <https://pyopenssl.org/en/stable/changelog.html>`_.




certbot-dns-arsys
=================

.. image:: https://img.shields.io/pypi/v/certbot-dns-arsys
   :target: https://pypi.org/project/certbot-dns-arsys/
   :alt: PyPI version

.. image:: https://img.shields.io/pypi/l/certbot-dns-arsys
   :target: https://github.com/spanishkangaroo/certbot-dns-arsys/blob/main/LICENSE
   :alt: License: Apache 2.0

.. image:: https://img.shields.io/pypi/pyversions/certbot-dns-arsys
   :target: https://pypi.org/project/certbot-dns-arsys/
   :alt: Supported Python versions

.. image:: https://github.com/spanishkangaroo/certbot-dns-arsys/actions/workflows/test.yml/badge.svg
   :target: https://github.com/spanishkangaroo/certbot-dns-arsys/actions/workflows/test.yml
   :alt: CI test status

`Certbot <https://certbot.eff.org/>`_ DNS authenticator plugin for `Arsys <https://www.arsys.es/>`_ domains.

Automates DNS-01 challenge validation by creating and removing ``_acme-challenge`` TXT records via
the Arsys Hosting SOAP API, enabling wildcard certificate issuance and fully automated renewal.

.. contents:: Table of Contents
   :local:
   :depth: 1


Prerequisites
-------------

- Python 3.10+
- Certbot 2.0+
- An Arsys account with API access enabled (obtain your API key from the Arsys control panel)
- Network access to ``api.servidoresdns.net`` on port **54321**


Installation
------------

.. code-block:: bash

   pip install certbot-dns-arsys

Verify the plugin is available::

   certbot plugins

You should see ``dns-arsys`` in the list.


Snap
----

If you installed Certbot as a snap, a pip-installed plugin is **not** visible to it.
Install this plugin from the Snap Store instead:

.. code-block:: bash

   snap install certbot-dns-arsys
   snap connect certbot:plugin certbot-dns-arsys
   snap connect certbot-dns-arsys:certbot-metadata certbot:certbot-metadata

Then confirm the plugin is registered::

   certbot plugins

You should see ``dns-arsys`` in the list. The ``certbot-dns-arsys:certbot-metadata``
interface auto-connects; the ``certbot:plugin`` connection requires the explicit
``snap connect`` above.


Credentials File
----------------

Create a credentials file (e.g. ``~/.secrets/certbot/arsys.ini``) with the following content:

.. code-block:: ini

   # Arsys API endpoint (optional — this is the default)
   dns_arsys_api_url = https://api.servidoresdns.net:54321/hosting/api/soap/index.php

   # Your domain (as registered in your Arsys account)
   dns_arsys_api_login = example.com

   # API key from the Arsys control panel
   dns_arsys_api_key = YOUR_API_KEY_HERE

   # The base domain managed in this Arsys account
   dns_arsys_domain = example.com

Secure the file so only root can read it::

   chmod 600 ~/.secrets/certbot/arsys.ini


Usage
-----

**Wildcard certificate:**

.. code-block:: bash

   certbot certonly \
     --authenticator dns-arsys \
     --dns-arsys-credentials ~/.secrets/certbot/arsys.ini \
     -d "*.example.com" \
     -d "example.com"

**Standard certificate:**

.. code-block:: bash

   certbot certonly \
     --authenticator dns-arsys \
     --dns-arsys-credentials ~/.secrets/certbot/arsys.ini \
     -d "example.com" \
     -d "www.example.com"

**Renewal** (automatic, no extra flags needed after initial issuance)::

   certbot renew

**Non-root usage:**

Certbot requires write access to ``/var/log/letsencrypt``, ``/etc/letsencrypt``, and
``/var/lib/letsencrypt`` by default, which are root-owned. If you run certbot as a
regular user (e.g. for testing), redirect those paths with three extra flags:

.. code-block:: bash

   certbot certonly \
     --authenticator dns-arsys \
     --dns-arsys-credentials ~/.secrets/certbot/arsys.ini \
     -d "*.example.com" \
     -d "example.com" \
     --config-dir ~/.letsencrypt \
     --work-dir ~/.letsencrypt/work \
     --logs-dir ~/.letsencrypt/logs

Certificates will be written to ``~/.letsencrypt/live/example.com/``.


Options
-------

``--dns-arsys-credentials``
   Path to the INI credentials file. **Required.**

``--dns-arsys-propagation-seconds``
   Maximum seconds to wait for DNS propagation before proceeding. Default: ``30``.
   The plugin polls authoritative nameservers every 15 seconds and proceeds as soon as
   the record is confirmed. Increase this value if you see validation failures.


Docker
------

A Docker image based on ``certbot/certbot`` with the plugin pre-installed is available:

.. code-block:: bash

   docker run --rm \
     -v ~/.secrets/certbot:/secrets:ro \
     -v /etc/letsencrypt:/etc/letsencrypt \
     ghcr.io/javiervazquez/certbot-dns-arsys:latest \
     certonly \
       --authenticator dns-arsys \
       --dns-arsys-credentials /secrets/arsys.ini \
       -d "*.example.com"

Or build locally::

   docker build -t certbot-dns-arsys .
   docker run --rm certbot-dns-arsys plugins


Troubleshooting
---------------

**``dns-arsys`` is not listed by ``certbot plugins``**
   The plugin is not installed in the same environment as certbot. Confirm both are
   in the same interpreter::

      pip show certbot-dns-arsys
      certbot plugins

   If you installed certbot via snap, install the plugin into the snap instead of pip;
   a pip-installed plugin is not visible to a snap-installed certbot.

**Authentication errors (HTTP 401/403 or "invalid credentials")**
   Re-check the credentials file. ``dns_arsys_api_login`` must be your Arsys account
   domain and ``dns_arsys_api_key`` the key from the Arsys control panel. Make sure the
   API key has not been revoked and that ``dns_arsys_domain`` matches the zone you are
   issuing for.

**Connection timeouts / "connection refused" to the API**
   The Arsys Hosting API runs on the **non-standard port 54321**. Verify outbound
   connectivity from the host running certbot::

      nc -vz api.servidoresdns.net 54321

   If this fails, open outbound TCP to ``api.servidoresdns.net:54321`` in your firewall.

**Validation fails with "incorrect TXT record" or a propagation timeout**
   The challenge record had not propagated before certbot asked Let's Encrypt to validate.
   Increase the wait with ``--dns-arsys-propagation-seconds`` (default ``30``)::

      certbot certonly --authenticator dns-arsys \
        --dns-arsys-credentials ~/.secrets/certbot/arsys.ini \
        --dns-arsys-propagation-seconds 120 \
        -d "*.example.com"

   You can confirm propagation manually with::

      dig +short TXT _acme-challenge.example.com

**Permission errors reading the credentials file**
   Certbot warns if the credentials file is group/world-readable, and refuses to run if it
   cannot read it. Ensure the file is owned by the user running certbot and is mode ``600``::

      chmod 600 ~/.secrets/certbot/arsys.ini


Notes
-----

- The Arsys Hosting API endpoint runs on a non-standard port (54321). Ensure your firewall
  allows outbound TCP connections to ``api.servidoresdns.net:54321``.
- DNS propagation timing depends on Arsys infrastructure. The Arsys SOAP API applies
  changes almost immediately, so the default 30-second timeout is generally sufficient.
  Increase with ``--dns-arsys-propagation-seconds`` if you see validation failures.
- The plugin is a **third-party plugin** not affiliated with Certbot or the EFF.


License
-------

Licensed under the `Apache License 2.0 <https://www.apache.org/licenses/LICENSE-2.0>`_.

Copyright 2026 Javier Vázquez.

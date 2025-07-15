Welcome to {{cookiecutter.project_name}}'s documentation!
{{ '=' * ('Welcome to ' ~ cookiecutter.project_name ~ "'s documentation!" | length) }}

.. toctree::
   :maxdepth: 2
   :caption: Contents:

Configuration
-------------

The service reads settings from environment variables via ``pydantic``.
The most important variables are ``APP_HOST``, ``APP_PORT``, ``APP_ENV`` and
``REDIS_URL``. Metrics and tracing can be configured using ``STATSD_HOST``,
``STATSD_PORT``, ``JAEGER_HOST``, ``JAEGER_PORT`` and ``LOKI_ENDPOINT``. See
``.env.example`` for defaults.

Running with Docker Compose
---------------------------

Start all dependencies together with the application:

.. code-block:: bash

   docker-compose up -d

Metrics and tracing
-------------------

Metrics are sent via ``utils.metrics`` to a StatsD exporter. Traces are exported
to Jaeger when OpenTelemetry is available using ``utils.tracing``. Logs can be
forwarded to Loki if ``LOKI_ENDPOINT`` is set.

Graceful shutdown
-----------------

``api.main`` registers a shutdown handler that closes Redis connections, resets
the metrics client and clears stored spans to ensure clean exit.

Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`

API Documentation
=================

.. automodule:: {{cookiecutter.python_package_name}}.api.main
   :members:
   :undoc-members:
   :show-inheritance:

.. automodule:: {{cookiecutter.python_package_name}}.api.health
   :members:
   :undoc-members:
   :show-inheritance:

.. automodule:: {{cookiecutter.python_package_name}}.core.config
   :members:
   :undoc-members:
   :show-inheritance:

.. automodule:: {{cookiecutter.python_package_name}}.api.tasks
   :members:
   :undoc-members:
   :show-inheritance:

.. automodule:: {{cookiecutter.python_package_name}}.core.logging_config
   :members:
   :undoc-members:
   :show-inheritance:

.. automodule:: {{cookiecutter.python_package_name}}.utils.metrics
   :members:
   :undoc-members:
   :show-inheritance:

.. automodule:: {{cookiecutter.python_package_name}}.utils.redis_stream
   :members:
   :undoc-members:
   :show-inheritance:

.. automodule:: {{cookiecutter.python_package_name}}.utils.tracing
   :members:
   :undoc-members:
   :show-inheritance:

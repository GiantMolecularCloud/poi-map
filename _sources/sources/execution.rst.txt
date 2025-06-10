==================
How to run the app
==================

Local execution
===============

- (if necessary) Install `Poetry <https://python-poetry.org/>`_: see `Poetry installation <https://python-poetry.org/docs/#installation>`_
- Install the project: ``poetry install``
- Run the app: ``poetry run poi-map tests/test-data/local_execution/config.json``
- If your default browser does not open automatically, open the app at ``127.0.0.1:8080``

To customize the app:
- Copy the demo config file from ``tests/test-data/local_execution/config.json`` and customize it.
- Run the app: ``poetry run poi-map customized_config.json``
- If your default browser does not open automatically, open the app at ``127.0.0.1:8080``

Docker
======

-   Build the image: ``docker build -t poi-map:latest -f docker/Dockerfile .``
-   Customize the config file in ``tests/test-data/docker/config.json`` and save it as ``config.json``.
-   Run the container: ``docker run -v /path/to/your/config/directory:/config poi-map:latest poi-map``

Built docker images are also available on `Docker Hub <https://hub.docker.com/r/giantmolecularcloud/poi-map>`_.

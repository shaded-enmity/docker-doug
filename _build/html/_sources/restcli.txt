REST and CLI APIs 
=================

This section describes several APIs for interfacing with ``Docker's`` CLI, Socket, Registry and Hub.

CLI
---

To see all the particular flags definition please refer to: flags.py_

.. _flags.py: https://github.com/shaded-enmity/docker-doug/blob/master/libdoug/api/flags.py#L134

.. automodule:: libdoug.api.flags
   :members:
   :undoc-members:


Remote Base
-----------

.. automodule:: libdoug.api.remote_base
   :members:
   :undoc-members:


Docker Socket API
-----------------

For the description of ``REST`` APIs exposed by ``Docker daemon`` please refer to remote_docker.py_ 

.. _remote_docker.py: https://github.com/shaded-enmity/docker-doug/blob/master/libdoug/api/remote_docker.py


Registry API
------------

For the description of ``REST`` APIs exposed by ``Docker Registry`` please refer to remote_registry.py_ 

.. _remote_registry.py: https://github.com/shaded-enmity/docker-doug/blob/master/libdoug/api/remote_registry.py

Hub API
-------

For the description of ``REST`` APIs exposed by ``Docker Hub`` please refer to remote_hub.py_ 

.. _remote_hub.py: https://github.com/shaded-enmity/docker-doug/blob/master/libdoug/api/remote_hub.py

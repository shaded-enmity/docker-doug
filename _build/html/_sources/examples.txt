Examples
========

The following examples are excerpts from ``doug-cli.py`` that can be found in root directory of the repository at GitHub (https://github.com/shaded-enmity/docker-doug/)

Print local tags
----------------

.. code-block::  python
   :linenos:

   from libdoug.docker_api import DockerLocal
   from libdoug.history import ImageHistory
   docker = DockerLocal()
   repo = 'fedora'

   print "Local tags:"
   local = docker.getimages(repo)
   localhistory = ImageHistory(local)
   localhistory.printout()

Print remote tags
-----------------

.. code-block:: python
   :linenos:

   from libdoug.registry import Registry
   from libdoug.history import ImageHistory
   from libdoug.docker_api import UserInfo
   repo = 'fedora'
   user = UserInfo('me', 'mypass', 'my@mail.org')
   registry = Registry('docker.io')

   print "Remote tags:"
   remotehistory = ImageHistory.fromjson(registry.querytags(repo, user))
   remotehistory.printout()


Visualize dependencies
----------------------

.. code-block:: python
   :linenos:

   from libdoug.docker_api import DockerLocal
   from libdoug.utils import get_image
   from libdoug.dependency_walker import DependencyWalker
   from libdoug.graph import DependencyType
   docker = DockerLocal()
   img = 'fedora:21'

   print "Dependency Walker:"
   allimages = docker.getallimages()
   image = get_image(img, allimages)
   walker = DependencyWalker(image, DependencyType.IMAGE)
   walker.walk(docker.getallimages())


Explain Docker Commands
-----------------------

.. code-block:: python
   :linenos:

   from libdoug.api.flags import parse_cli

   cli = parse_cli('docker run -it --rm -p 3000:3000 -v /:/volume -v /another:/some/place/else -e A=B -e B=C myImage /bin/bash -c "echo Test!"')
   print 'Flags:   ', "\n	  ".join(["%s = %s"%a for a in cli.flags])
   print 'Verb:    ', cli.verb
   print 'Context: ', cli.context
   print 'Workdir: ', os.getcwd()

Make conflict solvers do your bidding
-------------------------------------

Please refer to doug-cli_ example.

.. _doug-cli: https://github.com/shaded-enmity/docker-doug/blob/master/doug-cli.py#L54

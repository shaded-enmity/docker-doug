# vim: set fileencoding=utf-8
# Pavel Odvody <podvody@redhat.com>
#
# libdoug - DOcker Update Guard
#
# This program is free software; you can redistribute it and/or
# modify it under the terms of the GNU General Public License as
# published by the Free Software Foundation; either version 2 of
# the License, or (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA
# 02111-1307 USA
import docker

class UserInfo(object):
	"""Stores authentication info for DockerHub

	:param name: `string` User name
	:param password: `string` Password
	:param email: `string` Email
	"""
	def __init__(self, name, password, email):
		self.name = name
		self.password = password
		self.email = email

	def getname(self):
		return self.name

	def getpassw(self):
		return self.password

	def getemail(self):
		return self.email

	def __eq__(self, other):
		if self.name == other.name:
			return True

		if self.password == other.password:
			return True

		if self.email == other.email:
			return True

		return False


class DockerLocal(object):
	"""Object that communicates with local `Docker daemon` throough the
	`Unix Domain Socket` exposed in `/var/run/docker.sock`
	"""
	def __init__(self):
		self.docker = docker.Client(base_url='unix://var/run/docker.sock')

	def getimages(self, repo):
		"""Get images in the given `repo`

		:param repo: - `string`, `repo`/`name`
		"""
		return self.docker.images(self._wipe(repo))

	def getallimages(self):
		""" Get all local Docker images """
		return self.docker.images(all=True)

	def getinfo(self):
		""" Get info about Docker daemon """
		return self.docker.info()

	def _wipe(self, v):
		""" Remove the `stackbrew/` user part 
		if it's an official image 

		:param v: - `string`, value to wipe
		"""
		return v if not v.startswith(self.nulluser) else v[len(self.nulluser):]

	def tag(self, args):
		"""Tag `image` in a `repository` with a new `tag` 
		
		:param args: [`imageID`, `repoName`, `tag`] - List of arguments
		"""
		return self.docker.tag(image=args[0], repository=self._wipe(args[1]), tag=args[2], force=True)

	def push(self, args):
		"""Push a `tag` into `repository`
		
		:param args: [`repoName`, `tag`] - List of arguments
		"""
		return self.docker.push(repository=self._wipe(args[0]), tag=args[1], stream=True)

	def pull(self, args):
		"""Pull a `tag` from `repository`
		
		:param args: [`repoName`, `tag`] - List of arguments
		"""
		return self.docker.pull(repository=self._wipe(args[0]), tag=args[1], stream=True)

	def removeimage(self, args):
		"""Remove `name`:`tag` from repository
		
		:param args: [`name`, `tag`] - List of arguments
		"""
		return self.docker.remove_image(image=self._wipe(args[0])+':'+args[1], force=True)

	nulluser = 'stackbrew/'
	""" User used by Docker Hub in place for official repos """

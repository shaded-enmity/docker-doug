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
import json
from libdoug.utils import flag_gen

class ResolutionType(object):
	""" Generic type of the resolution """
	(NONE, TAG, PUSH, PULL, REMOVE) = flag_gen(5)


class Resolution(object):
	""" A solution to your conflicts """
	def __init__(self, rtype, args):
		"""
		:param:`rtype` - ResolutionType, Type of the resolution
		:param:`args` - list, Arguments to use during execution
		"""
		self.type = rtype
		self.args = args

	def gettype(self):
		"""
		:return: ResolutionType
		"""
		return self.type

	def getargs(self):
		"""
		:return: list
		"""
		return self.args 

	def _getstream(self, stream):
		"""
		:param:`stream` - string generator, Input stream
		"""
		def _format(obj):
			if u'progress' in obj:
				return '%s %s' % (obj['status'], obj['progress'])
			return obj['status']

		for sl in stream:
			print u'  │├╼', _format(json.loads(sl))

		print u'  │╰╼ Finished' 

	def execute(self, docker):
		"""
		Execute refactoring, it's in a
		desparate need of one.
		:param:`docker` - DockerLocal, Instance of DockerLocal
		:return: list of changes
		"""
		command = { 
			ResolutionType.TAG:  u'  ┍ docker tag %s %s:%s',
			ResolutionType.REMOVE:  u'  ┍ docker rmi %s:%s',
			ResolutionType.PUSH: u'  ┍┯ docker push %s:%s',
			ResolutionType.PULL: u'  ┍┯ docker pull %s:%s'
		}.get(self.type) % self.args
		print command

		if self.type == ResolutionType.TAG:
			done = docker.tag(self.args)
			if done:
				print u'  ╰╼ done! '
			else:
				raise Exception('Tag error!')

		elif self.type == ResolutionType.PUSH:
			stream = docker.push(self.args)
			self._getstream(stream)
			print u'  ╰╼ done!'

		elif self.type == ResolutionType.PULL:
			stream = docker.pull(self.args)
			self._getstream(stream)
			print u'  ╰╼ done!'

		elif self.type == ResolutionType.REMOVE:
			done = docker.removeimage(self.args)
			if done:
				print u'  ╰╼ done! '
			else:
				print u'  ╰╼ node done! :/ '

		return command

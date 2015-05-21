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
from libdoug.token import RequestToken
from libdoug.decorators import http_request_decorate, RequestDecorator
from libdoug.history import ImageHistory
from libdoug.http import HTTPRequest
from libdoug.api.remote_distv2 import manifest_get

class BearerTokenDecorator(RequestDecorator):
	""" Decorates the request with bearer token

	:param token: Token to decorate with
	:type  token: libdoug.token.RequestToken
	"""
	def __init__(self, token):
		self.token = token
		super(BearerTokenDecorator, self).__init__()

	def _decorate(self, request):
		if not request.addheader(u'Authorization', u'Bearer {0}'.format(self.token.gettoken())):
			return False

		return super(BearerTokenDecorator, self)._decorate(request)

class Registry(object):
	"""Provides encapsulation for interacting with the Docker registry.

	:param registry: Domain name of the registry
	:type  registry: str
	"""
	def __init__(self, registry):
		self.registry = registry

	def getregistry(self):
		return self.registry

	def _ensuretoken(self, repo):
		"""Make sure `user` has a token for `repo`

		:param repo: Name of the repository
		:type  repo: str
		:param user: :class:`libdoug.docker_api.UserInfo`, Hub User
		:type  user: libdoug.docker_api.UserInfo 
		:return: A valid ``RequestToken``
		:rtype: libdoug.token.RequestToken
		"""
		token = self.authtoken(repo)
		if not token:
			raise Exception('Authorization failed!')

		return token
		
	def querydigest(self, repo, tag):
		"""Query the remote `repo`:`tag` for `digest`

		:param repo: Target repository
		:type  repo: str
		:param tag: Tag to query
		:type  tag: str
		:return: Digest of the requested image
		:rtype: str
		"""
		token = self._ensuretoken(repo)
		url = manifest_get.formaturl('https://registry-1.'+self.registry, (repo, tag))
		manifest = HTTPRequest(url)
		success = http_request_decorate(manifest, BearerTokenDecorator(token))
		if success:
			response = manifest.request()
			if response.getcode() == 200:
				return response.getheader('Docker-Content-Digest')
			else:
				print 'Bad response code: %d\nText:\n%s' %\
					(response.getcode(), response.getcontent())
		else:
			print 'RequestTokenDecorator has failed'
				
		return None

	def authtoken(self, repo):
		"""Performs bearer authentication for `repo`
		
		:param repo: Target repository
		:type  repo: str
		:return: A valid :class:`libdoug.token.RequestToken` or ``None`` on error
		:rtype: libdoug.token.RequestToken
		"""
		url = u'https://auth.{0}/v2/token/?scope=repository:{1}:pull&service=registry.{0}'.format(self.registry, repo)
		login_request = HTTPRequest(url)
		response = login_request.request()
		if response.getcode() == 200:
			r = json.loads(response.getcontent())
			return RequestToken(repo, None, r['token'])
		else:
			print 'Bad response code: %d\nText:\n%s' %\
				(response.getcode(), response.getcontent())
		return None

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
from libdoug.decorators import RequestTokenDecorator, \
			UserCredentialsDecorator, \
			http_request_decorate
from libdoug.history import ImageHistory
from libdoug.token import TokenCache, RequestToken
from libdoug.http import HTTPRequest
from libdoug.api.remote_registry import repository_tags_get
from libdoug.api.remote_hub import repository_list

class Registry(object):
	"""Provides encapsulation for interacting with the Docker registry.

	:param str registry: Domain name of the registry
	"""
	def __init__(self, registry):
		self.cache = TokenCache()
		self.cache.load('.tokencache.'+registry)
		self.registry = registry

	def getregistry(self):
		return self.registry

	def _ensuretoken(self, repo, user):
		"""Make sure `user` has a token for `repo`

		:param str repo: Name of the repository
		:param libdoug.docker_api.UserInfo user: :class:`libdoug.docker_api.UserInfo`, Hub User
		:return: A valid ``RequestToken``
		:rtype: libdoug.token.RequestToken
		"""
		cached = self.cache.gettokenfor(repo, user)
		if cached:
			return cached[0]
		
		token = self.authtoken(repo, user)
		if not token:
			raise Exception('Authorization failed!')

		return token
		
	def querytags(self, repo, user):
		"""Query the remote `repo` as `user` for a list
		of all tags

		:param str repo: Target repository
		:param libdoug.docker_api.UserInfo user: :class:`libdoug.docker_api.UserInfo`, Hub User
		:return: ``JSON Object`` of (`Id`, `Tag`) pairs
		:rtype: dict
		"""
		token = self._ensuretoken(repo, user)
		url = repository_tags_get.formaturl('https://registry-1.'+self.registry, repo.split('/'))
		tags_request = HTTPRequest(url)
		success = http_request_decorate(tags_request, RequestTokenDecorator(token))
		if success:
			response = tags_request.request()
			if response.getcode() == 200:
				return json.loads(response.getcontent())
			else:
				print 'Bad response code: %d\nText:\n%s' %\
					(response.getcode(), response.getcontent())
		else:
			print 'RequestTokenDecorator has failed'
				
		return None

	def authtoken(self, repo, user):
		"""Performs authentication for `repo` as `user`
		
		:param str repo: Target repository
		:param libdoug.docker_api.UserInfo user: :class:`libdoug.docker_api.UserInfo`, Hub User
		:return: A valid :class:`libdoug.token.RequestToken` or ``None`` on error
		:rtype: libdoug.token.RequestToken
		"""
		url = repository_list.formaturl('https://index.'+self.registry, repo.split('/'))
		login_request = HTTPRequest(url)
		success = http_request_decorate(login_request, UserCredentialsDecorator(user))
		if success:
			response = login_request.request()
			if response.getcode() == 200:
				raw_token = response.getheader('X-Docker-Token')
				token = raw_token[10:50]
				rt = RequestToken(repo, user, token)
				self.cache.addtoken(rt)
				self.cache.save('.tokencache.'+self.registry)
				return rt
			else:
				print 'Bad response code: %d\nText:\n%s' %\
					(response.getcode(), response.getcontent())
		else:
			print 'UserCredentialsDecorator has failed'
		return None

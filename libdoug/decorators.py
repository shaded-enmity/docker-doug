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
class RequestDecorator(object):
	""" Base class for all request decorators """
	def _decorate(self, request):
		return True


class RequestTokenDecorator(RequestDecorator):
	""" Decorates the request with auth token 
	
	:param token: Token to decorate with
	:type  token: libdoug.token.RequestToken
	"""
	def __init__(self, token):
		self.token = token
		super(RequestTokenDecorator, self).__init__()

	def _decorate(self, request):
		header_string = 'Token signature=%s,repository=%s,access=%s' %\
					(self.token.gettoken(), self.token.getrepo(),
					 self.token.getaccess())

		if not request.addheader('Authorization', header_string):
			return False

		return super(RequestTokenDecorator, self)._decorate(request)


class UserCredentialsDecorator(RequestDecorator):
	""" Decorates the request with user credentials and necessary header 
	
	:param user: User to decorate with
	:type  user: libdoug.docker_api.UserInfo
	"""
	def __init__(self, user):
		self.user = user
		super(UserCredentialsDecorator, self).__init__()

	def _decorate(self, request):
		if not request.addheader('X-Docker-Token', 'true'):
			return False

		if not request.addbauth(self.user.getname(), self.user.getpassw()):
			return False

		return super(UserCredentialsDecorator, self)._decorate(request)


def http_request_decorate(request, decorator):
	""" Apply `decorator` and return `success` """
	return decorator._decorate(request)

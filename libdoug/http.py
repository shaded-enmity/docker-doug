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
import requests
from clint.textui import progress

class HTTPResponse(object):
	"""A HTTP response encapsulation returned by :meth:`HTTPRequest.request`

	:param request: The original :class:`HTTPRequest` object
	:param response: The response object returned by `requests.get`
	"""
	def __init__(self, request, response):
		self.request = request
		self.response = response

	def getcode(self):
		""" HTTP status code """
		return self.response.status_code

	def getheader(self, key):
		""" Get header by `key`
		
		:param key: `string` Header to retrieve
		"""
		return self.response.headers[key]

	def getcontent(self):
		""" Get the content / response body """
		return self.response.text


class HTTPRequest(object):
	"""Initiate a HTTP request to a `url`
	
	:param url: `string` Target URL 
	"""
	def __init__(self, url):
		self.url = url
		self.headers = {}
		self.auth = None

	def addheader(self, key, value):
		""" Add custom header `key` with value `value` """
		self.headers[key] = value
		return True

	def addbauth(self, name, pw):
		""" Add basic HTTP Auth options
		
		:param name: `string` Username
		:param pw: `string` Password
		"""
		self.auth = (name, pw)
		return True

	def request(self):
		""" Perform the actual request
		
		:returns: :class:`HTTPResponse` object
		"""
		res = requests.get(self.url, headers=self.headers, auth=self.auth)
		return HTTPResponse(self, res)

	def requeststream(self, savepath):
		r = requests.get(self.url, headers=self.headers, stream=True)
		with open(savepath, 'wb') as f:
			total_length = int(r.headers.get('content-length'))
			for chunk in progress.bar(r.iter_content(chunk_size=1024), label='        ',  expected_size=(total_length/1024) + 1, width=63): 
				if chunk:
			    		f.write(chunk)
			    		f.flush()
		return HTTPResponse(self, r)

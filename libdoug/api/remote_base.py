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

class DockerAPIRequest(object):
	"""
	Class describing a generic
	Docker Remote API request
	"""
	def __init__(self):
		self.desc = ''
		self.type = ''
		self.url = ''
		self.url_sub = []
		self.get_params = []
		self.filters = []
		self.json = []
		self.status = []
		self.headers = []

	def formaturl(self, endpoint, subs):
		url, delta = self.url, 0
		subs = list(reversed(subs))
		for s in self.url_sub:
			val = subs.pop()
			url = url[:s[0]+delta] + val + url[s[1]+delta:]
			delta = len(val) - (s[1]-s[0])
		return endpoint + url

	@staticmethod
	def new(**kv):
		dar = DockerAPIRequest()
		for (key, value) in kv.iteritems():
			setattr(dar, key, value)
		return dar

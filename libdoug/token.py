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
from libdoug.docker_api import UserInfo
from datetime import timedelta, datetime

class AccessValue(object):
	"""
	The type of access we need from the registry
	"""
	Read = 'read'
	Write = 'write'
	ReadWrite = 'read,write'


class RequestToken(object):
	"""
	Token to get us talking with the registry
	"""
	def __init__(self, repo, user, token, access=AccessValue.Read):
		self.token = token
		self.repo = repo
		self.user = user
		self.access = access

	def gettoken(self):
		return self.token

	def getrepo(self):
		return self.repo

	def getuser(self):
		return self.user

	def getaccess(self):
		return self.access


class TokenCache(object):
	entry_lifespan = 3600*2

	class CacheEntry(object):
		"""
		Cache the tokens for 2hours
		"""
		def __init__(self, token):
			""" """
			self.token = token
			self.expire = datetime.now() + timedelta(0, TokenCache.entry_lifespan)

		def gettoken(self):
			""" Get the value of the token """
			return self.token

		def hasexpired(self):
			""" Has the token expired """
			return self.expire < datetime.now()

		def asdictionary(self):
			""" Format us as a dictionary """
			return {
				'Token': { 
					'Token': self.gettoken().gettoken(),
					'Repo': self.gettoken().getrepo(),
					'User': {
						'Name': self.gettoken().getuser().getname(),
						'Password': self.gettoken().getuser().getpassw(),
						'Email': self.gettoken().getuser().getemail()
					},
					'Access': self.gettoken().getaccess()
				},
				'Expire': str(self.expire)
			}

		@staticmethod
		def fromdictionary(d):
			"""  """
			td, ud = d['Token'], d['Token']['User']
			user = UserInfo(ud['Name'], ud['Password'], ud['Email'])
			token = RequestToken(td['Repo'], user, td['Token'], td['Access'])
			entry = TokenCache.CacheEntry(token)
			entry.expire = datetime.strptime(d['Expire'], '%Y-%m-%d %H:%M:%S.%f')
			return entry
			
	
	def __init__(self):
		self.cache = {}

	def addtoken(self, token):
		repo = token.getrepo()
		if repo in self.cache:
			self.cache[repo].append(self.CacheEntry(token))
		else:
			self.cache[repo] = [self.CacheEntry(token)]
		return True

	def gettokenfor(self, repo, user):
		if not repo in self.cache:
			return None

		tokens = [t for t in self.cache[repo] if t.gettoken().getuser() == user]
		valid = [t for t in tokens if not t.hasexpired()]

		purge = set(tokens) - set(valid)
		for p in purge:
			print "Purging expired token:", p.gettoken().gettoken()
			self.cache[repo].remove(p)
		if purge:
			print ''

		return [t.gettoken() for t in valid]

	def save(self, savefile='.tokencache'):
		fd = open(savefile, 'w+')
		dump = json.dump({k:[w.asdictionary() for w in v] for k,v in self.cache.iteritems()}, fd, separators=(',', ':'))
		#print 'Token cache saved into: %s' % savefile
		fd.close()
		return dump

	def load(self, loadfile='.tokencache'):
		fd = open(loadfile, 'a+')
		try:
			cachedict = json.load(fd)
			for k, v in cachedict.iteritems():
				self.cache[k] = [self.CacheEntry.fromdictionary(v[0])]
		except ValueError:
			self.cache = {}

		fd.close()
		#print 'Token cache loaded from %s:\n%s' % (loadfile, self.cache)
		return self.cache

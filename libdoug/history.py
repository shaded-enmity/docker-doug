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
from libdoug.values import EmptyDiff

class ImageHistory(object):
	class Entry(object):
		def __init__(self, tag, imgid):
			self.tag = tag
			self.id = imgid

		def gettag(self):
			return self.tag

		def getid(self):
			return self.id

		def __repr__(self):
			return "%s : %s" % (self.gettag(), self.getid())

		def __eq__(self, other):
			return self.tag == other.tag and self.id == other.id

		def __hash__(self):
			return hash(self.tag + self.id)

		def __gt__(self, other):
			return cmp(self.tag, other.tag) == 1


	def __init__(self, images):
		self.images = []
		self._addimages(images)

	@staticmethod
	def fromjson(json):
		hist = ImageHistory([])
		for k, v in json.iteritems():
			hist.images.append(ImageHistory.Entry(k, v))		
		return hist

	def _addimages(self, images):
		for img in images:
			for repotag in img['RepoTags']:
				self.images.append(
					self.Entry(repotag.split(':')[1], img['Id'])
				)

	def getimages(self):
		return self.images

	def printout(self):
		for n, img in enumerate(sorted(self.images)):
			print "  %s" % (img)


class HistoryDiff(object):
	def __init__(self, a, b):
		self.a = a
		self.b = b

	def diff(self):
		a, b = set(self.a.getimages()), set(self.b.getimages())
		if a == b:
			return EmptyDiff

		return (list(a - b), list(b - a))

	@staticmethod
	def printout(delta):
		left, right = delta
		if left:
			print '\n'.join(['  L '+str(i) for i in sorted(list(left))])
		
		if right:
			print '\n'.join(['  R '+str(i) for i in sorted(list(right))])

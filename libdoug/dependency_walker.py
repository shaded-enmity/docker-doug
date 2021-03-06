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
from libdoug.graph import GraphNode, TreeState

def graph_walk_callback(image, ts, islast):
	"""Implements a generic callback used during walking the graph

	:param image: Image Dictionary
	:type  image: dict
	:param ts: State of the tree
	:type  ts: libdoug.graph.TreeState
	:param islast: Denotes a leaf node
	:type  islast: bool
	"""
	pass

def _print_callback(image, ts, islast):
	print ts.formatline(image, islast)

class DependencyWalker(object):
	""" Tree-drawing dependency walker

	:param tid: ID for which walk the dependencies
	:type  tid: str
	:param deptype: Image or Container
	:type  deptype: libdoug.graph.DependencyType
	"""
	def __init__(self, tid, deptype):
		self.id = tid
		self.deptype = deptype

	def _findchildren(self, images, tid=None):
		"""Find children nodes of `tid` or `self`.`id`

		:param images: Docker images to search
		:type  images: dict[str, dict] 
		:param tid: ID whose children to get
		:type  tid: str
		:return: `List` of `Image Dictionaries`
		:rtype: list[dict[str, dict]]
		"""
		tid = tid if tid else self.id
		return [v for k, v in images.iteritems() if v['ParentId'] == tid]

	def _imagechain(self, allimages):
		"""Find all the parents of `self`.`id` image

		:param allimages: All Docker images
		:type  allimages: dict[str, dict] 
		:return: `List` of `Image Dictionaries`
		:rtype: list[dict[str, dict]]
		"""
		img = allimages[self.id]
		chain = [img]
		while img['ParentId'] != '':
			img = allimages[img['ParentId']]
			chain.append(img)
		return chain

	def _listtomap(self, allimages):
		"""Convert input list into a `Id`-`Image Dictionary` mapping

		:param allimages: Flat list of all Docker images
		:type  allimages: list
		:return: `Id`-`Image Dictionary` `dict` 
		:rtype: dict[str, dict]
		"""
		return {img['Id']: img for img in allimages}

	def _walkrecurse(self, images, allimages, level=0):
		for img in images:
			print u' '*level + u' %s %s' % (img['Id'], img['RepoTags'] if img['RepoTags'][0] != EmptyTag else '')
			children = self._findchildren(allimages, img['Id'])
			if children:
				self._walkrecurse(children, allimages, level+1)

	def makegraph(self, root, allimages):
		"""Make a graph of `root` nodes children

		:param root: From where to start constructing the graph
		:type  root: libdoug.graph.GraphNode 
		:param allimages: `dict`, All Docker images
		:type  allimages: dict[str, dict]
		:return: `root` node
		:rtype: libdoug.graph.GraphNode
		"""
		children = self._findchildren(allimages, root.getid())
		for c in children:
			self.makegraph(root.addchild(c['Id']), allimages)
		return root

	def walkgraphrecurse(self, root, allimages, ts, walkcb):
		"""Walk the graph from `root`

		:param root: From where to start constructing the graph
		:type  root: libdoug.graph.GraphNode 
		:param allimages: All Docker images
		:type  allimages: dict[str, dict] 
		:param ts: Current state of the tree
		:type  ts: libdoug.graph.TreeState 
		:param walkcb: Used during graph walk
		:type  walkcb: graph_walk_callback
		"""
		allchildren = [v for v in root.getchildren()]
		nchildren, link, img = len(allchildren), len(allchildren) > 1, allimages[root.getid()]

		potestsolumunum = nchildren == 0
		
		walkcb(img, ts, potestsolumunum)
		
		if potestsolumunum:
			return

		first, intermediary, last = allchildren[0], allchildren[1:-1], allchildren[-1]

		if first:
			ts.pushbranch(link)
			self.walkgraphrecurse(first, allimages, ts, walkcb)
			ts.popbranch()
		if intermediary:
			ts.pushbranch(link)
			for c in intermediary:
				self.walkgraphrecurse(c, allimages, ts, walkcb)
			ts.popbranch()
		if last and last != first:
			ts.pushbranch(False)
			self.walkgraphrecurse(last, allimages, ts, walkcb)
			ts.popbranch()

	def printtree(self, allimages):
		"""Print the graph as nicely structured tree

		:param allimages: All Docker images
		:type  allimages: dict[str, dict]
		"""
		rootnode, ts = GraphNode(None, self.id), TreeState()
		self.makegraph(rootnode, allimages)
		self.walkgraphrecurse(rootnode, allimages, ts, _print_callback)

	def walk(self, allimages):
		"""Bootstrap the walker and just printout for now

		:param allimages: All Docker images
		:type  allimages: list[dict]
		"""
		allimages = self._listtomap(allimages)
		ancestry = self._imagechain(allimages)

		#self._walkrecurse(ancestry, allimages)
		self.printtree(allimages)

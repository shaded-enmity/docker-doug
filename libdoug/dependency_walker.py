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

	:param dict image: Image Dictionary
	:param libdoug.graph.TreeState ts: State of the tree
	:param bool islast: Denotes a leaf node
	"""
	pass

def _print_callback(image, ts, islast):
	print ts.formatline(image, islast)

class DependencyWalker(object):
	""" Tree-drawing dependency walker

	:param str tid: ID for which walk the dependencies
	:param libdoug.graph.DependencyType deptype: Image or Container
	"""
	def __init__(self, tid, deptype):
		self.id = tid
		self.deptype = deptype

	def _findchildren(self, images, tid=None):
		"""Find children nodes of `tid` or `self`.`id`

		:param dict[str, dict] images: Docker images to search
		:param str tid: ID whose children to get
		:return: `List` of `Image Dictionaries`
		:rtype: list[dict[str, dict]]
		"""
		tid = tid if tid else self.id
		return [v for k, v in images.iteritems() if v['ParentId'] == tid]

	def _imagechain(self, allimages):
		"""Find all the parents of `self`.`id` image

		:param dict[str, dict] allimages: All Docker images
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

		:param list allimages: Flat list of all Docker images
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

		:param libdoug.graph.GraphNode root: From where to start constructing the graph
		:param dict[str, dict] allimages: `dict`, All Docker images
		:return: `root` node
		:rtype: libdoug.graph.GraphNode
		"""
		children = self._findchildren(allimages, root.getid())
		for c in children:
			self.makegraph(root.addchild(c['Id']), allimages)
		return root

	def walkgraphrecurse(self, root, allimages, ts, walkcb):
		"""Walk the graph from `root`

		:param libdoug.graph.GraphNode root: From where to start constructing the graph
		:param dict[str, dict] allimages: All Docker images
		:param libdoug.graph.TreeState ts: Current state of the tree
		:param graph_walk_callback walkcb: Used during graph walk
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

		:param dict[str, dict] allimages: All Docker images
		"""
		rootnode, ts = GraphNode(None, self.id), TreeState()
		self.makegraph(rootnode, allimages)
		self.walkgraphrecurse(rootnode, allimages, ts, _print_callback)

	def walk(self, allimages):
		"""Bootstrap the walker and just printout for now

		:param list[dict] allimages: All Docker images
		"""
		allimages = self._listtomap(allimages)
		ancestry = self._imagechain(allimages)

		#self._walkrecurse(ancestry, allimages)
		self.printtree(allimages)

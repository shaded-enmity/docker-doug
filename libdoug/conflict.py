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
from libdoug.conflict_resolution import Resolution
from libdoug.utils import flag_gen

class ConflictType(object):
	""" ``LEFT`` is local and ``RIGHT`` is Remote """
	(NONE, LEFT, RIGHT) = flag_gen(3)
	BOTH = LEFT | RIGHT 

class ConflictSolver(object):
	""" :class:`ConflictSolver` is a base class for implementing
	other conflict solvers.

	:param list allimages: All local images
	:param (list, list) delta: Delta information between ``Left``/``Right``
	:param str repo: Name of the repository
	:param libdoug.conflict_resolution.Resolution rt: Class representing conflict resolutions - :class:`libdoug.conflict_resolution.Resolution`
	"""
	def __init__(self, allimages, delta, repo, rt=Resolution):
		self.allimages = allimages
		self.delta = delta
		self.repo = repo
		self.resolution_type = rt

	def handleleft(self, left, resolutions):
		"""Handle `left` or (local) side of conflict

		:param list left: List of tags to handle
		:param list resolutions: Add resolutions to this list
		:return: :class:`ConflictType.LEFT`
		"""
		return ConflictType.LEFT

	def handleright(self, right, resolutions):
		"""Handle `right` (remote) side of conflict

		:param list right: List of tags to handle
		:param list resolutions: Add resolutions to this list
		:return: :class:`ConflictType.RIGHT`
		"""
		return ConflictType.RIGHT

	def solve(self, resolutions=None):
		"""Solve and return resolutions

		:param list resolutions: `list`, Add resolutions to this list
		:return: List of resolutions
		:rtype: list[libdoug.conflict_resolution.Resolution]
		"""
		return resolutions

	def addresolution(self, resolutions, rtype, args):
		"""Add resolution to a list of resolutions

		:param list resolutions: Add resolutions to this list
		:param libdoug.conflict_resolution.ResolutionType rtype: Type of the resolution
		:param list args: Args to use during resolution
		"""
		resolutions.append(self.resolution_type(rtype, args))

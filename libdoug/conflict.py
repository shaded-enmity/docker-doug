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

	:param allimages: All local images
	:type  allimages: list
	:param delta: Delta information between ``Left``/``Right``
	:type  delta: (list, list)
	:param repo: Name of the repository
	:type  repo: str
	:param rt: Class representing conflict resolutions - :class:`libdoug.conflict_resolution.Resolution`
	:type  rt: libdoug.conflict_resolution.Resolution 
	"""
	def __init__(self, allimages, delta, repo, rt=Resolution):
		self.allimages = allimages
		self.delta = delta
		self.repo = repo
		self.resolution_type = rt

	def handleleft(self, left, resolutions):
		"""Handle `left` or (local) side of conflict

		:param left: List of tags to handle
		:type  left: list
		:param resolutions: Add resolutions to this list
		:type  resolutions: list
		:return: :class:`ConflictType.LEFT`
		"""
		return ConflictType.LEFT

	def handleright(self, right, resolutions):
		"""Handle `right` (remote) side of conflict

		:param right: List of tags to handle
		:type  right: list
		:param resolutions: Add resolutions to this list
		:type  resolutions: list
		:return: :class:`ConflictType.RIGHT`
		"""
		return ConflictType.RIGHT

	def solve(self, resolutions=None):
		"""Solve and return resolutions

		:param resolutions: Add resolutions to this list
		:type  resolutions: list
		:return: List of resolutions
		:rtype: list[libdoug.conflict_resolution.Resolution]
		"""
		return resolutions

	def addresolution(self, resolutions, rtype, args):
		"""Add resolution to a list of resolutions

		:param resolutions: Add resolutions to this list
		:type  resolutions: list
		:param rtype: Type of the resolution
		:type  rtype: libdoug.conflict_resolution.ResolutionType
		:param args: Args to use during resolution
		:type  args: list
		"""
		resolutions.append(self.resolution_type(rtype, args))

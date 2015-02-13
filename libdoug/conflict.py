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

	:param allimages: list, All local images
	:param delta: tuple of lists, Delta information between ``Left``/``Right``
	:param repo: string, Name of the repository
	:param rt: `class`, Class representing conflict resolutions - :class:`libdoug.conflict_resolution.Resolution`
	"""
	def __init__(self, allimages, delta, repo, rt=Resolution):
		self.allimages = allimages
		self.delta = delta
		self.repo = repo
		self.resolution_type = rt

	def handleleft(self, left, resolutions):
		"""Handle `left` or (local) side of conflict

		:param left: `list`, List of tags to handle
		:param resolutions: `list`, Add resolutions to this list
		:return: :class:`ConflictType.LEFT`
		"""
		return ConflictType.LEFT

	def handleright(self, right, resolutions):
		"""Handle `right` (remote) side of conflict

		:param right: `list`, List of tags to handle
		:param resolutions: `list`, Add resolutions to this list
		:return: :class:`ConflictType.RIGHT`
		"""
		return ConflictType.RIGHT

	def solve(self, resolutions=None):
		"""Solve and return resolutions

		:param resolutions: `list`, Add resolutions to this list
		:return: `list`, List of resolutions
		"""
		return resolutions

	def addresolution(self, resolutions, rtype, args):
		"""Add resolution to a list of resolutions

		:param resolutions: `list`, Add resolutions to this list
		:param rtype: :class:`libdoug.conflict_resolution.ResolutionType`, Type of the resolution
		:param args: `list`, Args to use during resolution
		"""
		resolutions.append(self.resolution_type(rtype, args))

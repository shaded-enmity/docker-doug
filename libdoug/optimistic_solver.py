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
from libdoug.conflict import ConflictSolver
from libdoug.conflict_resolution import ResolutionType

class OptimisticConflictSolver(ConflictSolver):
	""" This sublcass of :class:`libdoug.conflict.ConflictSolver` class is called optimistic
	because it works as follows:
		
		1) Push what's missing in the remote
		2) Pull what's missing locally

	Conflicts are solved by syncing both sides to be the same, it could also be called naive.

	.. note:: `libdoug` also bundles other, more intricate solvers, such as the :class:`libdoug.vr_solver.VRConflictSolver`
	"""
	def handleleft(self, left, res):
		for tag in left:
			self.addresolution(res, ResolutionType.PUSH, (self.repo, tag.gettag()))

		return super(OptimisticConflictSolver, self).handleleft(left, res)

	def handleright(self, right, res):
		for tag in right:
			handled = False
			for img in self.allimages:
				if img['Id'] == tag.getid():
					self.addresolution(res, ResolutionType.TAG, (tag.getid(), self.repo, tag.gettag()))
					handled = True
					break
			if not handled:
				self.addresolution(res, ResolutionType.PULL, (self.repo, tag.gettag()))

		return super(OptimisticConflictSolver, self).handleright(right, res)

	def solve(self, resolutions=None):
		left, right = self.delta
		resolutions = []
		if not left:
			if not right:
				print " Nothing to do"
			else:
				self.handleright(right, resolutions)
		else:
			if not right:
				self.handleleft(left, resolutions)
			else:
				self.handleleft(left, resolutions)
				self.handleright(right, resolutions)

		return super(OptimisticConflictSolver, self).solve(resolutions)

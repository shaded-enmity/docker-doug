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
from libdoug.conflict_resolution import Resolution, ResolutionType
from libdoug.values import VRMatch

class VRTag(object):
	"""Wrapper around :class:`ImageHistory.Entry <libdoug.history.ImageHistory.Entry>` to support Version-Release ordering"""
	def __init__(self, entry):
		self.entry = entry
		self.invalid = False
		self._parsetag(entry.gettag())

	def _parsetag(self, tag):
		p = VRMatch.match(tag)
		if p:
			self.major, self.minor, self.build, self.release = p.groups()
		else:
			self.major, self.minor, self.build, self.release = (0, 0, 0, 0)
			self.invalid = True

	def isinvalid(self):
		return self.invalid

	def __cmp__(self, other):
		return self.entry == other.entry

	def __gt__(self, other):
		if self.major == other.major:
			if self.minor == other.minor:
				if self.build == other.build:
					return cmp(self.release, other.release) == 1
				else:
					return cmp(self.build, other.build) == 1
			else:
				return cmp(self.minor, other.minor) == 1
		else:
			return cmp(self.major, other.major) == 1

	def __repr__(self):
		return str(self.entry)


class VRConflictSolver(ConflictSolver):
	"""``Version-Release`` subclass of :class:`ConflictSolver <libdoug.conflict.ConflictSolver>`"""
	def __init__(self, allimages, delta, repo, rt=Resolution):
		super(VRConflictSolver, self).__init__(allimages, delta, repo, rt)
		self.localhead = None

	def getlocalhead(self):
		"""Local head is available after :meth:`solve` had been called"""
		return self.localhead

	def solve(self, resolutions=None):
		"""For more information see :meth:`ConflictSolver.solve <libdoug.conflict.ConflictSolver.solve>` """
		local, remote = self.delta

		localtags = sorted(t for t in [VRTag(e) for e in local.getimages()] if not t.isinvalid())
		remotetags = sorted(t for t in [VRTag(e) for e in remote.getimages()] if not t.isinvalid())

		if not localtags and not remotetags:
			print ' Repo not conforming to Version-Release updating'
			return super(VRConflictSolver, self).solve(resolutions)

		self.localhead, remotehead, localtail, remotetail = localtags[-1], remotetags[-1], \
			localtags[0], remotetags[0]

		if self.localhead > remotehead:
			print '  L ', localhead
		elif self.localhead < remotehead:
			print '  R ', remotehead
		else:
			print ' Local and Remote at the same Head: ', self.localhead

		outdated = localtags[:-1]
		
		if outdated:
			print ' Suggested removal of local out-of-date tags:'
			for lt in outdated:
				print '  L ', lt		

		return super(VRConflictSolver, self).solve(resolutions)


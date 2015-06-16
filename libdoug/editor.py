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
import re
from libdoug.utils import flag_gen

class IdentifierType(object):
	(NONE, NAMETAG, DIGEST) = flag_gen(3)

class Identifier(object):
	def __init__(self, itype, value):
		self.type = itype
		self.value = value.replace('.', '\.')

def StrIdent(ident):
	if ident.type == IdentifierType.NAMETAG:
		return 'NAMETAG'
	elif ident.type == IdentifierType.DIGEST:
		return 'DIGEST'

	return 'NONE'

class EditorBase(object):
	def __init__(self, repo):
		self.repo = repo

	def repository(self):
		return self.repo

	def substitute(self, text, idents, subs):
		pass

class DockerfileEditor(EditorBase):
	def __init__(self, repo):
		super(DockerfileEditor, self).__init__(repo)

	def _rematch(self, pattern, line):
		return re.match('.*' + pattern + '.*', line)

	def substitute(self, text, idents, subs):
		assert len(idents) == len(subs)
		s = zip(idents, subs)
		outlines=[]
		for line in text:
			if line.startswith("FROM"):
				newline = None
				r = filter(None, map(lambda (i, k): (i, k) if self._rematch(i.value, line) else None, s))
				if len(r) == 1:
					newline = re.sub(r[0][0].value, r[0][1], line)
					print ' Rebasing: DOCKERFILE_FROM_{0}\n  -{1}  +{2}'.format(StrIdent(r[0][0]), line, newline)
					line = newline
			outlines.append(line)
		return outlines


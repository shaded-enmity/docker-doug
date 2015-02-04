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
import os

def get_image(idname, allimages):
	""" """
	if len(idname) != 64:
		matching = [img for img in allimages if img['Id'].startswith(idname)]
		if not matching:
			named = [img for img in allimages \
					if any(idname in rt for rt in img['RepoTags'])]
			if len(named) == 1:
				return named[0]['Id']
			else:
				raise Exception('Multiple images matching the string: %s' % idname)
		elif len(matching) == 1:
			return matching[0]['Id']
		else:
			raise Exception('Multiple images matching the string: %s' % idname)
	else:
		return idname


def wipe_newlines(data):
	""" """
	if isinstance(data, list):
		return [wipe_newlines(item) for item in data]
	return data.replace('\r', '').replace('\n', '')

def flag_gen(num):
	""" """
	return [0]+[1<<x for x in range(0, num-1)]

class Console(object):
	""" """

	(_h, _w) = (int(x) for x in os.popen('stty size', 'r').read().split())
	@staticmethod
	def width():
		return Console._w

	@staticmethod
	def height():
		return Console._h

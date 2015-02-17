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
from libdoug.values import HashLength

class SollipsistException(Exception):
	""" Thrown if there's more than one results """
	pass

def get_image(idname, allimages):
	"""Find an image by ``id`` or fall back to 
	``name`` search. Both ``id`` and ``name`` can be specified partially
	but an :class:`SollipsistException` is thrown if multiple images are found.

	:param str idname: ``image id`` or ``repo:tag``
	:param list allimages: `list` of all images
	:return: The full ``image id`` or ``None`` if not found
	:rtype: str
	"""
	if len(idname) != HashLength:
		matching = [img for img in allimages if img['Id'].startswith(idname)]
		if not matching:
			named = [img for img in allimages \
					if any(idname in rt for rt in img['RepoTags'])]
			if len(named) == 1:
				return named[0]['Id']
			else:
				raise SollipsistException('Multiple images matching the string: %s' % idname)
		elif len(matching) == 1:
			return matching[0]['Id']
		else:
			raise SollipsistException('Multiple images matching the string: %s' % idname)
	else:
		return idname if any(idname == img['Id'] for img in allimages) else None


def wipe_newlines(data):
	"""Remove newlines from ``data``.
	Works recursively on list of strings too
	
	:param data: `str` or `list` 
	:type data: str or list
	:rtype: str or list
	"""
	if isinstance(data, list):
		return [wipe_newlines(item) for item in data]
	return data.replace('\r', '').replace('\n', '')

def flag_gen(num):
	"""Generate ``num`` bit flags 
	
	:param int num: `int` upper bound 
	:return: `list` of bit flags such as ``len([0, 1, 2, 4 ...]) == num``
	:rtype: list
	"""
	return [0]+[1<<x for x in range(0, num-1)]

class Console(object):
	"""Utility `static class` representing the size
	of the terminal window """

	(_h, _w) = (int(x) for x in os.popen('stty size', 'r').read().split())

	@staticmethod
	def width():
		""" Width of the terminal window """
		return Console._w

	@staticmethod
	def height():
		""" Height of the terminal window """
		return Console._h

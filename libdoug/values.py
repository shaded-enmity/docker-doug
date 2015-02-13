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
EmptyDiff = ([], []) #: Tuple of ``left`` and ``right`` lists 
EmptyTag = u'<none>:<none>' #: Special value representing untagged image
RootImage = u'511136ea3c5a64f264b78b5433614aec563103b4d4702f3ba7d4d2698e22c158' #: Also known as ``scratch`` image in `Docker`
HashLength = 64 #: Full ``image id`` length
VRMatch = re.compile('^(\d)\.(\d)\.(\d)[-]?(.*)$') #: ``X.Y.Z-R`` Version-Release matching

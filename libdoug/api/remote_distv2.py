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

from libdoug.api.remote_base import DockerAPIRequest

manifest_get = DockerAPIRequest.new(desc=u'Get image manifest', type=u'GET',
			url=u'/v2/(repo)/manifests/(tag)', url_sub=[(4, 10), (21, 26)],
			get_params=[],
			filters=[],
			json=[],
			status=[u'200', u'401', u'404'],
			headers=[])

tags_get = DockerAPIRequest.new(desc=u'Get all tags for manifest', type=u'GET',
			url=u'/v2/(repo)/tags/list', url_sub=[(4, 10)],
			get_params=[],
			filters=[],
			json=[],
			status=[u'200', u'401', u'404'],
			headers=[])


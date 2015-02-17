#!/usr/bin/python -tt
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
import argparse, os, shlex, json, shutil, subprocess
from libdoug.docker_api import DockerLocal, UserInfo
from libdoug.history import ImageHistory, HistoryDiff
from libdoug.registry import Registry
from libdoug.vr_solver import VRConflictSolver
from libdoug.dependency_walker import DependencyWalker
from libdoug.optimistic_solver import OptimisticConflictSolver
from libdoug.graph import DependencyType
from libdoug.values import EmptyDiff, RootImage
from libdoug.utils import Console, get_image, wipe_newlines
from libdoug.api.flags import parse_cli
from libdoug.http import HTTPRequest
from libdoug.decorators import http_request_decorate, RequestTokenDecorator

docker, registry, user = DockerLocal(), None, None

def dumplocal_action(args):
	print "Local tags:"
	local = docker.getimages(args.repo)
	localhistory = ImageHistory(local)
	localhistory.printout()

def dumpremote_action(args):
	print "Remote tags:"
	remotehistory = ImageHistory.fromjson(registry.querytags(args.repo, user))
	remotehistory.printout()

def dependencies_action(args):
	print "Dependency Walker:"
	allimages = docker.getallimages()
	image = get_image(args.image, allimages)

	walker = DependencyWalker(image, DependencyType.IMAGE)
	walker.walk(docker.getallimages())

def update_action(args):
	localhistory = ImageHistory(docker.getimages(args.repo))
	remotehistory = ImageHistory.fromjson(registry.querytags(args.repo, user))
	solver = args.solver

	if solver == 'optimistic':
		differ = HistoryDiff(localhistory, remotehistory)
		imgdelta = differ.diff()
		if imgdelta != EmptyDiff:
			print 'Local and Remote Diffs:'
			HistoryDiff.printout(imgdelta)

			if raw_input("Resolve conflicts [y/n]? [y] ") in ['', 'y', 'Y'] or args.force:
				conflict = OptimisticConflictSolver(docker.getallimages(), imgdelta, args.repo)
				resolve = conflict.solve()
				if resolve:
					print 'Resolutions: '
					for r in resolve:
						if not args.no_push or r.gettype() != ResolutionType.PUSH:
							r.execute(docker)
		else:
			print 'Local and Remote are up to date!'
	elif solver == 'vr':
		print "VR Conflict Status:"
		nevsolver = VRConflictSolver(docker.getallimages(), (localhistory, remotehistory), args.repo)
		nevsolver.solve()
	else:
		raise Exception('Unsupported solver: %s' % solver)

def dockercli_action(args):
	if len(args.cli) == 1:
		args.cli = shlex.split(args.cli[0])
	if args.cli[0] == 'docker':
		args.cli = args.cli[1:]
	cli = parse_cli(args.cli)
	print 'Flags:   ', "\n	  ".join(["%s = %s"%a for a in cli.flags])
	print 'Verb:    ', cli.verb
	print 'Context: ', cli.context
	print 'Workdir: ', os.getcwd()


def _get_filetype(path):
	return os.popen2('file ' + path)[1].readline()

def squash_images(chain, repo, tag):
	os.mkdir('_staged')
	print ''
	print '        Layers are being squashed.'
	for img in chain:
		path = '_staged/'+img['id']
		filepath = path + '/layer.tar'
		os.mkdir(path)

		ftype = _get_filetype(img['id'])
		if 'tar' in ftype:
			shutil.copyfile(img['id'], filepath)
		elif 'gzip' in ftype:
			with open(filepath, 'a') as f:
				subprocess.call(['gzip',  '-cd', img['id']], stdout=f)
		else:
			raise Exception('Invalid filetype: ' + ftype)

		shutil.copyfile(img['id']+'.json', path+'/json')
		with open(path+'/VERSION', 'a') as f:
			f.write('1.0')

	if repo and tag:
		with open('_staged/repositories', 'a') as f:
			json.dump({repo: {tag: chain[0]['id']}}, f)

	F_NULL = open(os.devnull, 'w')
	tar = subprocess.Popen(['tar', '-cf', 'image.tar', '.'], stderr=F_NULL,  cwd='_staged')
	if tar.wait() == 0:
		shutil.copyfile('_staged/image.tar', 'image.tar')
		print ''
		print 'DONE!'
		try:
			shutil.rmtree('_staged')
			for img in chain:
				os.remove(img['id'])
				os.remove(img['id']+'.json')
		except:
			print 'Cleanup failed ...'
	else:
		print 'Bad return code from Tar:', tar.returncode


def pullid_action(args):
	repo = args.repo if args.repo else 'library/scratch'
	md = registry.pullmetadata(args.id, repo, user)
	if not md:
		raise Exception('Couldn\'t get metadata')

	chain = [md]
	while 'parent' in md:
		md = registry.pullmetadata(md['parent'], repo, user)
		chain.append(md)

	print 'Layers:', '\n        '.join([i['id']+' = '+(str(i['Size']) if 'Size' in i else '0')+'B' for i in chain])

	print ''
	print '-' * Console.width()
	print ''

	for img in chain:
		img_id = img['id']
		filename = img_id + '.json'
		with open(filename, 'a') as f:
			json.dump(img, f) 
			print '       ', filename, ' [SAVED]'
		registry.pulldata(img_id, repo, user)

	r, t = None, None
	if args.tag.find(':') != -1:
		r, t = args.tag.split(':', 1)
	squash_images(chain, r, t)

def cli_command(args):
	action = args.action.replace('-', '')
	actionfunc = globals()[action+'_action']
	actionfunc(args)

if __name__ == '__main__':
	args = argparse.ArgumentParser(description='doug-cli libdoug interface')
	args.add_argument('-f', '--force', action='store_true', help='Do not ask for confirmations')
	args.add_argument('-u', '--user', help='Username for the Hub')
	args.add_argument('-p', '--password', help='Password for the Hub')
	args.add_argument('-e', '--email', help='Email for the Hub')
	args.add_argument('-r', '--registry', help='Registry URL we target', default='docker.io')
	args.add_argument('-a', '--baseauth', help='HTTP Basic Auth string')
	args.add_argument('-n', '--no-push', action='store_true', help='Do not push local changes upstream')
	subargs = args.add_subparsers(help='sub-command help', dest='action')

	localparser = subargs.add_parser('dump-local', help='Dump locally present tags')
	localparser.add_argument('repo', help='Target repository')

	remoteparser = subargs.add_parser('dump-remote', help='Dump remotely present tags')
	remoteparser.add_argument('repo', help='Target repository')

	cliparser = subargs.add_parser('docker-cli', help='Parse Dockers CLI')
	cliparser.add_argument('cli', nargs='*', help='Docker command')
	
	depparser = subargs.add_parser('dependencies', help='Visualize dependencies of target Image')
	depparser.add_argument('image', help='Target image ID or Repo[:Tag]')

	pullidparser = subargs.add_parser('pullid', help='Pull image from registry by Image ID')
	pullidparser.add_argument('-t', '--tag', help='Full repo/name:tag', default='')
	pullidparser.add_argument('-r', '--repo', help='Repository from which we\'re pulling', default='')
	pullidparser.add_argument('id', help='Image ID')

	updateparser = subargs.add_parser('update', help='Update Local/Remote tags')
	updateparser.add_argument('-s', '--solver', help='Solver to use (vr = Version-Release)', default='optimistic', choices=['optimistic', 'vr'])
	updateparser.add_argument('repo', help='Target repository')

	parsed = args.parse_args()
	if hasattr(parsed, 'repo'):
		if parsed.repo.count('/') == 0 and parsed.repo != '':
			parsed.repo = "stackbrew/" + parsed.repo
	registry = Registry(parsed.registry)

	if parsed.action in ['update', 'dump-remote', 'pullid']:
		if parsed.user == None:
			parsed.user, parsed.password, parsed.email = wipe_newlines(open(os.getenv("HOME") + '/.douguserinfo').readline().split(':'))
	user = UserInfo(parsed.user, parsed.password, parsed.email)

	cli_command(parsed)

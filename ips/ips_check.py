#!/usr/bin/env python
# $Id$

import getopt
import glob
import os
import re
import sha
import stat
import sys

def main():
	v_dir = ''
	v_delete = False

	try:
		opts, args = getopt.getopt(sys.argv[1:], 
			"hd:D",
			['help', 'dir=', 'delete'])
	except getopt.GetoptError, err:
		print err
		sys.exit(-1)

	for name, value in opts:
		if name in ('-h', '--help'):
			usage()
			sys.exit(-1)
		elif name in ('-d', '--dir'):
			v_dir = value
		elif name in ('-D', '--delete'):
			v_delete = True
		else:
			print "ERROR: invalid argument ", name
			sys.exit(-1)

	if v_dir == '':
		print "ERROR: needs --dir=repo_directory"
		sys.exit(-1)
 	if not os.path.isdir(v_dir):
		print "ERROR: %s is not a directory" % v_dir
		sys.exit(-1)

	check(v_dir, v_delete)	

def check(v_dir, v_delete):
	re_hash_csize = re.compile("^(file|license) ([^ ]+) chash=([^ ]+) .* pkg.csize=(\d+)")

	file_info_list = []
	count = 0
	for dir in os.listdir(v_dir + os.sep + 'pkg'):
		if not os.path.isdir('pkg' + os.sep + dir):
			continue

		for file in os.listdir('pkg' + os.sep + dir):
			filepath = 'pkg' + os.sep + dir + os.sep + file;
			#print filepath
			f = open(filepath, 'r')
			for line in f.readlines():
				line = line.strip()
				#print line
				result = re_hash_csize.search(line)
				if result:
					result.groups()
					file_info_list.append( (result.group(2), result.group(3), result.group(4) ) )
			count += 1	
	print "# INFO : found %d packages" % count
	print "# INFO : found %d files" % len(file_info_list) 

	count = 0
	for file_info in file_info_list:
		#print file_info
		file_hash = file_info[0]
		file_chash = file_info[1]
		file_size = int(file_info[2])

		filepath = 'file' + os.sep + file_hash[:2] + os.sep + file_hash[2:8] + os.sep + file_hash
		error = False
		if os.path.exists(filepath):
			# print file_info
			st = os.stat(filepath)
			if (st[stat.ST_SIZE] == file_size):
				sha1 = sha.new()
				sha1.update(open(filepath).read())
				if (sha1.hexdigest() != file_chash): 
					print "KO hash (found=%s != expected=%s ) file_hash=%s %s" % (sha1.hexdigest(), file_chash, file_hash, filepath)	
					error = True
			else:
				print "KO size (found=%d expected=%d) %s " % (st[stat.ST_SIZE], file_size, filepath)
				error = True
		if error:
			os.unlink(filepath)

if __name__ == '__main__':
	main()

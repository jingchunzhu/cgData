#!/usr/bin/env python

import MySQLdb
import _mysql_exceptions
import sys
import json
import csv
import re
import os
serverList = json.loads( open( sys.argv[1] ).read() )

reCommaEnd = re.compile(r',$')


for server in serverList:
	outDir = "data/%s/probes" % (server)
	if not os.path.exists( outDir ):
		os.makedirs( outDir )

	info = serverList[server]
	try:
		db=MySQLdb.connect(host=info['host'],db=info['db'], passwd=info['passwd'], user=info['user'])
		cur = db.cursor()	
		cur.execute("select name, wrangler, patDb, platform, aliasTable, profile from raDb")	
		for row in cur.fetchall():
			name = row[0]
			aliasTable = row[4]
			print name
			gData = {
				'type': 'probeMap',
				'name' : row[0],
				'author' : row[1],
				'probeSpace' : row[4]
			}
			oHandle = open( "%s/%s.json" % (outDir, name), "w" )
			oHandle.write( json.dumps( gData ) )
			oHandle.close()			
		
			profile = row[5]
			if serverList.has_key( profile ):				
				oHandle = open( "%s/%s" % (outDir, name), "w" )
				pHost = serverList[ profile ]
				try:
					db2 = MySQLdb.connect(host=pHost['host'],db=pHost['db'], passwd=pHost['passwd'], user=pHost['user'])
					cur2 = db2.cursor()				
					cur2.execute( "select name, chrom, chromStart, chromEnd, strand from %s" % ( name ) )
					cur3 = db2.cursor()					
					for row2 in cur2.fetchall():
						probeName = row2[0]
						chrom = row2[1]
						chromStart = row2[2]
						chromEnd = row2[3]
						strand = row2[4]							
						aliases = []
						if aliasTable is not None:
							try:
								aliasSQL =  "select alias from %s where name='%s'" % ( aliasTable, probeName ) 
								#print aliasSQL
								cur3.execute( aliasSQL )
								for row3 in cur3.fetchall():
									aliases.append( row3[0] )
							except _mysql_exceptions.ProgrammingError, e:
								print "ERROR:", e					
					
						oHandle.write("%s\t%s\t%s\t%s\t%s\t%s\n" % ( probeName, chrom, chromStart, chromEnd, strand, ",".join( aliases ) ) )
					
					cur2.close()
					cur3.close()
					db2.close()
				except _mysql_exceptions.ProgrammingError, e:
					print "ERROR:", e
			
				oHandle.close()
			
	except _mysql_exceptions.ProgrammingError:
		pass

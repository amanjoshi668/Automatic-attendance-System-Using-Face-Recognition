import sqlite3
def add(Id,Name,file):
	conn = sqlite3.connect('student.db')
	name = ""
	for x in file:
		name = name + ","+str(x)

	conn.execute("insert into details(id,name,file1,file2,file3,file4,file5,file6,file7,file8,file9,file10,file11,file12,file13,file14,file15,file16,file17,file18,file19,file20)\
		values(%d,%s%s)" %(int(Id),Name,name))
	conn.commit()
	conn.close()
	return
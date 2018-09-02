import find_faces
import sqlite3
import json
from sklearn import svm
from sklearn.externals import joblib
from sklearn.ensemble import RandomForestClassifier

def fun():
	id_to_int={}
	int_to_id = {}
	count = 0
	path = "Faces/"
	json_file = "Data/dictionary.json"
	json_rev_file = "Data/dictionary_reverse.json"
	model_name = 'models/trained_model.pkl'
	known_face_encodings = []
	result = []

	conn = sqlite3.connect('student.db')
	cursor = conn.execute("select * from details")

	for row in cursor:
		id_to_int[count] = row[0]
		int_to_id[row[0]] = count
		for i in range(2,len(row)):
			image = find_faces.load_image_file(str(path+str(row[i])))
			face = find_faces.face_encodings(image,num_jitters=5)
			if len(face)>0:
				face_encoding = face[0]
				known_face_encodings.append(face_encoding)
				result.append(count)
		count = count+1
		print(len(row))
	print(count)
	clf = RandomForestClassifier(n_jobs=-1)
	clf.fit(known_face_encodings,result)
	joblib.dump(clf,model_name)
	with open(json_file, 'w') as outfile:
			json.dump(id_to_int, outfile)
	with open(json_rev_file, 'w') as outfile:
			json.dump(int_to_id, outfile)
fun()

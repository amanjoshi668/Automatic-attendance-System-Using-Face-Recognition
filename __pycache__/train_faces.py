import face_recognition
import cv2
import sys
import sqlite3
import csv
import json
import pandas as pd 
from keras.layers import Dense, Conv2D, MaxPooling2D, Dropout, Flatten
from keras.models import Sequential
from keras.layers import Activation
from keras.optimizers import SGD
from keras.utils import np_utils
from keras.models import load_model
import keras.backend as K

def path(filename):
	return "Faces/"+filename

def start_training():
	conn = sqlite3.connect('student.db')
	cursor = conn.execute("select * from details")
	data = []
	labels = []
	with open('Data/dictionary.json') as data_file:
		convert = json.load(data_file)
	classes = 0

	for row in cursor:
		for (i,x) in enumerate(row):
			if i<2:
				continue
			labels.append(int(convert[str(row[0])]))
			image = face_recognition.load_image_file(path(x))
			data.append(face_recognition.face_encodings(image)[0])
	classes = classes+1

	data = np.array(data)
	labels = np_utils.to_categorical(labels, len(set(labels))) 

	model = Sequential()
	model.add(Dense(int(128), input_dim=128, init="uniform", activation="relu"))
	model.add(Dense(int(110), init="uniform", activation="relu"))
	model.add(Dense(int(100), init="uniform", activation="relu"))
	model.add(Dense(int(90),init="uniform", activation="relu"))
	model.add(Dense(int(classes),init="uniform", activation="relu"))
	model.add(Activation("softmax"))
	sgd = SGD(lr=0.001, decay=1e-7, momentum=.9)
	model.compile(loss="categorical_crossentropy", optimizer=sgd, metrics=["accuracy"])
	model.fit(data,labels,nb_epoch=60)
	model.save('model.hd5')

if __name__ == '__main__':
	start_training()

conn = sqlite3.connect('student.db')
cursor = conn.execute("select * from details")
data = []
labels = []
with open('Data/dictionary.json') as data_file:
	convert = json.load(data_file)
classes = 0
for row in cursor:
	for (i,x) in enumerate(row):
		if i<2:
			continue
		labels.append(int(convert[str(row[0])]))
		image = face_recognition.load_image_file(path(x))
		data.append(face_recognition.face_rencodings(image)[0])
	classes = classes+1
data = np.array(data)
labels = np_utils.to_categorical(labels, len(set(labels))) 
model = Sequential()
model.add(Dense(int(128), input_dim=128, init="uniform", activation="relu"))
model.add(Dense(int(110), init="uniform", activation="relu"))
model.add(Dense(int(100), init="uniform", activation="relu"))
model.add(Dense(int(90),init="uniform", activation="relu"))
model.add(Dense(int(classes),init="uniform", activation="relu"))
model.add(Activation("softmax"))
sgd = SGD(lr=0.001, decay=1e-7, momentum=.9)
model.compile(loss="categorical_crossentropy", optimizer=sgd, metrics=["accuracy"])
model.fit(data,labels,nb_epoch=60)
model.save('model.hd5')
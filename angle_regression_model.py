from keras.preprocessing.image import ImageDataGenerator
import keras.applications as  keras_applications
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import numpy as np
from sklearn.metrics import classification_report, confusion_matrix
import pandas as pd
import sys
from timeit import default_timer as timer
from keras import backend as K
from keras.callbacks import CSVLogger
import json
from keras.callbacks import ModelCheckpoint

from keras.optimizers import RMSprop, Adam, Adadelta
from keras.layers.convolutional import Convolution2D
from keras.models import Sequential
from keras.layers.core import Dense, Dropout, Activation, Flatten
from sklearn.model_selection import train_test_split 
import os

from keras.utils import plot_model
from keras import optimizers

def create_model():
    nb_filters = 8
    nb_conv = 5
    image_size=200
    model = Sequential()
    model.add(Convolution2D(nb_filters, nb_conv, nb_conv,
                            border_mode='valid',
                            input_shape=( image_size, image_size,1) ) )
    model.add(Activation('relu'))

    model.add(Convolution2D(nb_filters, nb_conv, nb_conv))
    model.add(Activation('relu'))

    model.add(Convolution2D(nb_filters, nb_conv, nb_conv))
    model.add(Activation('relu'))

    model.add(Convolution2D(nb_filters, nb_conv, nb_conv))
    model.add(Activation('relu'))
    model.add(Dropout(0.25))

    model.add(Convolution2D(nb_filters*2, nb_conv, nb_conv))
    model.add(Activation('relu'))

    model.add(Convolution2D(nb_filters*2, nb_conv, nb_conv))
    model.add(Activation('relu'))

    model.add(Convolution2D(nb_filters*2, nb_conv, nb_conv))
    model.add(Activation('relu'))
    
    model.add(Convolution2D(nb_filters*2, nb_conv, nb_conv))
    model.add(Activation('relu'))
    model.add(Dropout(0.5))
    model.add(Flatten())
    model.add(Dense(256))
    model.add(Activation('relu'))
    model.add(Dropout(0.5))
    model.add(Dense(128))
    model.add(Activation('relu'))
    model.add(Dropout(0.5))
    model.add(Dense(1))
    model.add(Activation('linear'))
    sgd = optimizers.SGD(lr=0.01, decay=1e-6, momentum=0.9, nesterov=True)

    #model.compile(loss='mean_squared_error', optimizer=Adadelta(),  metrics=['mean_squared_error'])
    model.compile(loss='mean_squared_error', optimizer=sgd,  metrics=['mean_squared_error'])
    return model



start=timer()
input_shape=(200,200,1)
 

#i=int(sys.argv[1])-1
#classes=int(sys.argv[2])

rootoutput='outputs/'
rootdataset='dataset/' 

expprefix="customeregression1"
datapath="rotationtraindata"
#classes_name=["nonsym","H"]
normalizefactor=1 # or 90

 
timerfile= rootoutput+ expprefix+'/timer.csv'
outdir=rootoutput + expprefix+"/output/"
checkpoint_dir = rootoutput+ expprefix+ "/models/"
validation_data_dir = rootdataset+ datapath+'/valid'
train_path = rootdataset+datapath+'/'
test_path = rootdataset+datapath+'/test'


if not os.path.exists(outdir):
    os.makedirs(outdir)
if not os.path.exists(checkpoint_dir):
    os.makedirs(checkpoint_dir)




img_width, img_height = 200, 200
train_data_dir = train_path

nb_train_samples = 12000#14000
nb_validation_samples = 1600
epochs = 20
batch_size = 16


def recall_m(y_true, y_pred):
        true_positives = K.sum(K.round(K.clip(y_true * y_pred, 0, 1)))
        possible_positives = K.sum(K.round(K.clip(y_true, 0, 1)))
        recall = true_positives / (possible_positives + K.epsilon())
        return recall

def precision_m(y_true, y_pred):
        true_positives = K.sum(K.round(K.clip(y_true * y_pred, 0, 1)))
        predicted_positives = K.sum(K.round(K.clip(y_pred, 0, 1)))
        precision = true_positives / (predicted_positives + K.epsilon())
        return precision

def f1_m(y_true, y_pred):
    precision = precision_m(y_true, y_pred)
    recall = recall_m(y_true, y_pred)
    return 2*((precision*recall)/(precision+recall+K.epsilon()))


 

modelname= expprefix
model=create_model()
csv_logger = CSVLogger(outdir+ modelname+ 'log.csv', append=True, separator=';')

checkpoint = ModelCheckpoint(checkpoint_dir+modelname+"_checkpoint.best.hdf5", monitor='val_mean_squared_error', verbose=1, save_best_only=True, mode='min')

model.compile(loss='mean_squared_error', optimizer=Adadelta(),  metrics=['mean_squared_error'])
 
#model.compile(optimizer='adam', loss='categorical_crossentropy', metrics=['accuracy',f1_m,precision_m, recall_m])
model.summary()

#plot_model(model, to_file='model.png')
#exit()

train_datagen = ImageDataGenerator(rescale = 1. / 255)
test_datagen = ImageDataGenerator(rescale = 1. / 255)

#train_generator = train_datagen.flow_from_directory(train_data_dir,  classes= classes_name,   target_size =(img_width, img_height), batch_size = batch_size, class_mode='categorical',color_mode="grayscale")
train_generator = train_datagen.flow_from_directory(train_path,  classes= [""],   target_size =(img_width, img_height), batch_size = 10000, class_mode='sparse',color_mode="grayscale")
X,_=train_generator.next()
y=[int(f.split("-")[5].replace(".png",""))/normalizefactor for f in train_generator.filenames]

cv_size = 2000
X_train, X_valid, y_train, y_valid = train_test_split(X, y, test_size=cv_size, random_state=56741)
print("X_train=",len(X_train))

#validation_generator = test_datagen.flow_from_directory(    validation_data_dir,   classes= classes_name, target_size =(img_width, img_height),          batch_size = batch_size,  class_mode='categorical',color_mode="grayscale")
model.fit(X, y, batch_size=batch_size, nb_epoch=epochs, verbose=1, validation_data=(X_valid, y_valid),  callbacks=[csv_logger,checkpoint] )


model.save_weights(checkpoint_dir+modelname+'_model_saved_weight.h5')


#model.fit_generator(train_generator, verbose=1, steps_per_epoch = nb_train_samples // batch_size, epochs = epochs, validation_data = validation_generator, validation_steps = nb_validation_samples // batch_size, callbacks=[csv_logger,checkpoint])
#model.save_weights(checkpoint_dir+modelname+'_model_saved_weight.h5')



history=model.history
with open( outdir+ "/history_" + modelname+ '.json', 'w') as f:
    json.dump(history.history, f)

'''
steps =  np.ceil(validation_generator.samples/batch_size)

Y_pred = model.predict_generator(validation_generator, steps=steps)
y_pred = np.argmax(Y_pred, axis=1)
#print('Confusion Matrix')
target_names = [k for k in validation_generator.class_indices]
#print(target_names)
cm=confusion_matrix(validation_generator.classes, y_pred)



np.savetxt(outdir+ "/conf_" + modelname+".csv", cm, fmt="%d", delimiter=",")

f=open(outdir+ "/conf_" + modelname+".csv", "a")
txt=  str(target_names).replace("[","").replace("]","")
with open(outdir+ "/conf_" + modelname+".csv", 'r') as original: data = original.read()
with open(outdir+ "/conf_" + modelname+".csv", 'w') as modified: modified.write(txt + "\n" + data)
'''
with open( timerfile, 'a+') as modified: modified.write(modelname + ", " +  str( round( (timer()- start) /(60*60) ,2)) + "\n")





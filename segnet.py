#coding=utf-8
import numpy as np  
from keras.models import Sequential  
from keras.layers import Conv2D,MaxPooling2D,UpSampling2D,BatchNormalization,Reshape,Permute,Activation  
from keras.utils.np_utils import to_categorical  
from keras.preprocessing.image import img_to_array  
from keras.callbacks import ModelCheckpoint  
from sklearn.preprocessing import LabelEncoder  
from PIL import Image  
import matplotlib.pyplot as plt  
import cv2
import random
import os
from tqdm import tqdm  
os.environ["CUDA_VISIBLE_DEVICES"] = "7"
seed = 7  
np.random.seed(seed)  
  
#data_shape = 360*480  
img_w = 256  
img_h = 256  
#有一个为背景  
n_label = 4+1  
  
classes = [0. ,  1.,  2.,   3.  , 4.]  
  
labelencoder = LabelEncoder()  
labelencoder.fit(classes)  

image_sets = ['1.png','2.png','3.png']

def creat_dataset(image_num = 900):
    print('creating dataset...')
    image_each = image_num / len(image_sets)
    g_count = 0
    for i in range(len(image_sets)):
        count = 0
        src_img = cv2.imread('./data/src/' + image_sets[i])  # 3 channels
        label_img = cv2.imread('./data/label/' + image_sets[i],cv2.IMREAD_GRAYSCALE)  # single channel
        X_height,X_width,_ = src_img.shape
        while count < image_each:
            random_width = random.randint(0, X_width - img_w - 1)
            random_height = random.randint(0, X_height - img_h - 1)
            src_roi = src_img[random_height: random_height + img_h, random_width: random_width + img_w,:]
            label_roi = label_img[random_height: random_height + img_h, random_width: random_width + img_w,:]
            cv2.imwrite(('./train/src/%d.png',g_count),src_roi)
            cv2.imwrite(('./train/label/%d.png',g_count),label_roi)
            count += 1 
            g_count += 1
        
    
  
#原keras中的load_img只读取两种格式，gray和RGB，其他类型的图像都会转为RBG进行读取，本处对此进行更改，保留原图格式  
def load_img(path, grayscale=False, target_size=None):  
    img = Image.open(path)  
    if grayscale:  
        if img.mode != 'L':  
            img = img.convert('L')  
    if target_size:  
        wh_tuple = (target_size[1], target_size[0])  
        if img.size != wh_tuple:  
            img = img.resize(wh_tuple)  
    return img  

'''    
train_url = open(r'./train/train.txt','r').readlines()  
#trainval_url = open(r'/media/wmy/document/BigData/VOCdevkit/VOC2012/ImageSets/Segmentation/trainval.txt','r').readlines()  
val_url = open(r'./train/val.txt','r').readlines()  
train_numb = len(train_url)  
valid_numb = len(val_url)  
print ("the number of train data is",train_numb)  
print ("the number of val data is",valid_numb)
'''
filepath ='./train/'  

def get_train_val(val_rate = 0.25):
    train_url = []    
    train_set = []
    val_set  = []
    for pic in os.listdir('./train/src'):
        train_url.append(pic)
    random.shuffle(train_url)
    total_num = len(train_url)
    val_num = int(val_rate * total_num)
    for i in range(len(train_url)):
        if i < val_num:
            val_set.append(train_url[i]) 
        else:
            train_set.append(train_url[i])
    return train_set,val_set

# data for training  
def generateData(batch_size,data=[]):  
    print 'generateData...'
    while True:  
        train_data = []  
        train_label = []  
        batch = 0  
        for i in (range(len(data))): 
            url = data[i]
            batch += 1 
            #print (filepath + 'src/' + url)
            img = load_img(filepath + 'src/' + url, target_size=(img_w, img_h))  
            img = img_to_array(img) 
            # print img
            # print img.shape  
            train_data.append(img)  
            label = load_img(filepath + 'label/' + url, target_size=(img_w, img_h),grayscale=True)  
            label = img_to_array(label).reshape((img_w * img_h,))  
            # print label.shape  
            train_label.append(label)  
            if batch % batch_size==0: 
                #print 'get enough bacth!\n'
                train_data = np.array(train_data)  
                train_label = np.array(train_label).flatten()  
                train_label = labelencoder.transform(train_label)  
                train_label = to_categorical(train_label, num_classes=n_label)  
                train_label = train_label.reshape((batch_size,img_w * img_h,n_label))  
                yield (train_data,train_label)  
                train_data = []  
                train_label = []  
                batch = 0  
 
# data for validation 
def generateValidData(batch_size,data=[]):  
    print 'generateValidData...'
    while True:  
        valid_data = []  
        valid_label = []  
        batch = 0  
        for i in (range(len(data))):  
            url = data[i]
            batch += 1  
            img = load_img(filepath + 'src/' + url, target_size=(img_w, img_h)) 
            print img
            #print (filepath + 'src/' + url)
            img = img_to_array(img)  
            # print img.shape  
            valid_data.append(img)  
            label = load_img(filepath + 'label/' + url, target_size=(img_w, img_h),grayscale=True)  
            label = img_to_array(label).reshape((img_w * img_h,))  
            # print label.shape  
            valid_label.append(label)  
            if batch % batch_size==0:  
                valid_data = np.array(valid_data)  
                valid_label = np.array(valid_label).flatten()  
                valid_label = labelencoder.transform(valid_label)  
                valid_label = to_categorical(valid_label, num_classes=n_label)  
                valid_label = valid_label.reshape((batch_size,img_w * img_h,n_label))  
                yield (valid_data,valid_label)  
                valid_data = []  
                valid_label = []  
                batch = 0  
  
def SegNet():  
    model = Sequential()  
    #encoder  
    model.add(Conv2D(64,(3,3),strides=(1,1),input_shape=(3,img_w,img_h),padding='same',activation='relu'))  
    model.add(BatchNormalization())  
    model.add(Conv2D(64,(3,3),strides=(1,1),padding='same',activation='relu'))  
    model.add(BatchNormalization())  
    model.add(MaxPooling2D(pool_size=(2,2)))  
    #(128,128)  
    model.add(Conv2D(128, (3, 3), strides=(1, 1), padding='same', activation='relu'))  
    model.add(BatchNormalization())  
    model.add(Conv2D(128, (3, 3), strides=(1, 1), padding='same', activation='relu'))  
    model.add(BatchNormalization())  
    model.add(MaxPooling2D(pool_size=(2, 2)))  
    #(64,64)  
    model.add(Conv2D(256, (3, 3), strides=(1, 1), padding='same', activation='relu'))  
    model.add(BatchNormalization())  
    model.add(Conv2D(256, (3, 3), strides=(1, 1), padding='same', activation='relu'))  
    model.add(BatchNormalization())  
    model.add(Conv2D(256, (3, 3), strides=(1, 1), padding='same', activation='relu'))  
    model.add(BatchNormalization())  
    model.add(MaxPooling2D(pool_size=(2, 2)))  
    #(32,32)  
    model.add(Conv2D(512, (3, 3), strides=(1, 1), padding='same', activation='relu'))  
    model.add(BatchNormalization())  
    model.add(Conv2D(512, (3, 3), strides=(1, 1), padding='same', activation='relu'))  
    model.add(BatchNormalization())  
    model.add(Conv2D(512, (3, 3), strides=(1, 1), padding='same', activation='relu'))  
    model.add(BatchNormalization())  
    model.add(MaxPooling2D(pool_size=(2, 2)))  
    #(16,16)  
    model.add(Conv2D(512, (3, 3), strides=(1, 1), padding='same', activation='relu'))  
    model.add(BatchNormalization())  
    model.add(Conv2D(512, (3, 3), strides=(1, 1), padding='same', activation='relu'))  
    model.add(BatchNormalization())  
    model.add(Conv2D(512, (3, 3), strides=(1, 1), padding='same', activation='relu'))  
    model.add(BatchNormalization())  
    model.add(MaxPooling2D(pool_size=(2, 2)))  
    #(8,8)  
    #decoder  
    model.add(UpSampling2D(size=(2,2)))  
    #(16,16)  
    model.add(Conv2D(512, (3, 3), strides=(1, 1), padding='same', activation='relu'))  
    model.add(BatchNormalization())  
    model.add(Conv2D(512, (3, 3), strides=(1, 1), padding='same', activation='relu'))  
    model.add(BatchNormalization())  
    model.add(Conv2D(512, (3, 3), strides=(1, 1), padding='same', activation='relu'))  
    model.add(BatchNormalization())  
    model.add(UpSampling2D(size=(2, 2)))  
    #(32,32)  
    model.add(Conv2D(512, (3, 3), strides=(1, 1), padding='same', activation='relu'))  
    model.add(BatchNormalization())  
    model.add(Conv2D(512, (3, 3), strides=(1, 1), padding='same', activation='relu'))  
    model.add(BatchNormalization())  
    model.add(Conv2D(512, (3, 3), strides=(1, 1), padding='same', activation='relu'))  
    model.add(BatchNormalization())  
    model.add(UpSampling2D(size=(2, 2)))  
    #(64,64)  
    model.add(Conv2D(256, (3, 3), strides=(1, 1), padding='same', activation='relu'))  
    model.add(BatchNormalization())  
    model.add(Conv2D(256, (3, 3), strides=(1, 1), padding='same', activation='relu'))  
    model.add(BatchNormalization())  
    model.add(Conv2D(256, (3, 3), strides=(1, 1), padding='same', activation='relu'))  
    model.add(BatchNormalization())  
    model.add(UpSampling2D(size=(2, 2)))  
    #(128,128)  
    model.add(Conv2D(128, (3, 3), strides=(1, 1), padding='same', activation='relu'))  
    model.add(BatchNormalization())  
    model.add(Conv2D(128, (3, 3), strides=(1, 1), padding='same', activation='relu'))  
    model.add(BatchNormalization())  
    model.add(UpSampling2D(size=(2, 2)))  
    #(256,256)  
    model.add(Conv2D(64, (3, 3), strides=(1, 1), input_shape=(3,img_w, img_h), padding='same', activation='relu'))  
    model.add(BatchNormalization())  
    model.add(Conv2D(64, (3, 3), strides=(1, 1), padding='same', activation='relu'))  
    model.add(BatchNormalization())  
    model.add(Conv2D(n_label, (1, 1), strides=(1, 1), padding='same'))  
    model.add(Reshape((n_label,img_w*img_h)))  
    #axis=1和axis=2互换位置，等同于np.swapaxes(layer,1,2)  
    model.add(Permute((2,1)))  
    model.add(Activation('softmax'))  
    model.compile(loss='categorical_crossentropy',optimizer='sgd',metrics=['accuracy'])  
    model.summary()  
    return model  
  
  
def train():  
    model = SegNet()  
    modelcheck = ModelCheckpoint('Segnet_params_1.h5',monitor='val_acc',save_best_only=True,mode='max')  
    callable = [modelcheck]  
    train_set,val_set = get_train_val()
    train_numb = len(train_set)  
    valid_numb = len(val_set)  
    print ("the number of train data is",train_numb)  
    print ("the number of val data is",valid_numb)
    model.fit_generator(generator=generateData(16,train_set),steps_per_epoch=train_numb,epochs=10,verbose=1,  
                    validation_data=generateValidData(16,val_set),validation_steps=valid_numb,callbacks=callable,max_q_size=1)  
  
def predict():  
    model = SegNet()  
    model.load_weights('Segnet_params_1.h5')  
    while True:  
        print ("please input the test img path:" )
        test_imgpath = raw_input()  
        img = load_img(test_imgpath, target_size=(img_w, img_h))  
        #img = img_to_array(img).reshape((1, img_h, img_w, -1))  
        img = img_to_array(img).reshape((1, -1,img_h, img_w))
        pred = model.predict_classes(img,verbose=2)  
        pred = labelencoder.inverse_transform(pred[0])  
        print (np.unique(pred))  
        pred = pred.reshape((img_h,img_w)).astype(np.uint8)  
        pred_img = Image.fromarray(pred)  
        pred_img.save('1.png',format='png')  
        ''''' 
        print pred 
        plt.subplot(2,1,1) 
        plt.imshow(img.reshape((img_h,img_w,3)).astype(np.uint8)) 
        plt.subplot(2,1,2) 
        plt.imshow(pred) 
        plt.show() 
        '''  
  
if __name__=='__main__':  
    #creat_dataset()
    #train()  
    predict()  
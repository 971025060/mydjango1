import os
import math
import random
import glob

import cv2
import numpy as np
import tensorflow as tf

slim = tf.contrib.slim
import matplotlib.pyplot as plt
import matplotlib.image as mpimg
import sys
from app01 import recongnite
sys.path.append('../')
from app01.nets import ssd_vgg_300, ssd_common, np_methods
from app01.preprocessing import ssd_vgg_preprocessing
from app01.notebooks import visualization

# TensorFlow session: grow memory when needed. TF, DO NOT USE ALL MY GPU MEMORY!!!
gpu_options = tf.GPUOptions(allow_growth=True)
config = tf.ConfigProto(log_device_placement=False, gpu_options=gpu_options)
isess = tf.InteractiveSession(config=config)
# Input placeholder.
net_shape = (300, 300)
data_format = 'NHWC'
img_input = tf.placeholder(tf.uint8, shape=(None, None, 3))
# Evaluation pre-processing: resize to SSD net shape.
image_pre, labels_pre, bboxes_pre, bbox_img = ssd_vgg_preprocessing.preprocess_for_eval(
    img_input, None, None, net_shape, data_format, resize=ssd_vgg_preprocessing.Resize.WARP_RESIZE)
image_4d = tf.expand_dims(image_pre, 0)

# Define the SSD model.
reuse = True if 'ssd_net' in locals() else None
ssd_net = ssd_vgg_300.SSDNet()
with slim.arg_scope(ssd_net.arg_scope(data_format=data_format)):
    predictions, localisations, _, _ = ssd_net.net(image_4d, is_training=False, reuse=reuse)

# Restore SSD model.
ckpt_filename = '../checkpoints/ssd_300_vgg.ckpt'
# ckpt_filename = '../checkpoints/VGG_VOC0712_SSD_300x300_ft_iter_120000.ckpt'
isess.run(tf.global_variables_initializer())
saver = tf.train.Saver()
saver.restore(isess, ckpt_filename)

# SSD default anchor boxes.
ssd_anchors = ssd_net.anchors(net_shape)


# Main image processing routine.
def process_image(img, select_threshold=0.5, nms_threshold=.45, net_shape=(300, 300)):
    # Run SSD network.
    rimg, rpredictions, rlocalisations, rbbox_img = isess.run([image_4d, predictions, localisations, bbox_img],
                                                              feed_dict={img_input: img})

    # Get classes and bboxes from the net outputs.
    rclasses, rscores, rbboxes = np_methods.ssd_bboxes_select(
        rpredictions, rlocalisations, ssd_anchors,
        select_threshold=select_threshold, img_shape=net_shape, num_classes=21, decode=True)

    rbboxes = np_methods.bboxes_clip(rbbox_img, rbboxes)
    rclasses, rscores, rbboxes = np_methods.bboxes_sort(rclasses, rscores, rbboxes, top_k=400)
    rclasses, rscores, rbboxes = np_methods.bboxes_nms(rclasses, rscores, rbboxes, nms_threshold=nms_threshold)
    # Resize bboxes to original image shape. Note: useless for Resize.WARP!
    rbboxes = np_methods.bboxes_resize(rbbox_img, rbboxes)
    return rclasses, rscores, rbboxes
#摄像头截取图片
def cameraAutoForPictures(saveDir):
	'''
    调用电脑摄像头来自动获取图片
    '''
	if not os.path.exists(saveDir):
		os.makedirs(saveDir)
	count = 1  # 图片计数索引
	cap = cv2.VideoCapture(0)

	width, height, w = 640, 480, 360
	cap.set(cv2.CAP_PROP_FRAME_WIDTH, width)
	cap.set(cv2.CAP_PROP_FRAME_HEIGHT, height)
	crop_w_start = (width - w) // 2
	crop_h_start = (height - w) // 2
	print('-------------')
	print
	'width: ', width
	print
	'height: ', height
	while True:
		ret, frame = cap.read()  # 获取相框
		frame = frame[crop_h_start:crop_h_start + w, crop_w_start:crop_w_start + w]  # 展示相框
		frame = cv2.flip(frame, 1, dst=None)  # 前置摄像头获取的画面是非镜面的，即左手会出现在画面的右侧，此处使用flip进行水平镜像处理
		cv2.imshow("capture", frame)
		#print('input:')
		action = cv2.waitKey(1) & 0xFF
		if action == ord('p'):
			cv2.imwrite("%s/%d.jpg" % (saveDir, count), cv2.resize(frame, (224, 224), interpolation=cv2.INTER_AREA))
			print(u"%s: %d 张图片" % (saveDir, count))
			count += 1
		elif action == ord('q'):
			break
	cap.release()  # 释放摄像头
	cv2.destroyAllWindows()  # 丢弃窗口
# Test on some demo image and visualize output.
# 测试的文件夹
folder_path = 'D:\\Workspace\\demo\\'
# cameraAutoForPictures(folder_path)
path = 'D:\\Workspace\\demo\\'
paths = glob.glob(os.path.join(path, '*.jpg'))
image_names = sorted(os.listdir(path))
#image_names = paths.sort()
for path in paths:
    img = mpimg.imread(path)
# 文件夹中的第几张图，-1代表最后一张
#img = mpimg.imread(path + image_names[61])
    rclasses, rscores, rbboxes = process_image(img)
    recongnite.getClasses(rclasses)
    print("----类别为----:", rclasses)
# visualization.bboxes_draw_on_img(img, rclasses, rscores, rbboxes, visualization.colors_plasma)
    visualization.plt_bboxes(img, rclasses, rscores, rbboxes)

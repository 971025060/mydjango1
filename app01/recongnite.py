import os,cv2
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
# from .notebooks import test
import cv2
def getClasses(classes):
	print ('___class___',classes)
# if __name__ == '__main__':
	# saveDir = 'D:\\Workspace\\DjangoProject\\mydjango1\\app01\\media\\img'
	# cameraAutoForPictures(saveDir)
	
import numpy as np
import cv2
from mss import mss
import time
from pynput.mouse import Button, Controller

imgname = mss().shot()
print("正在获取您的屏幕..")
img = cv2.imread(imgname)
sp = img.shape
szX = sp[1]
szY = sp[0]
print("当前您的屏幕尺寸为{}x{}".format(szX, szY))
point1 = (int(szX * 0.49), int(szY * 0.6))
point2 = (int(szX * 0.51), int(szY * 0.4))
bounding_box = {
    "top": int(szX * 0.15),
    "left": int(szX * 0.49),
    "width": int(point2[0] - point1[0]),
    "height": int(point1[1] - point2[1]),
}
print("请将鱼钩放置在框内,5秒后开始钓鱼..开始后按q结束")
time.sleep(5)

mouse = Controller()

while True:
    mss_img = np.array(mss().grab(bounding_box))  # 持续捕获屏幕
    hsv = cv2.cvtColor(mss_img, cv2.COLOR_BGR2HSV)  # 转成hsv模式提取红色特征
    minRed = np.array([0, 43, 46])  # 定义红色最小值
    maxRed = np.array([10, 255, 255])  # 定义红色最大值
    mask = cv2.inRange(hsv, minRed, maxRed)  # 创建蒙版
    ret, binary = cv2.threshold(mask, 100, 255, cv2.THRESH_BINARY)  # 二值化
    contours, hierarchy = cv2.findContours(
        binary, cv2.RETR_TREE, cv2.CHAIN_APPROX_TC89_L1
    )  # 识别轮廓
    cv2.drawContours(mss_img, contours, -1, (0, 0, 255), 1)  # 画出轮廓
    cv2.imshow("img", binary)  # 展示图像

    cts = len(contours)
    if cts == 0:
        print("\n鱼钩消失，重新抛钩")
        mouse.click(Button.right)
        time.sleep(2)
        continue

        # 计算鱼钩高度
    hooktop = 9999
    hookbottom = 0
    for contour in contours:
        pts = len(contour)
        for i in range(0, pts):
            hooktop = min(hooktop, contour[i, 0, 1])
            hookbottom = max(hookbottom, contour[i, 0, 1])
    hookheight = hookbottom - hooktop

    print("\r鱼钩位置{}".format(hookheight), end="")
    if hookheight <= 0:
        print("\n收钩..")
        mouse.click(Button.right)
        print("抛钩..")
        mouse.click(Button.right)
        time.sleep(2)

    if (cv2.waitKey(1) & 0xFF) == ord("q"):
        cv2.destroyAllWindows()
        break

import numpy as np
import matplotlib.pyplot as plt

# 读取数据文件
file_path = (
    "/home/ahrs/workspace/esp/gesture_detection/scripts/image.txt"  # 更改为你的文件路径
)
with open(file_path, "r") as file:
    data = file.read()

# 数据清洗
data = data.strip(",")  # 移除最后一个逗号
pixels = np.fromstring(data, dtype=int, sep=",")

# 将一维数组转换为二维图像数组
image_width = 96  # 根据实际情况修改宽度
image_height = 96  # 根据实际情况修改高度
pixels = pixels.reshape((image_height, image_width))

# 使用matplotlib显示图像
plt.imshow(pixels, cmap="gray", vmin=-128, vmax=127)
plt.colorbar()  # 显示色标
plt.title("Visualized Image Data")
plt.show()

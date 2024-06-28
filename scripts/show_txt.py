import numpy as np
import matplotlib.pyplot as plt
import os

# 文件路径列表
file_paths = [
    "/home/ahrs/workspace/esp/gesture_detection/scripts/image.txt",
    "/home/ahrs/workspace/esp/gesture_detection/scripts/image copy.txt",
    # 添加更多文件路径
]

# 图像宽度和高度
image_width = 96  # 根据实际情况修改宽度
image_height = 96  # 根据实际情况修改高度

# 创建子图
num_images = len(file_paths)
cols = 3  # 每行显示的图片数量
rows = (num_images + cols - 1) // cols  # 计算行数

fig, axes = plt.subplots(rows, cols, figsize=(15, 5 * rows))

# 如果只有一行或一列时，axes可能是一维的，需要转换为二维
if rows == 1:
    axes = np.expand_dims(axes, axis=0)
if cols == 1:
    axes = np.expand_dims(axes, axis=1)

# 绘制每张图像
for idx, file_path in enumerate(file_paths):
    if os.path.exists(file_path):
        # 读取数据文件
        with open(file_path, "r") as file:
            data = file.read()

        # 数据清洗
        data = data.strip(",")  # 移除最后一个逗号
        pixels = np.fromstring(data, dtype=int, sep=",")

        # 将一维数组转换为二维图像数组
        pixels = pixels.reshape((image_height, image_width))

        # 选择子图位置
        ax = axes[idx // cols, idx % cols]

        # 显示图像
        im = ax.imshow(pixels, cmap="gray", vmin=-128, vmax=127)
        ax.set_title(f"{os.path.basename(file_path)}")
        fig.colorbar(im, ax=ax)  # 显示色标
    else:
        print(f"File not found: {file_path}")

# 移除空白子图
for i in range(num_images, rows * cols):
    if i >= num_images:
        fig.delaxes(axes.flatten()[i])

plt.tight_layout()
plt.show()

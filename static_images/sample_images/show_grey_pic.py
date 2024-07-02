import numpy as np
import matplotlib.pyplot as plt

# 从文件中读取像素值
with open("output.txt", "r") as file:
    pixel_values = file.read()

# 将读取的像素值转换为整数列表
pixels = list(map(int, pixel_values.split(",")))

# 检查像素值的数量是否正确
if len(pixels) != 96 * 96:
    raise ValueError("Pixel values do not match the expected size of 96x96")

# 将像素值转换为 96x96 的 numpy 数组
image = np.array(pixels).reshape((96, 96))

# 显示灰度图
plt.imshow(image, cmap="gray")
plt.title("Gray Scale Image")
plt.axis("off")  # 关闭坐标轴

# 保存灰度图
plt.savefig("gray_image.jpg", bbox_inches="tight", pad_inches=0)

# 显示灰度图
plt.show()

import numpy as np
from PIL import Image
import matplotlib.pyplot as plt
import matplotlib.font_manager as fm


# 分析 image0 格式
def analyze_image0_format(image0_path):
    with open(image0_path, "rb") as file:
        image0_data = file.read()

    # 假设图像尺寸为 96x96
    IMAGE_WIDTH = 96
    IMAGE_HEIGHT = 96

    # 转换二进制数据为 numpy 数组
    image0_array = np.frombuffer(image0_data, dtype=np.uint8)
    image0_array = image0_array.reshape((IMAGE_HEIGHT, IMAGE_WIDTH))

    # 打印数组的形状以确认
    print("图像数组形状:", image0_array.shape)

    # 显示灰度图像
    plt.imshow(image0_array, cmap="gray")
    plt.title("Image0 灰度图像")
    plt.show()

    return IMAGE_WIDTH, IMAGE_HEIGHT


# 转换 RGB 图像为灰度图像并保存为与 image0 相同格式的二进制文件
def convert_rgb_to_image0_format(rgb_image_path, output_path, width, height):
    rgb_image = Image.open(rgb_image_path)

    # 将RGB图像转换为灰度图像
    gray_image = rgb_image.convert("L")

    # 调整图像大小
    gray_image = gray_image.resize((width, height))

    # 转换为numpy数组
    gray_image_array = np.array(gray_image).reshape((height, width))

    # 保存为二进制文件
    gray_image_array.tofile(output_path)
    print(f"灰度图像已保存为 {output_path}")


# 主函数
def main(image0_path, rgb_image_path, output_path):
    # 分析 image0 的格式
    width, height = analyze_image0_format(image0_path)

    # 转换 RGB 图像为灰度图像并保存为二进制文件
    convert_rgb_to_image0_format(rgb_image_path, output_path, width, height)

    # 验证转换后的图像
    with open(output_path, "rb") as file:
        converted_data = file.read()
    converted_array = np.frombuffer(converted_data, dtype=np.uint8).reshape(
        (height, width)
    )

    plt.imshow(converted_array, cmap="gray")
    plt.title("Converted Image from image10.jpg")
    plt.show()


if __name__ == "__main__":
    image0_path = (
        "/home/ahrs/workspace/esp/gesture_detection/static_images/sample_images/image0"
    )
    rgb_image_path = "/home/ahrs/workspace/esp/gesture_detection/static_images/sample_images/output.jpg"
    output_path = (
        "/home/ahrs/workspace/esp/gesture_detection/static_images/sample_images/image23"
    )

    # 添加解决字体问题的代码
    font_path = "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"
    prop = fm.FontProperties(fname=font_path)
    plt.rcParams["font.family"] = prop.get_name()

    main(image0_path, rgb_image_path, output_path)

import argparse
from PIL import Image
import os


def resize_image(input_path, output_path, width, height, grayscale=False):
    with Image.open(input_path) as img:
        # Resize the image
        img = img.resize((width, height), Image.ANTIALIAS)

        # Convert to grayscale if needed
        if grayscale:
            img = img.convert("L")

        # Save the output image
        img.save(output_path)
        print(f"Image saved to {output_path}")


def check_file_existence(file_path):
    if not os.path.isfile(file_path):
        raise argparse.ArgumentTypeError(f"File '{file_path}' does not exist.")
    return file_path


def main():
    parser = argparse.ArgumentParser(
        description="Resize and optionally convert an RGB image to grayscale."
    )

    parser.add_argument(
        "-i",
        "--input",
        required=True,
        type=check_file_existence,
        help="Path to the input JPG image.",
    )
    parser.add_argument(
        "-o", "--output", required=True, help="Path to save the output image."
    )
    parser.add_argument(
        "-W", "--width", type=int, required=True, help="Width of the output image."
    )
    parser.add_argument(
        "-H", "--height", type=int, required=True, help="Height of the output image."
    )
    parser.add_argument(
        "-g", "--grayscale", action="store_true", help="Convert the image to grayscale."
    )

    args = parser.parse_args()

    resize_image(args.input, args.output, args.width, args.height, args.grayscale)


if __name__ == "__main__":
    main()


# python resize_image.py -i input.jpg -o output.jpg -W 800 -H 600 -g
# 参数说明：

# -i 或 --input：输入 JPG 图像的路径。
# -o 或 --output：输出图像的保存路径。
# -w 或 --width：输出图像的宽度（像素）。
# -h 或 --height：输出图像的高度（像素）。
# -g 或 --grayscale：可选参数，如果指定，将图像转换为灰度图。

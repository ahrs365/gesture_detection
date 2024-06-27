import matplotlib.pyplot as plt
import numpy as np

IMAGE_WIDTH = 96
IMAGE_HEIGHT = 96


def parse_output(file_path):
    gray_image = np.zeros((IMAGE_HEIGHT, IMAGE_WIDTH), dtype=np.uint8)
    converted_gray_image = np.zeros((IMAGE_HEIGHT, IMAGE_WIDTH), dtype=np.int8)
    rgb_image = np.zeros((IMAGE_HEIGHT, IMAGE_WIDTH, 3), dtype=np.int8)

    with open(file_path, "r") as file:
        lines = file.readlines()

        gray_section = True
        index = 0
        for line in lines:
            if "----------------------------------------------" in line:
                gray_section = False
                index = 0
                continue
            if gray_section:
                parts = line.strip().split(")(")
                for part in parts:
                    part = part.strip("()")
                    if part:
                        values = part.split(",")
                        index = int(values[0].strip())
                        gray_value = int(values[1].strip())
                        converted_value = int(values[2].strip())
                        row = index // IMAGE_WIDTH
                        col = index % IMAGE_WIDTH
                        gray_image[row, col] = gray_value
                        converted_gray_image[row, col] = converted_value
            else:
                values = line.strip().split(",")
                for value in values:
                    if value:
                        r = int(value)
                        row = index // IMAGE_WIDTH
                        col = index % IMAGE_WIDTH
                        rgb_image[row, col] = [r, r, r]
                        index += 1

    return gray_image, converted_gray_image, rgb_image


def visualize_images(gray_image, converted_gray_image, rgb_image):
    fig, axs = plt.subplots(1, 3, figsize=(15, 5))
    axs[0].imshow(gray_image, cmap="gray")
    axs[0].set_title("Original Gray Image")
    axs[1].imshow(converted_gray_image, cmap="gray")
    axs[1].set_title("Converted Gray Image")
    axs[2].imshow(rgb_image, cmap="gray")
    axs[2].set_title("RGB Image")
    plt.show()


gray_image, converted_gray_image, rgb_image = parse_output("output.txt")
visualize_images(gray_image, converted_gray_image, rgb_image)

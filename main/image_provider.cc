
/* Copyright 2019 The TensorFlow Authors. All Rights Reserved.

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

    http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.
==============================================================================*/
#include <cstdlib>
#include <cstring>
#include <iostream>

#include "freertos/FreeRTOS.h"
#include "freertos/task.h"
#include "esp_log.h"
#include "esp_spi_flash.h"
#include "esp_system.h"
#include "esp_timer.h"

#include "app_camera_esp.h"
#include "esp_camera.h"
#include "model_settings.h"
#include "image_provider.h"
#include "esp_main.h"
#include <math.h> // for floor function

static const char* TAG = "app_camera";

static uint16_t *display_buf; // buffer to hold data to be sent to display

// Get the camera module ready
TfLiteStatus InitCamera() {
#if CLI_ONLY_INFERENCE
  ESP_LOGI(TAG, "CLI_ONLY_INFERENCE enabled, skipping camera init");
  return kTfLiteOk;
#endif
// if display support is present, initialise display buf
#if DISPLAY_SUPPORT
  if (display_buf == NULL) {
    // Size of display_buf:
    // Frame 96x96 from camera is extrapolated to 192x192. RGB565 pixel format -> 2 bytes per pixel
    display_buf = (uint16_t *) heap_caps_malloc(96 * 2 * 96 * 2 * sizeof(uint16_t), MALLOC_CAP_SPIRAM | MALLOC_CAP_8BIT);
  }
  if (display_buf == NULL) {
    ESP_LOGE(TAG, "Couldn't allocate display buffer");
    return kTfLiteError;
  }
#endif // DISPLAY_SUPPORT

#if ESP_CAMERA_SUPPORTED
  int ret = app_camera_init();
  if (ret != 0) {
    MicroPrintf("Camera init failed\n");
    return kTfLiteError;
  }
  MicroPrintf("Camera Initialized\n");
#else
  ESP_LOGE(TAG, "Camera not supported for this device");
#endif
  return kTfLiteOk;
}

void *image_provider_get_display_buf()
{
  return (void *) display_buf;
}

// Get an image from the camera module
TfLiteStatus GetImage(int image_width, int image_height, int channels, int8_t* image_data) {
#if ESP_CAMERA_SUPPORTED
  camera_fb_t* fb = esp_camera_fb_get();
  if (!fb) {
    ESP_LOGE(TAG, "Camera capture failed");
    return kTfLiteError;
  }

#if DISPLAY_SUPPORT
  // In case if display support is enabled, we initialise camera in rgb mode
  // Hence, we need to convert this data to grayscale to send it to tf model
  // For display we extra-polate the data to 192X192
  for (int i = 0; i < kNumRows; i++) {
    for (int j = 0; j < kNumCols; j++) {
      uint16_t pixel = ((uint16_t *) (fb->buf))[i * kNumCols + j];

      // for inference
      uint8_t hb = pixel & 0xFF;
      uint8_t lb = pixel >> 8;
      uint8_t r = (lb & 0x1F) << 3;
      uint8_t g = ((hb & 0x07) << 5) | ((lb & 0xE0) >> 3);
      uint8_t b = (hb & 0xF8);

      /**
       * Gamma corected rgb to greyscale formula: Y = 0.299R + 0.587G + 0.114B
       * for effiency we use some tricks on this + quantize to [-128, 127]
       */
      int8_t grey_pixel = ((305 * r + 600 * g + 119 * b) >> 10) - 128;

      image_data[i * kNumCols + j] = grey_pixel;

      // to display
      display_buf[2 * i * kNumCols * 2 + 2 * j] = pixel;
      display_buf[2 * i * kNumCols * 2 + 2 * j + 1] = pixel;
      display_buf[(2 * i + 1) * kNumCols * 2 + 2 * j] = pixel;
      display_buf[(2 * i + 1) * kNumCols * 2 + 2 * j + 1] = pixel;
    }
  }
#else // DISPLAY_SUPPORT
  MicroPrintf("Image Captured\n");
  // We have initialised camera to grayscale
  // Just quantize to int8_t
  printf("start capture--------------------------\n");
  for (int i = 0; i < image_width * image_height; i++) {
    image_data[i] = ((uint8_t *) fb->buf)[i] ^ 0x80;
    printf("%d,",image_data[i]);
  }
  printf("stop capture--------------------------\n");

  // MicroPrintf("\n");

#endif // DISPLAY_SUPPORT

  esp_camera_fb_return(fb);
  /* here the esp camera can give you grayscale image directly */
  return kTfLiteOk;
#else
  return kTfLiteError;
#endif
}

// Process the captured image
TfLiteStatus ProcessImage(int image_width, int image_height,int8_t* image_data) {
  const int imgSize = 96;
  // 设置捕获图像的宽度和高度
  int kCaptureWidth = 320;
  int kCaptureHeight = 240;
  int capDataLen = kCaptureWidth * kCaptureHeight * 2; // RGB565 每个像素2字节
  camera_fb_t* fb = esp_camera_fb_get();
  if (!fb) {
      ESP_LOGE(TAG, "Camera capture failed");
      return kTfLiteError;
  }

  uint8_t* captured_data = fb->buf;
  // printf("start--------------\n");
  // Color of the current pixel
  uint16_t color;
  for (int y = 0; y < imgSize; y++) {
    for (int x = 0; x < imgSize; x++) {
      int currentCapX = floor(map(x, 0, imgSize, 40, kCaptureWidth - 80));
      int currentCapY = floor(map(y, 0, imgSize, 0, kCaptureHeight));
      // Read the color of the pixel as 16-bit integer
      int read_index = (currentCapY * kCaptureWidth + currentCapX) * 2;
      int i2 = (currentCapY * kCaptureWidth + currentCapX + 1) * 2;
      int i3 = ((currentCapY + 1) * kCaptureWidth + currentCapX) * 2;
      int i4 = ((currentCapY + 1) * kCaptureWidth + currentCapX + 1) * 2;

      uint8_t high_byte = captured_data[read_index];
      uint8_t low_byte = captured_data[read_index + 1];

      color = ((uint16_t)high_byte << 8) | low_byte;
      // Extract the color values (5 red bits, 6 green, 5 blue)
      uint8_t r, g, b;
      r = ((color & 0xF800) >> 11) * 8;
      g = ((color & 0x07E0) >> 5) * 4;
      b = ((color & 0x001F) >> 0) * 8;
      // Convert to grayscale by calculating luminance
      float gray_value = (0.2126 * r) + (0.7152 * g) + (0.0722 * b);

      if (i2 > 0 && i2 < capDataLen - 1) {
          high_byte = captured_data[i2];
          low_byte = captured_data[i2 + 1];
          color = ((uint16_t)high_byte << 8) | low_byte;
          r = ((color & 0xF800) >> 11) * 8;
          g = ((color & 0x07E0) >> 5) * 4;
          b = ((color & 0x001F) >> 0) * 8;
          gray_value += (0.2126 * r) + (0.7152 * g) + (0.0722 * b);
      }
      if (i3 > 0 && i3 < capDataLen - 1) {
          high_byte = captured_data[i3];
          low_byte = captured_data[i3 + 1];
          color = ((uint16_t)high_byte << 8) | low_byte;
          r = ((color & 0xF800) >> 11) * 8;
          g = ((color & 0x07E0) >> 5) * 4;
          b = ((color & 0x001F) >> 0) * 8;
          gray_value += (0.2126 * r) + (0.7152 * g) + (0.0722 * b);
      }

      if (i4 > 0 && i4 < capDataLen - 1) {
          high_byte = captured_data[i4];
          low_byte = captured_data[i4 + 1];
          color = ((uint16_t)high_byte << 8) | low_byte;
          r = ((color & 0xF800) >> 11) * 8;
          g = ((color & 0x07E0) >> 5) * 4;
          b = ((color & 0x001F) >> 0) * 8;
          gray_value += (0.2126 * r) + (0.7152 * g) + (0.0722 * b);
      }

      gray_value = gray_value / 4;

      // Convert to signed 8-bit integer by subtracting 128.
      gray_value -= 128;
      // The index of this pixel in our flat output buffer
      int index = y * image_width + x;
      image_data[index] = static_cast<int8_t>(gray_value);
      // printf("%d,", image_data[index]);
    }
  }
  // printf("end--------------\n");

  esp_camera_fb_return(fb);
  return kTfLiteOk;
}


// Map function to map a number from one range to another
int map(int x, int in_min, int in_max, int out_min, int out_max) {
    return (x - in_min) * (out_max - out_min) / (in_max - in_min) + out_min;
}
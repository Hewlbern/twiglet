// ST7701 480x480 RGB panel on the Waveshare ESP32-S3-Touch-LCD-2.1 (flat, SKU 28169).
// Init sequence, pins and timings are ported from Waveshare's official demo
// (ESP32-S3-Touch-LCD-2.1 Arduino example "LVGL_Arduino": Display_ST7701.cpp / TCA9554PWR.cpp), reorganised as a table.
#pragma once
#include <Arduino.h>
#include "esp_lcd_panel_ops.h"
#include "esp_lcd_panel_rgb.h"

#define PANEL_W 480
#define PANEL_H 480

bool panel_begin();                    // I2C expander + ST7701 SPI init + RGB panel with 2 PSRAM frame buffers
uint16_t *panel_backbuffer();          // buffer to draw the next frame into (RGB565, 480*480)
void panel_present();                  // show the back buffer (swaps at vsync) and wait until the old front buffer is free
void panel_backlight(uint8_t pct);     // 0..100

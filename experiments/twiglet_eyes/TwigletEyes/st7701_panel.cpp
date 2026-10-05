#include "st7701_panel.h"
#include <Wire.h>
#include "driver/spi_master.h"
#include "freertos/semphr.h"

// ---- board pins (Waveshare ESP32-S3-Touch-LCD-2.1) ----
#define I2C_SDA 15
#define I2C_SCL 7
#define TCA9554_ADDR 0x20
#define EXIO_LCD_RST 1   // EXIO1
#define EXIO_TP_RST  2   // EXIO2
#define EXIO_LCD_CS  3   // EXIO3
#define LCD_SPI_SDA 1
#define LCD_SPI_SCL 2
#define LCD_BL 6
static const int RGB_DATA[16] = {5, 45, 48, 47, 21, 14, 13, 12, 11, 10, 9, 46, 3, 8, 18, 17};
#define RGB_HSYNC 38
#define RGB_VSYNC 39
#define RGB_DE 40
#define RGB_PCLK 41

static esp_lcd_panel_handle_t s_panel = nullptr;
static spi_device_handle_t s_spi = nullptr;
static uint16_t *s_fb[2] = {nullptr, nullptr};
static int s_back = 1;
static SemaphoreHandle_t s_vsync = nullptr;
static uint8_t s_exio = 0xFF;

static void exio_write(uint8_t reg, uint8_t v) { Wire.beginTransmission(TCA9554_ADDR); Wire.write(reg); Wire.write(v); Wire.endTransmission(); }
static void exio_set(int pin, bool high) { if (high) s_exio |= (1 << (pin - 1)); else s_exio &= ~(1 << (pin - 1)); exio_write(0x01, s_exio); }

static void lcd_cmd(uint8_t c) { spi_transaction_t t = {}; t.cmd = 0; t.addr = c; spi_device_transmit(s_spi, &t); }
static void lcd_dat(uint8_t d) { spi_transaction_t t = {}; t.cmd = 1; t.addr = d; spi_device_transmit(s_spi, &t); }

// {cmd, n, data...}; n = 0xFE -> delay(data[0]*10 ms) after the command
static const uint8_t INIT[] = {
  0xFF, 5, 0x77, 0x01, 0x00, 0x00, 0x10,
  0xC0, 2, 0x3B, 0x00,
  0xC1, 2, 0x0B, 0x02,
  0xC2, 2, 0x07, 0x02,
  0xCC, 1, 0x10,
  0xCD, 1, 0x08,
  0xB0, 16, 0x00, 0x11, 0x16, 0x0e, 0x11, 0x06, 0x05, 0x09, 0x08, 0x21, 0x06, 0x13, 0x10, 0x29, 0x31, 0x18,
  0xB1, 16, 0x00, 0x11, 0x16, 0x0e, 0x11, 0x07, 0x05, 0x09, 0x09, 0x21, 0x05, 0x13, 0x11, 0x2a, 0x31, 0x18,
  0xFF, 5, 0x77, 0x01, 0x00, 0x00, 0x11,
  0xB0, 1, 0x6d,
  0xB1, 1, 0x37,
  0xB2, 1, 0x81,
  0xB3, 1, 0x80,
  0xB5, 1, 0x43,
  0xB7, 1, 0x85,
  0xB8, 1, 0x20,
  0xC1, 1, 0x78,
  0xC2, 1, 0x78,
  0xD0, 1, 0x88,
  0xE0, 3, 0x00, 0x00, 0x02,
  0xE1, 11, 0x03, 0xA0, 0x00, 0x00, 0x04, 0xA0, 0x00, 0x00, 0x00, 0x20, 0x20,
  0xE2, 13, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
  0xE3, 4, 0x00, 0x00, 0x11, 0x00,
  0xE4, 2, 0x22, 0x00,
  0xE5, 16, 0x05, 0xEC, 0xA0, 0xA0, 0x07, 0xEE, 0xA0, 0xA0, 0, 0, 0, 0, 0, 0, 0, 0,
  0xE6, 4, 0x00, 0x00, 0x11, 0x00,
  0xE7, 2, 0x22, 0x00,
  0xE8, 16, 0x06, 0xED, 0xA0, 0xA0, 0x08, 0xEF, 0xA0, 0xA0, 0, 0, 0, 0, 0, 0, 0, 0,
  0xEB, 7, 0x00, 0x00, 0x40, 0x40, 0x00, 0x00, 0x00,
  0xED, 16, 0xFF, 0xFF, 0xFF, 0xBA, 0x0A, 0xBF, 0x45, 0xFF, 0xFF, 0x54, 0xFB, 0xA0, 0xAB, 0xFF, 0xFF, 0xFF,
  0xEF, 6, 0x10, 0x0D, 0x04, 0x08, 0x3F, 0x1F,
  0xFF, 5, 0x77, 0x01, 0x00, 0x00, 0x13,
  0xEF, 1, 0x08,
  0xFF, 5, 0x77, 0x01, 0x00, 0x00, 0x00,
  0x36, 1, 0x00,
  0x3A, 1, 0x66,
  0x11, 0xFE, 48,        // sleep out, 480 ms
  0x20, 0xFE, 12,        // inversion off (as in the vendor demo), 120 ms
  0x29, 0,               // display on
};

static bool IRAM_ATTR on_vsync(esp_lcd_panel_handle_t, const esp_lcd_rgb_panel_event_data_t *, void *) {
  BaseType_t woken = pdFALSE; xSemaphoreGiveFromISR(s_vsync, &woken); return woken == pdTRUE;
}

bool panel_begin() {
  Wire.begin(I2C_SDA, I2C_SCL);
  exio_write(0x03, 0x00);                 // all EXIO pins outputs
  s_exio = 0xFF; exio_write(0x01, s_exio);
  exio_set(EXIO_LCD_RST, false); delay(10); exio_set(EXIO_LCD_RST, true); delay(50);

  spi_bus_config_t bus = {};
  bus.mosi_io_num = LCD_SPI_SDA; bus.miso_io_num = -1; bus.sclk_io_num = LCD_SPI_SCL; bus.quadwp_io_num = -1; bus.quadhd_io_num = -1; bus.max_transfer_sz = 64;
  if (spi_bus_initialize(SPI2_HOST, &bus, SPI_DMA_CH_AUTO) != ESP_OK) return false;
  spi_device_interface_config_t dev = {};
  dev.command_bits = 1; dev.address_bits = 8; dev.mode = 0; dev.clock_speed_hz = 40000000; dev.spics_io_num = -1; dev.queue_size = 1;
  if (spi_bus_add_device(SPI2_HOST, &dev, &s_spi) != ESP_OK) return false;

  exio_set(EXIO_LCD_CS, false); delay(10);
  for (size_t i = 0; i < sizeof(INIT);) {
    uint8_t c = INIT[i++], n = INIT[i++];
    lcd_cmd(c);
    if (n == 0xFE) { delay(INIT[i++] * 10); continue; }
    for (uint8_t k = 0; k < n; k++) lcd_dat(INIT[i++]);
  }
  exio_set(EXIO_LCD_CS, true); delay(10);

  esp_lcd_rgb_panel_config_t cfg = {};
  cfg.clk_src = LCD_CLK_SRC_DEFAULT;
  cfg.timings.pclk_hz = 16 * 1000 * 1000;
  cfg.timings.h_res = PANEL_W; cfg.timings.v_res = PANEL_H;
  cfg.timings.hsync_pulse_width = 8; cfg.timings.hsync_back_porch = 10; cfg.timings.hsync_front_porch = 50;
  cfg.timings.vsync_pulse_width = 3; cfg.timings.vsync_back_porch = 8; cfg.timings.vsync_front_porch = 8;
  cfg.data_width = 16; cfg.bits_per_pixel = 16; cfg.num_fbs = 2;
  cfg.bounce_buffer_size_px = 10 * PANEL_W;
  cfg.hsync_gpio_num = RGB_HSYNC; cfg.vsync_gpio_num = RGB_VSYNC; cfg.de_gpio_num = RGB_DE; cfg.pclk_gpio_num = RGB_PCLK; cfg.disp_gpio_num = -1;
  for (int k = 0; k < 16; k++) cfg.data_gpio_nums[k] = RGB_DATA[k];
  cfg.flags.fb_in_psram = 1;
  if (esp_lcd_new_rgb_panel(&cfg, &s_panel) != ESP_OK) return false;
  s_vsync = xSemaphoreCreateBinary();
  esp_lcd_rgb_panel_event_callbacks_t cbs = {}; cbs.on_vsync = on_vsync;
  esp_lcd_rgb_panel_register_event_callbacks(s_panel, &cbs, nullptr);
  esp_lcd_panel_reset(s_panel); esp_lcd_panel_init(s_panel);
  void *a = nullptr, *b = nullptr;
  esp_lcd_rgb_panel_get_frame_buffer(s_panel, 2, &a, &b);
  s_fb[0] = (uint16_t *)a; s_fb[1] = (uint16_t *)b;
  memset(s_fb[0], 0, PANEL_W * PANEL_H * 2); memset(s_fb[1], 0, PANEL_W * PANEL_H * 2);
  ledcAttach(LCD_BL, 20000, 10);
  panel_backlight(80);
  return s_fb[0] && s_fb[1];
}
uint16_t *panel_backbuffer() { return s_fb[s_back]; }
void panel_present() {
  // passing one of the driver's own frame buffers makes the driver switch to it (no copy)
  esp_lcd_panel_draw_bitmap(s_panel, 0, 0, PANEL_W, PANEL_H, s_fb[s_back]);
  xSemaphoreTake(s_vsync, 0);                         // drop a stale vsync
  xSemaphoreTake(s_vsync, pdMS_TO_TICKS(40));         // the swap happens at the next vsync
  s_back ^= 1;
}
void panel_backlight(uint8_t pct) { if (pct > 100) pct = 100; ledcWrite(LCD_BL, (uint32_t)pct * 1023 / 100); }

/*  TwigletEyes - pixel-art eyes for Twiglet (Open Duck Mini v2 head A v3)
    Board : Waveshare ESP32-S3-Touch-LCD-2.1 (flat panel, 480x480 ST7701 RGB), one board per eye, same firmware on both.
    Arduino IDE: board "ESP32S3 Dev Module" (esp32 core >= 3.0), PSRAM "OPI PSRAM", Flash 16MB, USB CDC On Boot "Disabled"
                 (so Serial = UART0 = GPIO43/44 = the 12-pin header TXD/RXD and the "UART" USB-C port).
    Link   : Pi Zero 2W /dev/serial0 115200 8N1. Pi TX -> RXD (GPIO44) of BOTH boards; L board TXD (GPIO43) -> Pi RX. Common GND.
    Protocol (one line per command, '\n' terminated, case-insensitive; optional "L:" / "R:" prefix = only that eye):
      EYE ring|heart|happy|angry|wide|blink|off|test    LOOK x y   (x,y -1..1; +x = toward the robot's own left, +y = up)
      BLINK          AUTOBLINK 0|1     BRIGHT 0..100     COLOR rrggbb
      SIDE L|R       ROT 0..3          MIRROR 0|1        CENTER x y      SAVE     INFO     PING
    Replies ("OK ...", "ERR ...") are only sent by the eye whose SIDE is L (its TX is the only one wired back), unless ECHO 1. */
#include <Arduino.h>
#include <Preferences.h>
#include <WiFi.h>
#include "st7701_panel.h"
#include "eye_bitmaps.h"
#include "eye_geometry.h"

enum Expr { E_RING, E_HEART, E_HAPPY, E_ANGRY, E_WIDE, E_OFF, E_TEST };
struct Cfg { char side; int cx, cy, rot, mirror, bright; uint16_t color; bool autoblink, echo; } cfg;
static Expr expr = E_RING;
static float lookX = 0, lookY = 0;                 // -1..1
static uint32_t blinkStart = 0; static bool blinking = false; static uint32_t nextBlink = 3000;
static uint32_t exprStart = 0;
static bool dirty = true;
Preferences prefs;

static uint16_t rgb565(uint32_t rgb) { return ((rgb >> 8) & 0xF800) | ((rgb >> 5) & 0x07E0) | ((rgb >> 3) & 0x001F); }
static void loadCfg() {
  prefs.begin("twigleteyes", true);
  cfg.side = (char)prefs.getUChar("side", DEFAULT_SIDE);
  bool L = cfg.side == 'L';
  cfg.cx = prefs.getInt("cx", L ? GEO_L_CX : GEO_R_CX); cfg.cy = prefs.getInt("cy", L ? GEO_L_CY : GEO_R_CY);
  cfg.rot = prefs.getInt("rot", L ? GEO_L_ROT : GEO_R_ROT); cfg.mirror = prefs.getInt("mir", 0);
  cfg.bright = prefs.getInt("bri", 80); cfg.color = prefs.getUShort("col", rgb565(0xFF7A00));
  cfg.autoblink = prefs.getBool("ab", true); cfg.echo = prefs.getBool("echo", false);
  prefs.end();
}
static void saveCfg() {
  prefs.begin("twigleteyes", false);
  prefs.putUChar("side", cfg.side); prefs.putInt("cx", cfg.cx); prefs.putInt("cy", cfg.cy); prefs.putInt("rot", cfg.rot); prefs.putInt("mir", cfg.mirror);
  prefs.putInt("bri", cfg.bright); prefs.putUShort("col", cfg.color); prefs.putBool("ab", cfg.autoblink); prefs.putBool("echo", cfg.echo);
  prefs.end();
}
static void reply(const String &s) { if (cfg.side == 'L' || cfg.echo) Serial.println(s); }

// ---------------- drawing ----------------
static uint16_t *fb;
static inline void fillRect(int x0, int y0, int w, int h, uint16_t c) {
  int x1 = x0 + w, y1 = y0 + h; if (x0 < 0) x0 = 0; if (y0 < 0) y0 = 0; if (x1 > PANEL_W) x1 = PANEL_W; if (y1 > PANEL_H) y1 = PANEL_H;
  for (int y = y0; y < y1; y++) { uint16_t *p = fb + y * PANEL_W + x0; for (int x = x0; x < x1; x++) *p++ = c; }
}
// art-frame point (u right, v up; pixels from the aperture centre) -> panel pixel
static void artToPanel(int u, int v, int &x, int &y) {
  if (cfg.mirror) u = -u;
  int px, py;                                       // un-rotated: art right = +x, art up = -y
  switch (cfg.rot & 3) { case 0: px = u; py = -v; break; case 1: px = v; py = u; break; case 2: px = -u; py = v; break; default: px = -v; py = -u; break; }
  x = cfg.cx + px; y = cfg.cy + py;
}
// one LED "dot": EYE_DOT x EYE_DOT rounded square centred on art cell (i,j) shifted by (di,dj) cells
static void dot(int i, int j, uint16_t c) {
  int u = (int)((j - (EYE_N - 1) / 2.0f) * EYE_CELL), v = (int)(-(i - (EYE_N - 1) / 2.0f) * EYE_CELL);
  int x, y; artToPanel(u, v, x, y);
  int h = EYE_DOT / 2;
  fillRect(x - h + 1, y - h, EYE_DOT - 2, EYE_DOT, c); fillRect(x - h, y - h + 1, EYE_DOT, EYE_DOT - 2, c);   // 1 px cut corners
}
static inline bool bmpGet(const uint8_t (*b)[EYE_N / 8], int i, int j) {
  if (i < 0 || j < 0 || i >= EYE_N || j >= EYE_N) return false; return b[i][j >> 3] & (0x80 >> (j & 7));
}
// lids: top/bottom limits in cells from the centre (rows with |row centre| outside are hidden); closed -> 3-row line
static void drawBitmap(const uint8_t (*b)[EYE_N / 8], int di, int dj, float lidTop, float lidBot, bool closed) {
  const float c0 = (EYE_N - 1) / 2.0f;
  for (int i = 0; i < EYE_N; i++) {
    float yc = -(i - c0);
    for (int j = 0; j < EYE_N; j++) {
      float xc = j - c0;
      if (xc * xc + yc * yc > EYE_VIS_R * EYE_VIS_R) continue;
      bool on;
      if (closed) on = fabsf(yc) <= 1.5f && fabsf(xc) <= EYE_R_OUT - 0.5f;
      else on = bmpGet(b, i - di, j - dj) && yc <= lidTop && yc >= lidBot;
      if (on) dot(i, j, cfg.color);
    }
  }
}
static void drawTest() {
  fillRect(0, 0, 40, 40, rgb565(0xFF0000));                           // native (0,0) corner: red square
  fillRect(PANEL_W / 2 - 1, 0, 2, PANEL_H, rgb565(0x303030)); fillRect(0, PANEL_H / 2 - 1, PANEL_W, 2, rgb565(0x303030));
  // art-frame arrow pointing UP (world up) + a dot on the viewer's RIGHT, centred on the configured aperture centre
  for (int k = 0; k < 14; k++) { dot(26 - k, 19, cfg.color); dot(26 - k, 20, cfg.color); }
  for (int k = 0; k < 5; k++) { dot(12 + k, 19 - k, cfg.color); dot(12 + k, 20 + k, cfg.color); }
  dot(19, 33, rgb565(0x00FF00)); dot(20, 33, rgb565(0x00FF00));
  // aperture outline (56 mm = ~250 px radius) in grey
  for (int a = 0; a < 360; a += 2) { int x, y; artToPanel((int)(249 * cosf(a * DEG_TO_RAD)), (int)(249 * sinf(a * DEG_TO_RAD)), x, y); fillRect(x - 1, y - 1, 3, 3, rgb565(0x606060)); }
}
static void render() {
  fb = panel_backbuffer();
  memset(fb, 0, PANEL_W * PANEL_H * 2);
  uint32_t t = millis();
  // blink: 7 phases x 55 ms (open, 1/3, 2/3, closed, 2/3, 1/3, open)
  float lidTop = 99, lidBot = -99; bool closed = false;
  if (blinking) {
    int ph = (t - blinkStart) / 55;
    static const float TOP[7] = {99, 8, 3, 0, 3, 8, 99}, BOT[7] = {-99, -11, -6, 0, -6, -11, -99};
    if (ph >= 7) blinking = false; else { lidTop = TOP[ph]; lidBot = BOT[ph]; closed = ph == 3; }
  }
  int dj = (int)roundf(lookX * 4.0f * (cfg.mirror ? 1 : 1)), di = (int)roundf(-lookY * 3.5f);
  // +LOOK x = toward the robot's own left = the viewer's right = +art x (same for both eyes)
  switch (expr) {
    case E_RING: drawBitmap(BMP_RING, di, dj, lidTop, lidBot, closed); break;
    case E_WIDE: drawBitmap(BMP_WIDE, di, dj, lidTop, lidBot, closed); break;
    case E_HAPPY: drawBitmap(BMP_HAPPY, 0, 0, 99, -99, false); break;
    case E_ANGRY: drawBitmap(cfg.side == 'L' ? BMP_ANGRY_L : BMP_ANGRY_R, di, dj, 99, -99, false); break;
    case E_HEART: { uint32_t b = (t - exprStart) % 900; drawBitmap((b < 180 || (b > 330 && b < 480)) ? BMP_HEART : BMP_HEART_SMALL, 0, 0, 99, -99, false); break; }  // double beat
    case E_TEST: drawTest(); break;
    case E_OFF: break;
  }
  panel_present();
}

// ---------------- commands ----------------
static void startBlink() { blinking = true; blinkStart = millis(); dirty = true; }
static void handle(String line) {
  line.trim(); if (!line.length()) return;
  String up = line; up.toUpperCase();
  if (up.length() > 2 && up[1] == ':' && (up[0] == 'L' || up[0] == 'R')) { if (up[0] != cfg.side) return; up = up.substring(2); up.trim(); }
  int sp = up.indexOf(' '); String cmd = sp < 0 ? up : up.substring(0, sp); String arg = sp < 0 ? "" : up.substring(sp + 1); arg.trim();
  if (cmd == "EYE") {
    if (arg == "BLINK") { startBlink(); }
    else {
      Expr e;
      if (arg == "RING" || arg == "DEFAULT") e = E_RING; else if (arg == "HEART" || arg == "HEARTS") e = E_HEART; else if (arg == "HAPPY") e = E_HAPPY;
      else if (arg == "ANGRY") e = E_ANGRY; else if (arg == "WIDE") e = E_WIDE; else if (arg == "OFF") e = E_OFF; else if (arg == "TEST") e = E_TEST;
      else { reply("ERR unknown eye " + arg); return; }
      expr = e; exprStart = millis(); if (e == E_OFF) panel_backlight(0); else panel_backlight(cfg.bright);
    }
  } else if (cmd == "BLINK") startBlink();
  else if (cmd == "LOOK") { float x = 0, y = 0; sscanf(arg.c_str(), "%f %f", &x, &y); lookX = constrain(x, -1.0f, 1.0f); lookY = constrain(y, -1.0f, 1.0f); }
  else if (cmd == "AUTOBLINK") cfg.autoblink = arg.toInt() != 0;
  else if (cmd == "BRIGHT") { cfg.bright = constrain(arg.toInt(), 0, 100); panel_backlight(cfg.bright); }
  else if (cmd == "COLOR") cfg.color = rgb565(strtoul(arg.c_str(), nullptr, 16));
  else if (cmd == "SIDE") { if (arg == "L" || arg == "R") cfg.side = arg[0]; }
  else if (cmd == "ROT") cfg.rot = arg.toInt() & 3;
  else if (cmd == "MIRROR") cfg.mirror = arg.toInt() != 0;
  else if (cmd == "CENTER") { sscanf(arg.c_str(), "%d %d", &cfg.cx, &cfg.cy); }
  else if (cmd == "ECHO") cfg.echo = arg.toInt() != 0;
  else if (cmd == "SAVE") saveCfg();
  else if (cmd == "PING") { reply(String("PONG ") + cfg.side); return; }
  else if (cmd == "INFO") { reply(String("INFO side=") + cfg.side + " cx=" + cfg.cx + " cy=" + cfg.cy + " rot=" + cfg.rot + " mirror=" + cfg.mirror + " bright=" + cfg.bright + " expr=" + (int)expr); return; }
  else { reply("ERR unknown " + cmd); return; }
  dirty = true; reply("OK " + up);
}

void setup() {
  Serial.begin(115200);
  WiFi.mode(WIFI_OFF); btStop();
  loadCfg();
  if (!panel_begin()) { Serial.println("ERR panel init failed (PSRAM enabled?)"); }
  panel_backlight(cfg.bright);
  exprStart = millis(); nextBlink = millis() + 2500 + (cfg.side == 'R' ? 0 : 0);
  reply(String("READY TwigletEyes side=") + cfg.side);
}
void loop() {
  static String buf;
  while (Serial.available()) { char ch = Serial.read(); if (ch == '\n' || ch == '\r') { handle(buf); buf = ""; } else if (buf.length() < 96) buf += ch; }
  uint32_t t = millis();
  // auto-blink: both boards get the same random seed schedule only if commanded; Pi can send "BLINK" to sync both eyes
  if (cfg.autoblink && !blinking && (expr == E_RING || expr == E_WIDE) && (int32_t)(t - nextBlink) >= 0) { startBlink(); nextBlink = t + 2500 + (esp_random() % 4000); }
  bool animating = blinking || expr == E_HEART;
  static uint32_t lastFrame = 0;
  if ((dirty || animating) && t - lastFrame >= 16) { lastFrame = t; dirty = false; render(); }
  else delay(1);
}

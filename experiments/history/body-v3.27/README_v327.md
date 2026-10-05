# Twiglet head v3.27 - wig only (head_upper byte-identical to v3.16-v3.26)

Mike's feedback on v3.26: "make the hair less spiky, and more cohesive - the ones over the middle of the head should be more cohesive and angular but whole,
the sideburns less spiky, more like blond hair, the side a bit lower on either side, more middle rising and the middle angular triangle almost",
then "middle strand like photo, and ones to side too".

## Changes (hair_v327.py, baked "v3.27 tuning" block; variant H4 of ~25 tried)
- Cohesive clumps: lock bases x0.9 (was x0.82), partings 3 mm (was 4 mm), fuller lock ends (taper stops at 0.14 x root width, was 0.10).
- Central fringe strand, traced from the original + front photos: straight down and symmetric (curl, S-wave and twist 0).
  It is a flat-faceted, straight-sided triangle with a crisp centre ridge. The crest is 25 mm (was 18), so it stands proud ("middle rising").
  It is 36 mm wide and runs th 16-66 (was 59), with its point between the eyes at eye-top level.
- The two strands beside it: narrower (26 mm, was 36/42) and longer (th1 66, was 51/52). They are flat-faceted and pointed, and swept outward over the eye tops (curl +-28, was +-12).
  A clear V parting separates each from the central strand, as in the photos. The eye screens stay 100 % clear.
- Sides lower: F4/F5 th1 86 -> 92 (about 11 mm). The side-lock arm relief starts at th 80 (was 77), about 5.5 mm lower. Arm sweep is still 0/7/7.
- Sideburns: fully rounded 26 mm strand bundles (were 20 mm) with 3 soft strand grooves and a wide rounded end (0.5 x width), so there is no spike.
- Fly-away blades: minimum blade thickness 1.4 -> 1.9 mm, so the blade edge lips are >= 1.7 mm (wall check).
- Unchanged: hat seat (8 mm smooth crown, 4.5 mm recessed band) and the solid felt-hat render proxy.
- New per-lock hooks: STYLE (ROUND / PEXP / WEND / LR / L / TAPER / TIP_EXP / GROOVE), COHESIVE and TRI. COHESIVE and TRI are off in the final build:
  - a triangular *notch* hairline (TRI) was tried first;
  - the photos show a downward-pointing central strand instead, and fitting it to them raised front IoU from 0.474 to 0.520.

## Checks
- Eye coverage 0 / 0 %; head-range contacts 6/315; arm contacts 0/7/7.
- Head pitch 0.203 N·m standing (2.4x margin vs 0.49 N·m).
- Head+arm margin 32.5 mm at 4 % infill. Sweep in sim/sweep327.txt: 0 % 29.3, 1 % 22.9, 2 % 21.4, 2.5 % 24.0, 3 % 23.5, 3.5 % 21.7, 4 % 32.5, 5 % 23.5, 6 % 31.3, 7 % 26.5, 8 % 26.5.
  The print setting is therefore 4 % lightning (v3.26 was 3 %).
- Walls: wallsec 0 genuinely < 1.2 mm (min local wall 1.5 mm). The wig is watertight, 1 body, 652 cm3, 241.0 x 248.7 x 247.7 mm oriented, and fits the P1S.
- head_upper md5 (vertices + faces) c7039022ad79686931a170ea7b64255c, the same as v3.26.
- Gaits:
  - fast: 100 % (20/20) at 0.213 m/s after refines (seed 33, then 7). v3.26 was 95 % at 0.206 m/s.
  - energy: 100 % at 0.161 m/s.

## Print
Wig ~188 g + ~53 g tree support, ~15.1 h on the P1S. 0.2 mm layers, 2 walls, 4 % LIGHTNING infill (required by the sims).

## Note
At 19:29 on 30 Sep, the other folders' .cache dirs were deleted on the shared box, including body-v3.16/.cache/head_v315.pkl.
head_v327 now builds from body-v3.27/.cache/head_v326.pkl and reuses its head_upper unchanged; the md5 above verifies it.

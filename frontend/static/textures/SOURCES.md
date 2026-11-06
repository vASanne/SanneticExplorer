# Planet maps

Equirectangular color maps are the Solar System Scope set, used under
[Creative Commons Attribution 4.0](https://creativecommons.org/licenses/by/4.0/).

Credit: Solar System Scope — https://www.solarsystemscope.com/textures/

Those maps are processed from public-domain NASA / USGS / JPL imagery (SDO, MESSENGER,
Magellan, Blue Marble, Viking, Cassini, Voyager). The processed files are not themselves
public domain; keep this credit if you redistribute them.

The scene samples every map with mipmaps, linear filtering, and the renderer’s anisotropy
limit. Color maps use sRGB. Normal and roughness maps stay linear (`NoColorSpace`).
Longitude 0° is the center of each Scope color map. Detail maps are aligned to that.

| File                   | Pixels      | Body                         | Source                                              |
| ---------------------- | ----------- | ---------------------------- | --------------------------------------------------- |
| `sun.jpg`              | 4096×2048   | Sun                          | `8k_sun.jpg` (highest published file is 4K)        |
| `mercury.jpg`          | 8192×4096   | Mercury                      | `8k_mercury.jpg`                                    |
| `venus.jpg`            | 4096×2048   | Venus cloud tops             | `4k_venus_atmosphere.jpg` (no 8K atmosphere)        |
| `earth_day.jpg`        | 8192×4096   | Earth day                    | `8k_earth_daymap.jpg`                               |
| `earth_clouds.jpg`     | 8192×4096   | Earth clouds                 | `8k_earth_clouds.jpg`                               |
| `earth_night.jpg`      | 8192×4096   | Earth night lights           | `8k_earth_nightmap.jpg`                             |
| `earth_normal.png`     | 8192×4096   | Earth tangent normals        | `8k_earth_normal_map.tif`, saved as PNG             |
| `earth_roughness.png`  | 8192×4096   | Earth roughness              | `8k_earth_specular_map.tif`, see below              |
| `mars.jpg`             | 8192×4096   | Mars                         | `8k_mars.jpg`                                       |
| `mars_normal.png`      | 4096×2048   | Mars tangent normals         | NASA MOLA MEG016, see below                         |
| `jupiter.jpg`          | 4096×2048   | Jupiter                      | `8k_jupiter.jpg` (highest published file is 4K)    |
| `saturn.jpg`           | 4096×2048   | Saturn                       | `8k_saturn.jpg` (highest published file is 4K)     |
| `saturn_ring.png`      | 8192×500    | Saturn rings                 | `8k_saturn_ring_alpha.png`                          |
| `uranus.jpg`           | 2048×1024   | Uranus                       | `2k_uranus.jpg` (no higher Scope map)               |
| `neptune.jpg`          | 2048×1024   | Neptune                      | `2k_neptune.jpg` (no higher Scope map)              |
| `moon.jpg`             | 8192×4096   | Moon                         | `8k_moon.jpg`                                       |
| `moon_normal.png`      | 4096×2048   | Moon tangent normals         | NASA LOLA LDEM_16, see below                        |
| `stars.jpg`            | 8192×4096   | Milky Way starfield          | `8k_stars_milky_way.jpg`                            |

`stars.jpg` is unchanged from the previous showcase step. A thin layer of procedural
point stars is drawn in the scene (not a texture file). The Sun’s corona glow is also
drawn in the scene.

Scope’s download names say `8k_` for the Sun, Jupiter, and Saturn, but those files are
4096×2048. That is the highest resolution the publisher offers for those bodies, so the
showcase uses them as-is. Uranus and Neptune are published only at 2048×1024. Venus’s
cloud map stops at 4096×2048. The whole `textures/` folder is about 90 MB, which keeps
`make build` and the frontend image practical. 8K normal TIFFs are not used directly:
browsers cannot decode TIFF through the texture loader, so they are stored as PNG.

## Earth roughness

`8k_earth_specular_map.tif` is white on water and black on land. The showcase stores the
inverse as roughness: land 0.92, ocean 0.22. Once that map loads, the material roughness
is 1 so the texture is the roughness. Night lights and the cloud layer are unchanged.

## Moon and Mars relief

Solar System Scope does not publish normal maps for the Moon or Mars. These two are
derived here from NASA public-domain elevation grids (no extra license):

- Moon: LOLA Gridded Data Record `ldem_16` (16 pixels per degree, 5760×2880, signed
  16-bit, 0.5 m per DN). PDS Geosciences Node,
  `lro-l-lola-3-rdr-v1` / `lola_gdr/cylindrical/img/ldem_16.img`.
- Mars: MOLA Mission Experiment Gridded Data Record topography `megt90n000eb`
  (16 pixels per degree, 5760×2880, signed 16-bit meters). PDS Geosciences Node,
  `urn-nasa-pds-mgs_mola_topography_derived/meg016/megt90n000eb.img`.

Both grids put longitude 0° on the left edge. They are rolled 180° so longitude 0° sits
in the center, matching the Scope color maps, then resampled to 4096×2048. Tangent
normals use the real body radius. Mars slopes are multiplied by 2 because a 16
pixel-per-degree grid averages canyon walls and volcano scarps down to a few degrees;
the gain keeps Valles Marineris and Olympus Mons readable up close. The Moon is left at
physical slope. The 64 pixel-per-degree grids are hundreds of megabytes and are not in
the repo. NASA SVS hosts the same LOLA elevations, but those file URLs refused this
environment; the PDS copies above are the source actually fetched.

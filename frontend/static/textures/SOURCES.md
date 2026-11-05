# Planet maps

Equirectangular maps in this folder are the 2K Solar System Scope set, used under
[Creative Commons Attribution 4.0](https://creativecommons.org/licenses/by/4.0/).

Credit: Solar System Scope — https://www.solarsystemscope.com/textures/

The maps are processed from public-domain NASA / USGS / JPL imagery (SDO, MESSENGER,
Magellan, Blue Marble, Viking, Cassini, Voyager). The processed files are not themselves
public domain; keep this credit if you redistribute them.

| File               | Body                | Source image                         |
| ------------------ | ------------------- | ------------------------------------ |
| `sun.jpg`          | Sun                 | `2k_sun.jpg`                         |
| `mercury.jpg`      | Mercury             | `2k_mercury.jpg`                     |
| `venus.jpg`        | Venus cloud tops    | `2k_venus_atmosphere.jpg`            |
| `earth_day.jpg`    | Earth day           | `2k_earth_daymap.jpg`                |
| `earth_clouds.jpg` | Earth clouds        | `2k_earth_clouds.jpg`                |
| `earth_night.jpg`  | Earth night lights  | `2k_earth_nightmap.jpg`              |
| `mars.jpg`         | Mars                | `2k_mars.jpg`                        |
| `jupiter.jpg`      | Jupiter             | `2k_jupiter.jpg`                     |
| `saturn.jpg`       | Saturn              | `2k_saturn.jpg`                      |
| `saturn_ring.png`  | Saturn rings        | `2k_saturn_ring_alpha.png`           |
| `uranus.jpg`       | Uranus              | `2k_uranus.jpg`                      |
| `neptune.jpg`      | Neptune             | `2k_neptune.jpg`                     |
| `moon.jpg`         | Moon                | `2k_moon.jpg`                        |
| `stars.jpg`        | Milky Way starfield | `8k_stars_milky_way.jpg` (8192×4096) |

`stars.jpg` is the 8K Milky Way panorama used as the sky background, replacing the 2K map so the band stays sharp at typical camera distances. The scene samples it with mipmaps, linear filtering, and the renderer’s anisotropy limit, on a finer sky sphere. A thin layer of procedural point stars is drawn in the scene (not a texture file) so individual stars stay round instead of becoming texels. `moon.jpg` is the same 2K set.

The Sun’s corona glow is drawn in the scene. It is not a photographed texture.

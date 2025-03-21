# ani2png

ani2png is a Python script the converts Windows animated mouse cursor file (.ani) to a PNG file that usable with Mousecape.

[Mousecape](https://github.com/alexzielenski/Mousecape) is a macOS utility that changes the mouse cursor.
In Mousecape, a cursor theme/package is called a "cape".
While there are many good "capes" out there, they are not as diverse and quirky like Windows cursors.
For example this [Boochi Bocchi the Rock!](https://en.wikipedia.org/wiki/Bocchi_the_Rock!) I purchased from [bilibili](https://www.bilibili.com/video/BV1yjwWeTEtH/?share_source=copy_web&vd_source=171e667bc748e9fa6eceb9695cf79762).

[![Video](https://github.com/user-attachments/assets/b8173d05-f78e-45ab-9a54-3bef651a2e6c)](https://www.bilibili.com/video/BV1yjwWeTEtH/?share_source=copy_web&vd_source=171e667bc748e9fa6eceb9695cf79762)

This script converts Windows `.ani` files to PNGs that can be used with Mousecape.

Specifically, Mousecape expects as tall strip of image with each frame of the animation layed out just like a movie film.

This script does just that. And the output format is PNG.

```
ani2png.py <INPUT_PATH> -o <OUTPUT_PATH>
```

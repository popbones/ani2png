# ani2png

ani2png is a Python script the converts Windows animated mouse cursor file (.ani) to a PNG file that usable with Mousecape.

[Mousecape](https://github.com/alexzielenski/Mousecape) is a macOS utility that changes the mouse cursor.
In Mousecape, a cursor theme/package is called a "cape".
While there are many good "capes" out there, they are not as diverse and quirky like Windows cursors.
For example this [Boochi Bocchi the Rock!](https://en.wikipedia.org/wiki/Bocchi_the_Rock!) I purchased from bilibili.

<iframe src="//player.bilibili.com/player.html?isOutside=true&aid=113861629903212&bvid=BV1yjwWeTEtH&cid=27996260696&p=1" scrolling="no" border="0" frameborder="no" framespacing="0" allowfullscreen="true"></iframe>

This script converts Windows `.ani` files to PNGs that can be used with Mousecape.

Specifically, Mousecape expects as tall strip of image with each frame of the animation layed out just like a movie film.

This script does just that. And the output format is PNG.

```
ani2png.py <INPUT_PATH> -o <OUTPUT_PATH>
```

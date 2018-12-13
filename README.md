This script makes use of two images:

1. A square image (aspect ratio 1:1) that will be used to generate a tile 
   used to form the new image. The tile will be made by converting the image
   to monochrome and then resizing it to the tile size (in pixels) specified
   by the user.

2. An image (typically a well known work of art) with any dimensions that
   will be used to control the tiling of the above image. The user specifies
   a crop of this image by specifying the location of the top left pixel 
   in the crop and the width and height of the crop in pixels. 

The output image will be formed by repeating the tile in the same number 
of rows and columns as the crop. Each tile will be tinted using the colour
of the corresponding pixel in the crop.

It's very unlikely that the brightness of the tile will match the average
brightness of the image and so the result might be lighter or darker tnan
you expect. Use the brightness opton to tweak the brightness of the tile.

You'll need to install Pillow, the maintained fork of PIL:
https://pypi.org/project/Pillow/

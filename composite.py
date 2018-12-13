#!/usr/bin/env python

"""
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


"""
import PIL.Image
import PIL.ImageOps
import PIL.ImageEnhance
import argparse
import os
import sys

def fail(reason):
    print >>sys.stderr, 'error:', reason
    sys.exit(1)


def main():

    parser = argparse.ArgumentParser(description='Form a composite image from a tile driven by artwork')
    parser.add_argument('artwork',      metavar='PATH',                        help='path to image file that will control the output')
    parser.add_argument('tile',         metavar='PATH',                        help='path to image file that will be used as the tile')
    parser.add_argument('--top',        metavar="NUMBER", type=int, default=0, help='The top edge of the image crop, in pixels')
    parser.add_argument('--left',       metavar="NUMBER", type=int, default=0, help='The left edge of the image crop, in pixels')
    parser.add_argument('--width',      metavar="NUMBER", type=int,            help='The width of the image crop, in pixels')
    parser.add_argument('--height',     metavar="NUMBER", type=int,            help='The height of the image crop, in pixels')
    parser.add_argument('--tile-size',  metavar="NUMBER", type=int,            help='Size of the tile, in pixels')
    parser.add_argument('--brightness', metavar="NUMBER", type=int, default=1, help='Enhancement for brightness (0=black, 1=unchanged, ...)')
    parser.add_argument('--verbose',    action='store_true',                   help='Explain whats going on')
     
    args = parser.parse_args()

    # Make sure the arguments given make sense.
    if not os.path.isfile(args.artwork):
        fail('the artwork %s is not a file' % args.artwork)
    if not os.path.isfile(args.tile):
        fail('the tile %s is not a file' % args.tile)
    if args.brightness < 0:
        fail('brightness is less than zero')

    # Now do our best to open the images. We need to do this next so we can check
    # that the crop dimensions make sense if provided and to set them if not.
    artwork_whole = PIL.Image.open(args.artwork)
    tile_colour = PIL.Image.open(args.tile)
    artwork_width, artwork_height = artwork_whole.size
    tile_width, tile_height = tile_colour.size

    if args.verbose:
        print args.artwork, 'is %ux%u' % (artwork_width, artwork_height)
        print args.tile, 'is %ux%u' % (tile_width, tile_height)

    # Fill in the defaults if they were not specified
    if not args.width:
        args.width = artwork_width
    if not args.height:
        args.height = artwork_height
    if not args.tile_size:
        args.tile_size = tile_width

    if args.verbose:
        print 'The crop specified has its topleft at (%u,%u), width %u and height %u' % (args.left, args.top, args.width, args.height)

    if args.left + args.width > artwork_width:
        fail('The crop extends %u pixels past the right edge of the artwork' % (args.left + args.width - artwork_width))
    if args.top + args.height > artwork_height:
        fail('The crop extends %u pixels past the bottom edge of the artwork' % (args.top + args.height - artwork_height))

    if tile_width != tile_height:
        print >>sys.stderr, 'warning: the tile is not square'


    # Generate the initial monochrome tile, resize it to the dimensions 
    # requested and then adjust the brightness as requested.
    tile_mono = PIL.ImageOps.grayscale(tile_colour)
    tile_mono = tile_mono.resize((args.tile_size, args.tile_size))
    tile_mone = PIL.ImageEnhance.Brightness(tile_mono).enhance(args.brightness)

    # Cut out the bit of artwork to generate
    extent = (args.left, args.top, args.left+args.width, args.top+args.height)
    artwork_crop = artwork_whole.crop(extent)

    # Now work out the size of the resulting composite
    composite_width = args.width * args.tile_size
    composite_height = args.height * args.tile_size
    composite_image = PIL.Image.new('RGB', (composite_width, composite_height))

    # We'll need to access all of the pixels
    pixels = artwork_crop.load()

    # Process every pixel in the cropped artwork
    for row in range(args.height):

        if args.verbose: 
            print 'row', row

        for col in range(args.width):

            # We could speed things up by building a map from rgb to tinted tile
            # rather than regerating the tile each time but things seem ok as
            # they are.
            pixel_rgb = pixels[col, row]
            tile_instance = PIL.ImageOps.colorize(tile_mono, (0, 0, 0), pixel_rgb)

            # Place the tinted tile into the output composite
            composite_image.paste(tile_instance, (col*args.tile_size, row*args.tile_size))

    if args.verbose:
        print 'saving', 'composite.%d.jpg' % args.tile_size, 'dimensions %ux%u' % (composite_image.size[0], composite_image.size[1])
    composite_image.save('composite.%d.jpg' % args.tile_size, 'JPEG')


if __name__ == '__main__':
    main()
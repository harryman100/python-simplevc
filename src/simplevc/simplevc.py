'''
Created on 30 Aug 2014

@author: harry <AT> alt-control.net
'''

from PIL import Image
import random, operator
import math

# the second value is the ALPHA, setting it to transparent for blank pixels allows the images to be overlayed in software
BLANKPIXEL = 0xFF, 0x00
FILLEDPIXEL = 0x00, 0xFF

def ceil(f):
    return int(math.ceil(f))

def floor(f):
    return int(math.floor(f))

def mult(tupl, scalar):
    return tuple(map(lambda x: scalar * x, tupl))

def tuple_mult(a, b):
    assert len(a) == len(b)
    return tuple(map(operator.mul, a, b))

def add(tupl, scalar):
    return tuple(map(lambda x: x + scalar, tupl))

def tuple_add(a, b):
    assert len(a) == len(b)
    return tuple(map(operator.add, a, b))

def allPositions(size):
    maxX, maxY = size
    for x in range(0, maxX):
        for y in range(0, maxY):
            yield (x, y)


def allZeroCentrePositions(size):
    halfX = size[0] / 2.0
    halfY = size[1] / 2.0
    for x in range(-1 * floor(halfX), ceil(halfX)):
        for y in range(-1 * floor(halfY), ceil(halfY)):
            yield (x, y)

def padPositions(padCentrePoint, padSize):
    for offset in allZeroCentrePositions(padSize):
        yield tuple_add(padCentrePoint, offset)

def padCentre(sourcePosition, padSize):
    return tuple(map(floor, tuple_add(tuple_mult(sourcePosition, padSize), mult(padSize, 0.5))))

def randomHalfOf(vals):
    return random.sample(vals, int(len(vals) / 2))

def generateKeySetPositions(sourceSize, padSize):
    for sourcePosition in allPositions(sourceSize):
        pad = padCentre(sourcePosition, padSize)
        allPadPositions = list(padPositions(pad, padSize))
        for padPos in randomHalfOf(allPadPositions):
            yield padPos

def createKeyImage(sourceSize, padsize):
    keyIm = Image.new('LA', tuple_mult(sourceSize, padsize), BLANKPIXEL)
    for pos in generateKeySetPositions(sourceSize, padsize):
        keyIm.putpixel(pos, FILLEDPIXEL)
    return keyIm

def isPixelSet(pixelValue):
    return pixelValue > 0x00

def invertPixel(im, pos):
    im.putpixel(pos, add(mult(im.getpixel(pos), -1), 0xFF))

def invertPad(cipherIm, padCentre, padSize):
    for padPos in padPositions(padCentre, padSize):
        invertPixel(cipherIm, padPos)

def getSetPixels(image):
    for position in allPositions(image.size):
        if isPixelSet(image.getpixel(position)):
            yield position

def createCipherImage(keyIm, plainIm, padSize):
    assert keyIm.size == tuple_mult(plainIm.size, padSize)
    assert plainIm.mode == 'L'
    assert keyIm.mode == 'LA'
    cipherIm = keyIm.copy()
    for position in getSetPixels(plainIm):
        pad = padCentre(position, padSize)
        invertPad(cipherIm, pad, padSize)
    return cipherIm

def createKeyAndCipher(inputImageFilename, outputFormat, keyFilename, cipherFilename, padSize=(3, 3)):
    """
    Creates a key/cipher pair which when combined produce a representation of the original image.
    
    The input image should be black and white (not greyscale).
    The dimensions of the output images will be the dimensions of the input image,
    multiplied by the padSize.    
    """
    plainIm = Image.open(inputImageFilename).convert(mode='L')
    keyIm = createKeyImage(plainIm.size, padSize)
    keyIm.save(keyFilename, outputFormat)
    cipherIm = createCipherImage(keyIm, plainIm, padSize)
    cipherIm.save(cipherFilename, outputFormat)

if __name__ == '__main__':
    createKeyAndCipher("exampleinput.png", "PNG", "examplekey.png", "examplecipher.png", (3, 3))


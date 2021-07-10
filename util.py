
from PIL import Image, ImageFont, ImageDraw

import cv2
import numpy as np

def breakWrappedText(text, font, lineLength):
    words = text.split(' ')
    curLine = ''
    allLines = []
    for word in words:
        if len(curLine) == 0:
            newLine = word
        else:
            newLine = curLine + ' ' + word
        if font.getlength(newLine) >= lineLength:
            allLines.append(curLine)
            curLine = word
        else:
            curLine = newLine
    allLines.append(curLine)
    return allLines
    
    """for word in text.split():
        line = f'{lines[-1]} {word}'.strip()
        if font.getlength(text) <= lineLength:
            lines[-1] = line
        else:
            lines.append(word)
    return lines
    #return '\n'.join(lines)"""

"""def drawWrappedText2(image, text, font, text_color, text_start_height):
    draw = ImageDraw.Draw(image)
    image_width, image_height = image.size
    y_text = text_start_height
    lines = textwrap.wrap(text, width=40)
    for line in lines:
        line_width, line_height = font.getsize(line)
        draw.text(((image_width - line_width) / 2, y_text), 
                  line, font=font, fill=text_color)
        y_text += line_height"""

def drawWrappedText(allText, font, fullWidth, fullHeight, leftPad, rightPad):
    width = fullWidth - leftPad - rightPad
    image = Image.new("RGBA", (width, fullHeight), (255,255,255,255))
    draw = ImageDraw.Draw(image)

    lines = breakWrappedText(allText, font, width)
    yOffset = 0
    for line in lines:
        lineWidth, lineHeight = font.getsize(line)
        draw.text(((width - lineWidth) / 2, yOffset), 
                  line, font=font, fill=(0,0,0,255))
        yOffset += lineHeight

    #draw.rectangle([(0, 0), (width, height)], fill=(128,128,128,255))
    #draw.text((10, 0), text, (0,0,0,255), font=font)
    #img_resized = image.resize((188,45), Image.ANTIALIAS)
    result = np.array(image)[:,:,0:3] / 255.0
    result = np.pad(result, ((0, 0), (leftPad, rightPad), (0, 0)), constant_values=1.0)
    return result

def saveNPYImg(filename, img):
    img = (img * 255.0).astype(np.uint8)
    cv2.imwrite(filename, img)

def linearMap(x, minValIn, maxValIn, minValOut, maxValOut):
    return ((x - minValIn) * (maxValOut - minValOut) / (maxValIn - minValIn) + minValOut)

def printArrayStats(x, name):
    print(name, x.shape, x.dtype, 'range=[', np.amin(x), ', ', np.amax(x), ']')
    
def makeGrayscale(img):
    if len(img.shape) == 2:
        return img
    if img.shape[2] == 1:
        return img[:,:,0]
    imgMax = np.max(img, axis=2)
    imgMin = np.min(img, axis=2)
    return (imgMax + imgMin) / 2.0 # 'L' in HSL

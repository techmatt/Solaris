
from PIL import Image, ImageFont, ImageDraw
import numpy as np

import util

#full image: (666,906)
#half image: (666, 453)
#half image: (2664, 1812)

class Opt:
    def __init__(self):
        self.fontTitle = ImageFont.truetype("fonts/CenturyGothicBold.ttf", 100)
        self.fontDesc = ImageFont.truetype("fonts/futura.ttf", 80)
        self.pageWidth = 2664
        self.pageHeight = 1812

class SpellList:
    def __init__(self):
        self.spells = []
        self.spells.append(self.makeSpell())

    def makeSpell(self):
        result = {}
        result['name'] = 'Fireball'
        result['description'] = 'Casts fireball!'
        result['r'] = 1
        result['y'] = 1
        result['g'] = 1
        result['b'] = 1
        result['v'] = 1
        result['gray'] = 1
        result['w'] = 1
        return result


def makeSpellPage(opt, spell):
    result = np.ones([opt.pageHeight, opt.pageWidth, 3], dtype=np.float32)

    titleStart = int(opt.pageHeight * 0.05)
    titleHeight = int(opt.pageHeight * 0.1)

    titleImg = util.drawWrappedText(spell['name'], opt.fontTitle, opt.pageWidth, titleHeight, int(opt.pageWidth * 0.1), int(opt.pageWidth * 0.1))
    
    util.printArrayStats(result, 'result')
    util.printArrayStats(titleImg, 'titleImg')

    result[titleStart:titleStart + titleHeight] = titleImg[:]
    util.saveNPYImg('result.png', result)

def convertAll():
    opt = Opt()
    spellList = SpellList()

    makeSpellPage(opt, spellList.spells[0])
    
    #img = util.drawWrappedText('this is a really long string. this is a really long string. this is a really long string. this is a really long string. this is a really long string. this is a really long string. this is a really long string. this is a really long string.', fontTitle, 1024)
    #util.printArrayStats(img, 'img')
    #util.saveNPYImg('debug.png', img)

convertAll()
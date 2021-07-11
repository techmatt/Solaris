
from functools import cmp_to_key
from PIL import Image, ImageFont, ImageDraw
import numpy as np
from math import pow

import util

#full image: (666,906)
#half image: (666, 453)
#half image: (2664, 1812)

def scoreSpell(a, weights):
    return a['r'] * pow(10.0, weights[0]) + \
           a['y'] * pow(10.0, weights[1]) + \
           a['g'] * pow(10.0, weights[2]) + \
           a['b'] * pow(10.0, weights[3]) + \
           a['v'] * pow(10.0, weights[4]) + \
           a['w'] * pow(10.0, weights[5]) + \
           a['gray'] * pow(10.0, weights[6])

def anySort(a, b, weights):
    aScore = scoreSpell(a, weights)
    bScore = scoreSpell(b, weights)
    if aScore > bScore:
        return 1
    elif aScore == bScore:
        return 0
    else:
        return -1

def rSort(a, b):
    return anySort(a, b, [7, 6, 5, 4, 3, 2, 1])

def ySort(a, b):
    return anySort(a, b, [7, 6, 5, 4, 3, 2, 1])

def gSort(a, b):
    return anySort(a, b, [7, 6, 5, 4, 3, 2, 1])

def bSort(a, b):
    return anySort(a, b, [7, 6, 5, 4, 3, 2, 1])

def vSort(a, b):
    return anySort(a, b, [7, 6, 5, 4, 3, 2, 1])

def wSort(a, b):
    return anySort(a, b, [7, 6, 5, 4, 3, 2, 1])

def getCompareKey(s):
    if s == 'r':
        return cmp_to_key(rSort)
    elif s == 'y':
        return cmp_to_key(ySort)
    elif s == 'g':
        return cmp_to_key(gSort)
    elif s == 'b':
        return cmp_to_key(bSort)
    elif s == 'v':
        return cmp_to_key(vSort)
    elif s == 'w':
        return cmp_to_key(wSort)
    return None

class Opt:
    def __init__(self):
        self.fontTitle = ImageFont.truetype("fonts/CenturyGothicBold.ttf", 200)
        self.fontDesc = ImageFont.truetype("fonts/futura.ttf", 100)
        self.pageWidth = 2664
        self.pageHeight = 1812
        self.gemImgs = {}
        self.gemImgSize = [200, 200]
        self.gemImgs['r'] = util.loadImg('images/red.png', self.gemImgSize)
        self.gemImgs['y'] = util.loadImg('images/yellow.png', self.gemImgSize)
        self.gemImgs['g'] = util.loadImg('images/green.png', self.gemImgSize)
        self.gemImgs['b'] = util.loadImg('images/blue.png', self.gemImgSize)
        self.gemImgs['v'] = util.loadImg('images/violet.png', self.gemImgSize)
        self.gemImgs['gray'] = util.loadImg('images/gray.png', self.gemImgSize)
        self.gemImgs['w'] = util.loadImg('images/white.png', self.gemImgSize)

class SpellList:
    def __init__(self, filename):
        self.spells = []
        self.spellbooks = {}

        spellbookChars = ['r', 'y', 'g', 'b', 'v', 'w']
        for c in spellbookChars:
            self.spellbooks[c] = []
        
        with open(filename) as f:
            spellLines = f.readlines()
        spellLines = [x.strip() for x in spellLines]
        for line in spellLines:
            spell = self.makeSpell(line)
            self.spells.append(spell)
            for c in spellbookChars:
                if spell[c] > 0:
                    self.spellbooks[c].append(spell)

        for c in spellbookChars:
            self.spellbooks[c].sort(key=getCompareKey(c))

        #self.spells.append(self.makeSpell())
        
    def makeSpell(self, line):
        parts = line.split('\t')
        if len(parts) != 9:
            print('unexpected line: ' + line)
            return None
        
        def readInt(s):
            if len(s) == 0:
                return 0
            else:
                return int(s)
        result = {}
        result['name'] = parts[0].title()
        result['gray'] = readInt(parts[1])
        result['r'] = readInt(parts[2])
        result['y'] = readInt(parts[3])
        result['g'] = readInt(parts[4])
        result['b'] = readInt(parts[5])
        result['v'] = readInt(parts[6])
        result['w'] = readInt(parts[7])
        result['desc'] = parts[8]
        return result

def makeSpellImg(opt, spell, fullWidth, leftPad, rightPad):
    allImgs = []
    for gem in ['w', 'r', 'y', 'g', 'b', 'v', 'gray']:
        for x in range(0, spell[gem]):
            allImgs.append(opt.gemImgs[gem])
    result = np.concatenate(allImgs, axis=1)
    centerWidth = fullWidth - leftPad - rightPad
    centerPadL = (centerWidth - result.shape[1]) // 2
    centerPadR = centerWidth - result.shape[1] - centerPadL
    result = np.pad(result, ((0, 0), (centerPadL, centerPadR), (0, 0)), constant_values=1.0)
    result = np.pad(result, ((0, 0), (leftPad, rightPad), (0, 0)), constant_values=1.0)
    return result

def makeSpellPage(opt, spell):
    result = np.ones([opt.pageHeight, opt.pageWidth, 3], dtype=np.float32)

    titleStart = int(opt.pageHeight * 0.05)
    titleHeight = int(opt.pageHeight * 0.2)

    spellStart = int(opt.pageHeight * 0.2)
    spellHeight = opt.gemImgSize[0]
    
    descStart = int(opt.pageHeight * 0.37)
    descHeight = int(opt.pageHeight * 0.55)
    
    leftPad = int(opt.pageWidth * 0.2)
    rightPad = int(opt.pageWidth * 0.1)

    spellImg = makeSpellImg(opt, spell, opt.pageWidth, leftPad, rightPad)
    titleImg = util.drawWrappedText(spell['name'], opt.fontTitle, opt.pageWidth, titleHeight, leftPad, rightPad)
    descImg = util.drawWrappedText(spell['desc'], opt.fontDesc, opt.pageWidth, descHeight, leftPad, rightPad)
    
    #util.printArrayStats(result, 'result')
    #util.printArrayStats(titleImg, 'titleImg')

    result[titleStart:titleStart + titleHeight] = titleImg[:]
    result[spellStart:spellStart + spellHeight] = spellImg[:]
    result[descStart:descStart + descHeight] = descImg[:]

    util.saveNPYImg('spell.png', spellImg)
    util.saveNPYImg('result.png', result)

def convertAll():
    opt = Opt()
    spellList = SpellList('spells.txt')

    makeSpellPage(opt, spellList.spells[0])
    
    #img = util.drawWrappedText('this is a really long string. this is a really long string. this is a really long string. this is a really long string. this is a really long string. this is a really long string. this is a really long string. this is a really long string.', fontTitle, 1024)
    #util.printArrayStats(img, 'img')
    #util.saveNPYImg('debug.png', img)

convertAll()
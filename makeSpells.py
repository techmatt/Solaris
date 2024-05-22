
import os
from functools import cmp_to_key
from PIL import Image, ImageFont, ImageDraw
from fpdf import FPDF
import numpy as np
from math import pow

import util
import cv2

#full image: (666,906)
#half image: (666, 453)
#half image: (2664, 1812)

lookupDict = {'r': 'Red', 'y' : 'Yellow', 'g': 'Green',
              'b': 'Blue', 'v' : 'Violet', 'w': 'White'}
    
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
    return anySort(a, b, [6, 7, 5, 4, 3, 2, 1])

def gSort(a, b):
    return anySort(a, b, [5, 6, 7, 4, 3, 2, 1])

def bSort(a, b):
    return anySort(a, b, [4, 6, 5, 7, 3, 2, 1])

def vSort(a, b):
    return anySort(a, b, [3, 6, 5, 4, 7, 2, 1])

def wSort(a, b):
    return anySort(a, b, [2, 6, 5, 4, 3, 7, 1])

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
        self.fontDesc = ImageFont.truetype("fonts/futura.ttf", 80)
        self.bookTitle = ImageFont.truetype("fonts/FlareGothic.ttf", 200)
        self.fontPage = ImageFont.truetype("fonts/CenturyGothicBold.ttf", 140)
        self.fontAnom = ImageFont.truetype("fonts/futura.ttf", 80)
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
        line = line.replace('  ', ' ')
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
        result['desc'] = parts[8].replace('  ', ' ')
        return result

def resizeImgStd(img, newSize):
    result = cv2.resize(img, dsize=(newSize[1], newSize[0]), interpolation=cv2.INTER_LANCZOS4) #cv2.INTER_AREA
    result = np.clip(result, 0.0, 1.0)
    return result

def makeSpellImg(opt, spell, fullWidth, height, leftPad, rightPad):
    allImgs = []
    for gem in ['w', 'r', 'y', 'g', 'b', 'v', 'gray']:
        for x in range(0, spell[gem]):
            gemImg = opt.gemImgs[gem]
            gemImg = resizeImgStd(gemImg, [height, height])
            allImgs.append(gemImg)
    result = np.concatenate(allImgs, axis=1)
    return makeSpellImgFinal(result, fullWidth, leftPad, rightPad)
    
def makeSpellImgBookTitle(opt, gem, gemShape, fullWidth, leftPad, rightPad):
    gemImg = opt.gemImgs[gem]
    gemImg = cv2.resize(gemImg, dsize=(gemShape, gemShape), interpolation=cv2.INTER_LANCZOS4) #cv2.INTER_AREA
    gemImg = np.clip(gemImg, 0.0, 1.0)
    return makeSpellImgFinal(gemImg, fullWidth, leftPad, rightPad)

def makeSpellImgFinal(imgBase, fullWidth, leftPad, rightPad):
    if imgBase.shape[1] > fullWidth:
        imgBase = resizeImgStd(imgBase, [imgBase.shape[0], fullWidth])

    centerWidth = fullWidth - leftPad - rightPad
    centerPadL = (centerWidth - imgBase.shape[1]) // 2
    centerPadR = centerWidth - imgBase.shape[1] - centerPadL
    result = np.pad(imgBase, ((0, 0), (centerPadL, centerPadR), (0, 0)), constant_values=1.0)
    result = np.pad(result, ((0, 0), (leftPad, rightPad), (0, 0)), constant_values=1.0)
    return result

def makeSpellbookTitle(opt, spellbookChar):
    title = 'The ' + lookupDict[spellbookChar] + ' Grimoire'

    result = np.ones([opt.pageHeight, opt.pageWidth, 3], dtype=np.float32)

    gemStart = int(opt.pageHeight * 0.15)
    gemHeight = int(opt.pageHeight * 0.45)

    titleStart = int(opt.pageHeight * 0.65)
    titleHeight = int(opt.pageHeight * 0.2)

    leftPad = int(opt.pageWidth * 0.2)
    rightPad = int(opt.pageWidth * 0.1)

    gemImg = makeSpellImgBookTitle(opt, spellbookChar, gemHeight, opt.pageWidth, leftPad, rightPad)
    titleImg = util.drawWrappedText(title, opt.bookTitle, opt.pageWidth, titleHeight, leftPad, rightPad)
    
    result[gemStart:gemStart + gemHeight] = gemImg[:]
    result[titleStart:titleStart + titleHeight] = titleImg[:]
    
    return result

def makeSpellbookTOC(opt, spellbook):
    result = np.ones([opt.pageHeight, opt.pageWidth, 3], dtype=np.float32)

    #leftPad = int(opt.pageWidth * 0.2)
    #rightPad = int(opt.pageWidth * 0.1)
    
    tablePadding = 5

    columnWidth = int(opt.pageWidth * 0.45)
    entryHeight = int(opt.gemImgSize[0] * 0.8)

    columnStartsX = [int(opt.pageWidth * 0.1), int(opt.pageWidth * 0.55)]

    spellIdx = 0
    for columnIdx in range(0, 2):
        for rowIdx in range(0, 10):
            if spellIdx >= len(spellbook):
                continue

            spell = spellbook[spellIdx]
            spellImg = makeSpellImg(opt, spell, columnWidth, entryHeight, 0, 0)

            entryStartY = int(opt.pageHeight * 0.05 + rowIdx * (entryHeight + tablePadding))
            columnStartX = columnStartsX[columnIdx]
            
            result[entryStartY:entryStartY + entryHeight, columnStartX:columnStartX + columnWidth] = spellImg[:]

            pageIdxWidth = int(0.1 * opt.pageWidth)
            pageStartX = columnStartX + int(0.35 * opt.pageWidth)
            pageImg = util.drawWrappedText(str(spellIdx + 2), opt.fontPage, pageIdxWidth, entryHeight, 0, 0)
            result[entryStartY:entryStartY + entryHeight,pageStartX:pageStartX + pageIdxWidth] = \
                alphaMask(pageImg[:], result[entryStartY:entryStartY + entryHeight,pageStartX:pageStartX + pageIdxWidth])

            spellIdx += 1

    result[:, columnStartsX[1] - 10:columnStartsX[1]] = 0.0

    anomX = int(0.57 * opt.pageWidth)
    anomY = int(0.5 * opt.pageHeight)
    anomWidth  = int(0.4 * opt.pageWidth)
    anomHeight = int(0.5 * opt.pageHeight)
    anomalyText = "If you try to cast a spell not on this list, you instead trigger an anomaly. " \
                  "For the next minute, all casters must walk heel-to-toe and cannot meditate or cast spells."
    anomalyImg = util.drawWrappedText(anomalyText, opt.fontAnom, anomWidth, anomHeight, 0, 0)
    result[anomY:anomY + anomHeight,anomX:anomX + anomWidth] = \
                alphaMask(anomalyImg[:], result[anomY:anomY + anomHeight,anomX:anomX + anomWidth])
    
    return result

def alphaMask(imgOver, imgUnder):
    imgAlpha = (imgOver[:,:,0:1] + imgOver[:,:,1:2] + imgOver[:,:,2:3]) / 3.0
    return imgUnder * imgAlpha + imgOver * (1.0 - imgAlpha)

def makeSpellPage(opt, spell, pageIdx):
    result = np.ones([opt.pageHeight, opt.pageWidth, 3], dtype=np.float32)

    titleStart = int(opt.pageHeight * 0.05)
    titleHeight = int(opt.pageHeight * 0.2)

    spellStart = int(opt.pageHeight * 0.2)
    spellHeight = opt.gemImgSize[0]
    
    descStart = int(opt.pageHeight * 0.37)
    descHeight = int(opt.pageHeight * 0.55)
    
    leftPad = int(opt.pageWidth * 0.2)
    rightPad = int(opt.pageWidth * 0.1)

    spellImg = makeSpellImg(opt, spell, opt.pageWidth, opt.gemImgSize[0], leftPad, rightPad)
    titleImg = util.drawWrappedText(spell['name'], opt.fontTitle, opt.pageWidth, titleHeight, leftPad, rightPad)
    descImg = util.drawWrappedText(spell['desc'], opt.fontDesc, opt.pageWidth, descHeight, leftPad, rightPad)
    
    pageIdxWidth = int(0.1 * opt.pageWidth)
    pageIdxHeight = int(0.1 * opt.pageHeight)
    pageIdxStartX = int(0.9 * opt.pageWidth)
    pageIdxStartY = int(0.85 * opt.pageHeight)
    pageImg = util.drawWrappedText(str(pageIdx), opt.fontPage, pageIdxWidth, pageIdxHeight, 0, 0)
    
    #util.printArrayStats(result, 'result')
    #util.printArrayStats(titleImg, 'titleImg')

    result[titleStart:titleStart + titleHeight] = titleImg[:]
    result[spellStart:spellStart + spellHeight] = spellImg[:]
    result[descStart:descStart + descHeight] = descImg[:]
    result[pageIdxStartY:pageIdxStartY + pageIdxHeight,pageIdxStartX:pageIdxStartX + pageIdxWidth] = \
        alphaMask(pageImg[:], result[pageIdxStartY:pageIdxStartY + pageIdxHeight,pageIdxStartX:pageIdxStartX + pageIdxWidth])

    return result
    #util.saveNPYImg('spell.png', spellImg)
    #util.saveNPYImg('result.png', result)

def makeSpellbookImages(opt, spellbookChar, spellbook):
    baseDir = 'spellbooks/' + spellbookChar + '/'
    os.makedirs(baseDir, exist_ok=True)

    titleImg = makeSpellbookTitle(opt, spellbookChar)
    TOCImg = makeSpellbookTOC(opt, spellbook)

    util.saveNPYImgDouble(baseDir + '0.png', titleImg)
    util.saveNPYImgDouble(baseDir + '1.png', TOCImg)

    pageIdx = 2
    for spellIdx in range(0, len(spellbook)):
        spell = spellbook[spellIdx]
        print('saving ' + spellbookChar + ' ' + str(pageIdx))
        img = makeSpellPage(opt, spell, spellIdx+2)
        util.saveNPYImgDouble(baseDir + str(pageIdx) + '.png', img)
        pageIdx += 1

    pdf = FPDF()
    for idx in range(0, pageIdx):
        pdf.add_page()
        #a4 letter size in mm: 210 x 297 mm
        pdf.image(baseDir + str(idx) + '.png', 0, 0, 210, 297)
    #pdf.output(baseDir + str(spellbookChar) + ".pdf", "F")
    title = 'The ' + lookupDict[spellbookChar] + ' Grimoire'
    pdf.output('spellbooks/' + title + ".pdf", "F")


def convertAll():
    opt = Opt()
    spellList = SpellList('spells.txt')


    for spellChar in spellList.spellbooks:
        makeSpellbookImages(opt, spellChar, spellList.spellbooks[spellChar])

    #makeSpellPage(opt, spellList.spells[0])
    
    #img = util.drawWrappedText('this is a really long string. this is a really long string. this is a really long string. this is a really long string. this is a really long string. this is a really long string. this is a really long string. this is a really long string.', fontTitle, 1024)
    #util.printArrayStats(img, 'img')
    #util.saveNPYImg('debug.png', img)

convertAll()
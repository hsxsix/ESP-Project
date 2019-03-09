# -*- coding: utf-8 -*-

import os
from PIL import Image, ImageFont, ImageDraw



def text2img(text, imageSize="128x96" ,font="simsun.ttc", textSize=16, position=(0,32),
                bgImage=None, bgColor="#00FF00", autoLF=True, outFile='t.png'):
    if bgImage:
        im = Image.open(bgImage)
    else:
        try:
            weight, height = map(lambda x:int(x), imageSize.upper().split('X'))
        except:
            print('imageSize 参数格式不正确！')
            exit()
        
        im = Image.new("RGB", (weight, height), (0, 0, 0))
        dr = ImageDraw.Draw(im)
        try:
            font = ImageFont.truetype(font, textSize)
        except Exception as e:
            print("font 错误！",e)
            exit()

        if autoLF:
            line_word_num = weight//textSize 
            rows = len(text)//line_word_num + 1
            max_rows = height//textSize 
            if rows>max_rows:
                print("某些字可能显示不完全，请适当缩减字数！")
            auto_text_list = [text[r:r+line_word_num] for r in range(0, len(text),line_word_num)]
            text = '\n'.join(auto_text_list)
            print(text)
        dr.text(position, text, font=font, fill=bgColor)
        im.show()
        im.save(outFile)

if __name__ == "__main__":
    string = input("请输入：")
    text2img(text=string)

#!/usr/bin/env python
# -*- coding: UTF-8 -*-
'''
@Project ：python-note 
@File    ：process_png.py
@IDE     ：PyCharm 
@Author  ：wly
@Date    ：2025/10/18 1:39 
@Description: 
'''
import os
from PIL import Image


def fix_image_srgb_profile(file_path):
    img = Image.open(file_path)
    img.save(file_path, icc_profile=None)

pics = os.listdir('pics')
for pic in pics:
    fix_image_srgb_profile(f'pics/{pic}')
    print(f'{pic} done')

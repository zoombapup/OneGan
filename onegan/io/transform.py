# Copyright (c) 2017 Salas Lin (leVirve)
#
# This software is released under the MIT License.
# https://opensource.org/licenses/MIT

import random

import torch
import numpy as np
import torchvision.transforms as F
from PIL import Image


class SegmentationPair():

    def __init__(self,
                 target_size=None,
                 final_transform=False,
                 random_flip=False, random_crop=False):
        self.target_size = target_size
        self.final_transform = final_transform
        self.random_flip = random_flip
        self.random_crop = random_crop

    def __call__(self, image, segmentation, random=False) -> tuple:
        image = image.convert('RGB')
        segment = segmentation.convert('L')

        image, segment = self.random_flip(image, segment)
        image, segment = self.random_crop(image, segment)

        image = F.resize(image, self.target_size, interpolation=Image.BILINEAR)
        segment = F.resize(segment, self.target_size, interpolation=Image.NEAREST)

        return self._transform(image, segment)

    def _transform(self, image, segmentation) -> tuple:
        if self.final_transform:
            image = F.Normalize(mean=[.5, .5, .5], std=[.5, .5, .5])(F.to_tensor(image))
            segmentation = torch.from_numpy(np.array(segmentation)).long()
        return image, segmentation

    def random_flip(self, image, segment):
        if self.random_flip and random.random() >= 0.5:
            image = F.hflip(image)
            segment = F.hflip(segment)
        return image, segment

    def random_crop(self, image, segment):
        if self.random_crop:
            i, j, h, w = F.RandomResizedCrop.get_params(image)
            image = F.crop(image, i, j, h, w)
            segment = F.crop(segment, i, j, h, w)
        return image, segment

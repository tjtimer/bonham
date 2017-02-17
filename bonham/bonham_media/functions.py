from uuid import uuid4

import os
from PIL import Image as pil, ImageOps as img_ops

from bonham.settings import IMAGE_VARIANTS


async def get_resized_image(img, size):
    """ returns an resized image, where the longer side is scaled to given size"""
    x = float(img.size[0])
    y = float(img.size[1])
    as_ro = float(x / y)
    print(x, y, as_ro)
    if as_ro >= 1:
        resize_factor = float(float(size) / x)
        new_width = int(size)
        new_height = int(y * resize_factor)
        size = [new_width, new_height]
    else:
        resize_factor = float(float(size) / y)
        new_height = int(size)
        new_width = int(x * resize_factor)
        size = [new_width, new_height]
    return img.resize(size, pil.LANCZOS)


async def get_thumbnail(img, size, crop_center):
    return img_ops.fit(img, (size, size), method=pil.LANCZOS, centering=crop_center)


async def process_image(image_data, name, root_folder, *, crop_center=None, **kwargs):
    with pil.open(image_data) as pic:
        if name is None:
            name = uuid4().str
        filename = f"{''.join(name.split('.')[:-1])}.{pic.format.lower()}"
        if crop_center is None:
            crop_center = (0.5, 0.5)
        for sub, size in IMAGE_VARIANTS.items():
            img = pic.copy()
            directory = os.path.join(root_folder, sub)
            if not os.path.exists(directory):
                os.makedirs(directory)
            if 'orig' in sub:
                img.save(os.path.join(directory, filename))
            elif sub in 'm l xl':
                img = await get_resized_image(img, size)
            else:
                img = await get_thumbnail(img, size, crop_center)
            img.save(os.path.join(directory, filename))
    return filename

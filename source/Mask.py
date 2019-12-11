import numpy as np
from skimage import measure

"""
flips range and converts t.l.w.h to l.t.w.h
"""
def flipBox(box):
    return [box[1], box[0], box[2], box[3]]

"""
Convert points to indices and swaps x, and y.
"""
def pointsToIndices(points):
    points = np.swapaxes(points, 0, 1).astype(int)
    points[[0, 1],:] = points[[1, 0],:]

"""
returns (mask, bbox) where bbox is the union and mask is set to 0
"""
def jointMask(box0, box1):
    box = np.array([
        min(box0[0], box1[0]),
        min(box0[1], box1[1]),
        max(box0[0] + box0[2], box1[0] + box1[2]),
        max(box0[1] + box0[3], box1[1] + box1[3])
    ])
    box[2] -= box[0]
    box[3] -= box[1]

    mask = np.zeros((box[3], box[2])).astype(np.bool_)
    return (mask, box)


"""
set the mask values to 'value' where the points (translated by bbox left,top) 
"""
def paintPoints(mask, box, points, value):
    h = mask.shape[0]
    w = mask.shape[1]
    points = points - [box[0], box[1]]

    points = points[:, (points[1] > 0) & (points[0] > 0) & (points[1] < w - 1) & (points[0] < h - 1)]
    index = points[0,] * w + points[1,]

    for x in range(-1, 2):
        for y in range(-1, 2):
            np.put(mask, index + y * w + x, value, 'clip')


"""
paints the foreground of the mask as 'value' on the mask. dmask is the destination larger and contains smask
"""
def paintMask(dmask, dbox, smask, sbox, value):
    box = [sbox[0] - dbox[0], sbox[1] - dbox[1], sbox[2], sbox[3]]
    g = dmask[box[1]:box[1] + box[3], box[0]:box[0] + box[2]]

    if value == 0:
        g[:] = g & ~smask
    else:
        g[:] = g | smask

"""
Cut a mask using a set of points
"""
def cut(mask, box, points):
    box = flipBox(box)
    mask = mask > 0
    paintPoints(mask, box, points, 0)
    #regions = measure.regionprops(measure.label(mask))
    return (mask, flipBox(box))


"""
Merge two masks.
"""
def union(maskA, boxA, maskB, boxB):
    boxA = flipBox(boxA)
    boxB = flipBox(boxB)

    (mask, box) = jointMask(boxA, boxB)
    paintMask(mask, box, maskA, boxA, 1)
    paintMask(mask, box, maskB, boxB, 1)

    #regions = measure.regionprops(measure.label(mask))
    return (mask, flipBox(box))

"""
Subtracts the second mask from the first mask
"""
def subtract(maskA, boxA, maskB, boxB):
    boxA = flipBox(boxA)
    boxB = flipBox(boxB)

    (mask, box) = jointMask(boxA, boxB)
    paintMask(mask, box, maskA, boxA, 1)
    paintMask(mask, box, maskB, boxB, 0)

    regions = measure.regionprops(measure.label(mask))
    return (mask, flipBox(box))
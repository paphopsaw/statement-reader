import easyocr
import re
import numpy as np
import pandas as pd
import sys

from typing import List

reader = easyocr.Reader(['ja','en'])

image_file = sys.argv[1:][0]
print('apply ocr')
boxes = reader.readtext(image_file)
reader = easyocr.Reader(['ja','en'])

pattern = r'\d{2}\.\d{2}\.\d{2}'
amount_boxes = []
date_boxes = []
for box in boxes:
    text = box[1]
    if '円' in text:
        amount_boxes.append(box)
    if re.match(pattern, text):
        date_boxes.append(box)

def box_height(box):
    points = box[0]
    min_y = min(points, key=lambda x: x[1])[1]
    max_y = max(points, key=lambda x: x[1])[1]
    return max_y - min_y

def median_height(boxes):
    heights = np.array(list(map(box_height, boxes)))
    return np.median(heights)

# remove large amount box (box that's much bigger or smaller than median +-20%)
def remove_height_outliers(boxes):
    height_diff_threshold = 0.2
    median = median_height(boxes)
    new_boxes = []
    for box in boxes:
        if abs(box_height(box) - median) / median < height_diff_threshold:
            new_boxes.append(box)
    return new_boxes

amount_boxes = remove_height_outliers(amount_boxes)

def simplify_box(box):
    points = box[0]
    text = box[1]
    min_x = min(points, key=lambda x: x[0])[0]
    min_y = min(points, key=lambda x: x[1])[1]
    return (min_x, min_y, text)

def sort_and_simplify_boxes(boxes):
    return sorted(list(map(simplify_box, boxes)), key=lambda x: x[1])


def get_title(xy_amount_box, xy_date_box, boxes):
    amount_box_x = xy_amount_box[0]
    amount_box_y = xy_amount_box[1]
    date_box_y = xy_date_box[1]
    title_boxes = []
    for box in boxes:
        if is_title_box(box, amount_box_x, amount_box_y, date_box_y):
            title_boxes.append(box)
    return merge_title_boxes(title_boxes)


def is_title_box(box, amount_box_x, amount_box_y, date_box_y):
    points = box[0]
    box_x_right = max(points, key=lambda x: x[0])[0]
    box_y_bottom = max(points, key=lambda x: x[1])[1]
    if (box_x_right < amount_box_x) and (box_y_bottom > amount_box_y) and (box_y_bottom < date_box_y):
        return True
    return False

def merge_title_boxes(title_boxes):
    title = ""
    #TODO:sort left-right top-bottom
    for title_box in title_boxes:
        title += title_box[1]
    return title

xy_date_boxes = sort_and_simplify_boxes(date_boxes)
xy_amount_boxes = sort_and_simplify_boxes(amount_boxes)
# Amount must be on top, if there's date on top, remove it.
if xy_date_boxes[0] > xy_amount_boxes[0]:
    xy_date_boxes = xy_date_boxes[1:]
# If there's no date matching, remove last amount.
entry_count = min(len(xy_amount_boxes), len(xy_date_boxes))

data = []
for i in range(entry_count):
    xy_amount_box = xy_amount_boxes[i]
    xy_date_box = xy_date_boxes[i]
    amount = xy_amount_box[2].replace('円', '').strip()
    date = xy_date_box[2].replace('.', '/')
    title = get_title(xy_amount_box, xy_date_box, boxes)
    print(date, title, amount)
    data.append((date, title, amount))
pd.DataFrame(data).to_clipboard(index=False, header=None)
print('Data copied to clipboard')
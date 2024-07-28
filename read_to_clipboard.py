import easyocr
import re
import numpy as np
import pandas as pd
import sys

from typing import List, Self

class Point:
    def __init__(self, x: int, y: int) -> None:
        self.x = x
        self.y = y
    
    def __str__(self):
        return f"({self.x}, {self.y})"
    
    def __repr__(self):
        return f"({self.x}, {self.y})"

class Box:
    def __init__(self, points: List[Point], text: str) -> None:
        self.points = points
        self.text = text
    
    def x_left(self) -> int:
        return min(self.points, key=lambda point: point.x).x
    
    def x_right(self) -> int:
        return max(self.points, key=lambda point: point.x).x

    def y_top(self) -> int:
        return min(self.points, key=lambda point: point.y).y

    def y_bottom(self) -> int:
        return max(self.points, key=lambda point: point.y).y

    def width(self) -> int:
        return self.x_right() - self.x_left()

    def height(self) -> int:
        return self.y_bottom() - self.y_top()
    
    def __str__(self):
        return f"(\"{self.text}\", {str(self.points)})"
    
    def __repr__(self):
        return f"(\"{self.text}\", {str(self.points)})"
    

class Page:
    def __init__(self, boxes: List[Box]) -> None:
        self.boxes = boxes

    def median_height(self):
        heights = np.array(list(map(lambda box: box.height(), self.boxes)))
        return np.median(heights)
    
    def __str__(self):
        return f"{str(self.boxes)}"
    
    def __repr__(self):
        return f"{str(self.boxes)}"

class Transaction:
    def __init__(self, date: str, title: str, amount: int) -> None:
        self.date = date
        self.title = title
        self.amount = amount


class TransactionList:
    def __init__(self, transactions: List[Transaction]) -> None:
        self.transactions = transactions

    def append(self, transaction: Transaction) -> None:
        self.transactions.append(transaction)

    def to_clipboard(self) -> None:
        data: List[tuple[str, str, int]] = []
        for transaction in self.transactions:
            data.append((transaction.date, transaction.title, transaction.amount))
            print(transaction.date, transaction.title, transaction.amount)
        print('Copied to clipboard!')
        pd.DataFrame(data).to_clipboard(index=False, header=None)

    def extend(self, o: Self) -> None:
        self.transactions.extend(o.transactions)

class OcrReader:
    def __init__(self) -> None:
        self.reader = easyocr.Reader(['ja','en'])
    
    def read(self, file_name: str) -> Page: 
        result = self.reader.readtext(file_name) # type: ignore
        boxes: List[Box] = []
        for result_box in result:
            points: List[Point] = []
            for result_point in result_box[0]:
                points.append(Point(result_point[0], result_point[1]))
            text: str = result_box[1]
            boxes.append(Box(points, text)) 
        return Page(boxes)

class PageConverter:
    def read_to_transactions(self, page: Page) -> TransactionList:
        self.page = page
        self.amount_boxes: List[Box] = []
        self.date_boxes: List[Box] = []

        self._load_amount_and_date_boxes()
        self._remove_amount_box_height_outliers()
        self._sort_boxes_by_y()
        self._remove_incomplete_transaction()
        return self._get_transaction_list()
        
    
    def _load_amount_and_date_boxes(self):
        date_pattern = r'\d{2}\.\d{2}\.\d{2}'
        for box in self.page.boxes:
            text = box.text
            if '円' in text:
                self.amount_boxes.append(box)
            if re.match(date_pattern, text):
                self.date_boxes.append(box)

    # remove large amount box (box that's much bigger or smaller than median +-50%)
    def _remove_amount_box_height_outliers(self):
        height_diff_threshold = 0.5
        median = self.page.median_height()
        new_amount_boxes: List[Box] = []
        for box in self.amount_boxes:
            if abs(box.height() - median) / median < height_diff_threshold:
                new_amount_boxes.append(box)
        self.amount_boxes = new_amount_boxes

    def _sort_boxes_by_y(self):
        self.amount_boxes.sort(key=lambda box: box.y_top())
        self.date_boxes.sort(key=lambda box: box.y_top())

    def _remove_incomplete_transaction(self):
        # Amount must be on top, if there's date on top, remove it.
        if self.date_boxes[0].y_top() < self.amount_boxes[0].y_top():
            self.date_boxes = self.date_boxes[1:]

    def _get_transaction_list(self):
        # If there's no date matching amount, remove last amount.
        entry_count = min(len(self.amount_boxes), len(self.date_boxes))
        transactions: List[Transaction] = []
        for i in range(entry_count):
            amount_box = self.amount_boxes[i]
            date_box = self.date_boxes[i]
            amount = amount_box.text.replace('円', '').replace(',', '').strip()
            date = date_box.text.replace('.', '/')
            title = self._get_title(amount_box, date_box)
            transactions.append(Transaction(date, title, int(amount)))
        return TransactionList(transactions)

    def _get_title(self, amount_box: Box, date_box: Box) -> str:
        title_boxes: List[Box] = []
        for box in self.page.boxes:
            if self._is_title_box(box, amount_box, date_box):
                title_boxes.append(box)
        return self._merge_title_boxes(title_boxes)
    
    def _is_title_box(self, box: Box, amount_box: Box, date_box: Box) -> bool:
        if (box.x_right() < amount_box.x_left()) and (box.y_bottom() > amount_box.y_top()) and box.y_bottom() < date_box.y_top():
            return True
        return False
    
    def _merge_title_boxes(self, title_boxes: List[Box]) -> str:
        title = ""
        #TODO:sort left-right top-bottom
        for title_box in title_boxes:
            title += title_box.text
        return title

def main():
    image_files = sys.argv[1:]
    reader = OcrReader()
    transaction_list = TransactionList([])
    for image_file in image_files:
        page = reader.read(image_file)
        transaction_list.extend(PageConverter().read_to_transactions(page))
    transaction_list.to_clipboard()

if __name__ == '__main__':
    main()
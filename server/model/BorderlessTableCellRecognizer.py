import sys
import numpy as np
import cv2
from BorderTableCellRecognizer import extract_table
from server.service.data import Document, Table, Row, Cell, BBox, Point2D


def inside_table(table, cell, err):
    return cell[0] > table[0] - err and \
           cell[1] > table[1] - err and \
           cell[2] < table[2] + err and \
           cell[3] < table[3] + err


# calculating y's where horizontal lines should be
def y_lines_based_on_cells(table, cells, err):
    y_lines = [table[1]]  # list of y only
    bottom_y = top_y = -1
    prev_cell = None

    for i, cell in enumerate(cells):
        if i == 0:
            bottom_y, top_y = cell[1], cell[3]

        elif (bottom_y + err > cell[1] > bottom_y - err) or (top_y + err > cell[3] > top_y - err):
            if cell[3] > top_y:
                top_y = cell[3]

        else:
            bottom_y = cell[1]
            potential_line = (bottom_y + top_y) // 2  # mean of top y of row below and bottom y of row above

            if bottom_y > top_y:
                y_lines.append(potential_line)

            if prev_cell is not None:
                if potential_line < prev_cell + 10 or potential_line < prev_cell - 10:
                    y_lines.pop()  # same line

            prev_cell = potential_line
            top_y = cell[3]

    y_lines.append(table[3] + 50)

    return y_lines


# creating list of rows (list of cells in row)
def prepare_rows(y_lines, cells, err):
    rows = [[] for _ in range(len(y_lines))]

    i = 1
    for cell in cells:
        if cell[3] < y_lines[i]:
            rows[i - 1].append(cell)
        else:
            rows[i].append(cell)
            i += 1

    final_rows = [[] for _ in range(len(y_lines))]

    # correcting rows - sorting and removing "duplicated" cells
    for i, row in enumerate(rows):
        row.sort(key=lambda x: x[0])
        prev_cell = None

        for n, curr_cell in enumerate(row):
            if prev_cell is not None:
                if (prev_cell[0] + err >= curr_cell[0] >= prev_cell[0] - err) or \
                        (prev_cell[2] + err >= curr_cell[2] >= prev_cell[2] - err):
                    row.pop(n)

            prev_cell = curr_cell

        final_rows[i] = row

    return final_rows


# calculating top y and bottom y of each row
def calculate_rows_top_btm(final_rows):
    rows_top_btm = [[sys.maxsize, 0] for _ in range(len(final_rows))]
    prev_cell = None

    for n, row in enumerate(final_rows):
        for curr_cell in row:
            if prev_cell is None:
                prev_cell = curr_cell
            else:
                if curr_cell[1] < prev_cell[3]:
                    continue

            if rows_top_btm[n][0] > curr_cell[1]:
                rows_top_btm[n][0] = curr_cell[1]

            if rows_top_btm[n][1] < curr_cell[3]:
                rows_top_btm[n][1] = curr_cell[3]

    return rows_top_btm


# calculating y's where horizontal lines are based on top ys and bottom ys of rows
def y_lines_based_on_rows_boundaries(table, rows_top_btm):
    y_lines = [table[1]]
    prev_values, previous_line = None, None

    for i in range(len(rows_top_btm) - 1):
        if i == 0 and prev_values is None:
            prev_values = rows_top_btm[i]
        else:
            new_potential_line = (rows_top_btm[i][0] + prev_values[1]) // 2  # mean of min y curr_row and max y prev_row

            if previous_line is not None:
                if abs(new_potential_line - previous_line) <= 10:
                    y_lines.pop()

            y_lines.append(new_potential_line)
            previous_line = new_potential_line
            prev_values = rows_top_btm[i]

    y_lines.append(table[3])
    return y_lines


# calculating left x and right x of each col
def calculate_col_left_right(final_rows, max_len):
    col_left_right = [[sys.maxsize, 0] for _ in range(max_len)]

    for row in final_rows:
        if len(row) == max_len:  # for rows that have cells in every column
            for n, cell in enumerate(row):
                if cell[2] > col_left_right[n][1]:
                    col_left_right[n][1] = cell[2]

                if cell[0] < col_left_right[n][0]:
                    col_left_right[n][0] = cell[0]

    for row in final_rows:  # for rows that dont have cells in every column
        if len(row) != 0:
            i = 0
            for n, cell in enumerate(row):
                # finding in which column should we put first cell
                while i != len(row) - 1 and (col_left_right[n][0] > row[i][0]):
                    i += 1

                if n != 0:
                    if row[i - 1][0] > col_left_right[n - 1][1]:
                        if row[i - 1][0] < col_left_right[n][0]:
                            col_left_right[n][0] = row[i - 1][0]  # min x of column

    for row in final_rows:
        for n, cell in enumerate(row):
            if n != len(row) - 1:
                if cell[2] < col_left_right[n + 1][0]:
                    if cell[2] > col_left_right[n][1]:
                        col_left_right[n][1] = cell[2]  # max x of column

    return col_left_right


# calculating x's where vertical lines are based on left xs and rigth xs of cols
def x_lines_based_on_col_boundaries(table, col_left_right, max_len):
    x_lines = np.zeros(max_len + 1)
    x_lines[0] = table[0]

    prev_cell, i = 0, 1
    for x in range(len(col_left_right)):
        if x == 0:
            prev_cell = col_left_right[x]
        else:
            x_lines[i] = (col_left_right[x][0] + prev_cell[1]) // 2
            i += 1
            prev_cell = col_left_right[x]

    x_lines = x_lines.astype(int)
    x_lines[max_len] = table[2]

    return x_lines


# cell_img - image fragment of one cell
# returns bboxes of text in cell: [x, y, width, height] - (lower_left, width, height)
def extract_text_bboxes(cell_img):
    err7, err14 = 7, 14
    result_contours = []

    height, width = cell_img.shape[0:2]
    img_shape = height + err14, width + err14, 3

    img_array = np.zeros(img_shape, dtype=np.uint8)
    img_array[7:height+err7, 7:width+err7] = cell_img

    # preparing image
    img_gray = cv2.cvtColor(src=img_array, code=cv2.COLOR_BGR2GRAY)  # changing color space
    retval, img_threshold = cv2.threshold(src=img_gray, thresh=0, maxval=255,
                                          type=(cv2.THRESH_OTSU | cv2.THRESH_BINARY_INV))  # thresholding
    kernel = cv2.getStructuringElement(shape=cv2.MORPH_RECT, ksize=(3, 1))
    img_dilation = cv2.dilate(src=img_threshold, kernel=kernel, iterations=2)  # dilation

    # getting contours - vectors
    contours, hierarchy = cv2.findContours(image=img_dilation, mode=cv2.RETR_EXTERNAL, method=cv2.CHAIN_APPROX_NONE)

    # selecting contours
    for contour in contours:
        if cv2.contourArea(contour=contour) < 20:
            continue

        x, y, width, height = cv2.boundingRect(contour)

        if height < 6 or width < 4 or height / cell_img.shape[0] > 0.95 or height > 30:
            continue

        result_contours.append([x - err7, y - err7, width, height])

    return result_contours


# calculating bboxes of merged cells bboxes in rows
def calculate_merged_boxes(cell_bboxes_in_rows):
    merged_boxes = []  # boxes: [min x, min y, max x, max y]

    for cell_row in cell_bboxes_in_rows:
        cell_row = sorted(cell_row, key=lambda x: x[0])

        prev_cell = -1
        for cell in cell_row:
            if prev_cell == -1:
                prev_cell = cell
                continue

            if len(cell_row) == 1:
                merged_boxes.append(cell)
                break

            difference = (prev_cell[0] + prev_cell[2]) - cell[0]  # prev_cell max x - cell min x
            if abs(difference) < 10:
                prev_cell[2] = prev_cell[2] + cell[2] - difference

                if prev_cell[3] < cell[3]:
                    prev_cell[3] = cell[3]
            else:
                prev_cell[2] = prev_cell[0] + prev_cell[2]  # max x
                prev_cell[3] = prev_cell[1] + prev_cell[3]  # max y
                merged_boxes.append(prev_cell)

                prev_cell = cell

        prev_cell[2] = prev_cell[0] + prev_cell[2]
        prev_cell[3] = prev_cell[1] + prev_cell[3]
        merged_boxes.append(prev_cell)

    return merged_boxes


def prepare_document(table, ready_boxes_in_rows):
    upper_left = Point2D(table[0], table[3])
    lower_right = Point2D(table[2], table[1])
    bbox = BBox(upper_left, lower_right)
    table = Table(bbox)

    for final in ready_boxes_in_rows:
        row = Row()

        for box in final:
            upper_left = Point2D(box[0], box[3])
            lower_right = Point2D(box[2], box[1])
            bbox = BBox(upper_left, lower_right)
            cell = Cell("", bbox)
            row.addCell(cell)

        table.addRow(row)

    document = Document()
    document.add(table)

    return document


# input: table bboxes, detected cells bboxes, original image
# output: Document
#       bbox = [min x, min y, max x, max y]
def recognize(image, table, cells_bbox):
    err5, err15, err20, err50 = 5, 15, 20, 50

    table[0], table[1], table[2], table[3] = table[0] - err15, table[1] - err15, table[2] + err15, table[3] + err15

    cells = []
    for cell in cells_bbox:
        if inside_table(table, cell, err50):
            cells.append(cell)

    cells.sort(key=lambda x: x[3])

    horizontal_lines = [[table[0], table[1], table[2], table[1]]]  # list of horizontal lines: [min x, y, max x, y]

    y_lines = y_lines_based_on_cells(table, cells, err15)  # list of y only
    final_rows = prepare_rows(y_lines, cells, err5)  # list of rows (list of cells in row)
    rows_top_btm = calculate_rows_top_btm(final_rows)  # for each row: [min y, max y]
    y_lines = y_lines_based_on_rows_boundaries(table, rows_top_btm)  # list of y only

    max_len = 0
    for row in final_rows:
        if len(row) > max_len:
            max_len = len(row)

    col_left_right = calculate_col_left_right(final_rows, max_len)  # for each col: [min x, max x]
    x_lines = x_lines_based_on_col_boundaries(table, col_left_right, max_len)  # list of x where vertical lines are

    vertical_lines = []

    # ready lists of horizontal and vertical lines
    for no, c in enumerate(y_lines):
        vertical_lines.append([c, table[1], c, table[3]])  # [x, min y, x, max y]
    for no, c in enumerate(x_lines):
        horizontal_lines.append([table[0], c, table[2], c])  # [min x, y, max x, y]

    # from BorderTableCellRecognizer
    # cell bboxes: (x1, y1, x2, y2, x3, y3, x4, y4) - (lower_left, upper_left, upper_right, lower_right)
    final_cells_bboxes = extract_table(image[table[1]:table[3], table[0]:table[2]], 0,
                                       (horizontal_lines, vertical_lines))

    cells_bboxes = []  # cell bboxes: [x, y, width, height]

    for cell_bboxes in final_cells_bboxes:
        text_bboxes = extract_text_bboxes(image[cell_bboxes[1]:cell_bboxes[3], cell_bboxes[0]:cell_bboxes[4]])

        for text_bbox in text_bboxes:
            cells_bboxes.append([cell_bboxes[0] + text_bbox[0], cell_bboxes[1] + text_bbox[1],
                                 text_bbox[2], text_bbox[3]])

    cells_bboxes = sorted(cells_bboxes, key=lambda x: x[1])
    cell_bboxes_in_rows = [[]]  # list of rows of cell boxes

    bottom_y, row_number = -1, 0

    for cell in cells_bboxes:
        if bottom_y == -1:
            bottom_y = cell[1]
            cell_bboxes_in_rows[row_number].append(cell)
            continue

        if abs(cell[1] - bottom_y) < 8:
            cell_bboxes_in_rows[row_number].append(cell)
        else:
            bottom_y = cell[1]
            row_number += 1
            cell_bboxes_in_rows.append([])
            cell_bboxes_in_rows[row_number].append(cell)

    merged_boxes = calculate_merged_boxes(cell_bboxes_in_rows)  # boxes: [min x, min y, max x, max y]

    final_cells_bboxes.sort(key=lambda x: x[1])

    ready_boxes_in_rows = [[]]
    row_index, min_y = 0, -1

    for cell_bbox in final_cells_bboxes:
        if min_y == -1:
            min_y = cell_bbox[1]

        found_merged_box, found_final_box = [], []

        # finding max coordinates of merged_boxes containing current cell
        for merged_box in merged_boxes:
            if merged_box[0] >= cell_bbox[0] and merged_box[1] >= cell_bbox[1] and \
                    merged_box[2] <= cell_bbox[4] and merged_box[3] <= cell_bbox[3]:

                if len(found_merged_box) == 0:
                    found_merged_box = merged_box
                else:
                    if merged_box[0] < found_merged_box[0]:
                        found_merged_box[0] = merged_box[0]

                    if merged_box[1] < found_merged_box[1]:
                        found_merged_box[1] = merged_box[1]

                    if merged_box[2] > found_merged_box[2]:
                        found_merged_box[2] = merged_box[2]

                    if merged_box[3] > found_merged_box[3]:
                        found_merged_box[3] = merged_box[3]

        # finding box from final_rows which starts in cell_bbox
        for i, final_row in enumerate(final_rows):
            for j, box in enumerate(final_row):
                if cell_bbox[0] <= box[0] <= cell_bbox[4] and cell_bbox[1] <= box[1] <= cell_bbox[3]:
                    found_final_box = box
                    final_rows[i].pop(j)
                    break

        if abs(min_y - cell_bbox[1]) > 10:  # next row
            row_index += 1
            min_y = cell_bbox[1]
            ready_boxes_in_rows.append([])

        # deciding which to put in ready_boxes_in_rows
        if len(found_merged_box) == 0:
            if len(found_final_box) == 0:
                continue
            else:
                ready_boxes_in_rows[row_index].append(found_final_box)

        else:
            if len(found_final_box) == 0:
                ready_boxes_in_rows[row_index].append(found_merged_box)
            else:
                if abs(found_final_box[0] - found_merged_box[0]) <= err20 and \
                        abs(found_final_box[1] - found_merged_box[1]) <= err20 and \
                        abs(found_final_box[2] - found_merged_box[2]) <= err20 and \
                        abs(found_final_box[3] - found_merged_box[3]) <= err20:
                    ready_boxes_in_rows[row_index].append(found_merged_box)

                elif (abs(found_final_box[0] - found_merged_box[0]) <= err20 and
                      abs(found_final_box[2] - found_merged_box[2]) <= err20) or \
                        (abs(found_final_box[1] - found_merged_box[1]) <= err20 or
                         abs(found_final_box[3] - found_merged_box[3]) <= err20):
                    ready_boxes_in_rows[row_index].append(found_final_box)

                else:
                    ready_boxes_in_rows[row_index].append(found_merged_box)

    return prepare_document(table, ready_boxes_in_rows)

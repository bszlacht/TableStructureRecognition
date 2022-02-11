import sys
import numpy as np
import cv2
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


# finding intersection point of two lines
def intersection_point(x1, y1, x2, y2, x3, y3, x4, y4):

    if (x1 <= x4 + 5 or x1 <= x4 - 5) and (x1 >= x3 - 5 or x1 >= x3 + 5)  and\
            (y3 <= max(y1, y2) + 5) and (y3 + 8 >= min(y1, y2) or y3 - 5 >= min(y1, y2)):
        return [x1, y3]


# calculating cells bboxes based on found lines
def bboxes_based_on_lines(horizontal_lines, vertical_lines):

    x, y, num = 0, 0, 0
    points = []

    # finding all intersection points
    for x1, y1, x2, y2 in vertical_lines:
        col_points = []

        for x3, y3, x4, y4 in horizontal_lines:
            col_points.append(intersection_point(x1, y1, x2, y2, x3, y3, x4, y4))
            num += 1
        points.append(col_points)

    ready_bboxes, bboxes_to_finish = [], []
    flag = 1

    # cells bboxes based on intersection points
    for i, col_points in enumerate(points):
        new_bboxes = []

        for j, point in enumerate(col_points):

            if j == len(col_points) - 1:
                break

            next_point = col_points[j + 1]
            temp_bbox = [point[0], point[1], next_point[0], next_point[1], sys.maxsize, sys.maxsize, sys.maxsize, sys.maxsize]

            if i == 0:
                bboxes_to_finish.append(temp_bbox)

            else:
                new_bboxes.append(temp_bbox)

                indexes = []
                flag = 1

                for num, bbox_to_finish in enumerate(bboxes_to_finish):

                    if point[1] == bbox_to_finish[1] and bboxes_to_finish[num][4] == sys.maxsize:
                        bboxes_to_finish[num][4], bboxes_to_finish[num][5] = point[0], point[1]  # found top_right point

                        if bboxes_to_finish[num][4] != sys.maxsize and bboxes_to_finish[num][6] != sys.maxsize:
                            ready_bboxes.append(bboxes_to_finish[num])
                            indexes.append(num)
                            flag = 1

                    if next_point[1] == bbox_to_finish[3] and bboxes_to_finish[num][6] == sys.maxsize:
                        bboxes_to_finish[num][6], bboxes_to_finish[num][7] = next_point[0], next_point[1]  # found bottom_right point

                        if bboxes_to_finish[num][4] != sys.maxsize and bboxes_to_finish[num][6] != sys.maxsize:
                            ready_bboxes.append(bboxes_to_finish[num])
                            indexes.append(num)
                            flag = 1

                    if len(bboxes_to_finish) != 0:
                        if bboxes_to_finish[num][4] == sys.maxsize or bboxes_to_finish[num][6] == sys.maxsize:
                            flag = 0

                for idx in indexes:
                    bboxes_to_finish.pop(idx)

                # moving not ready bboxes to new_bboxes
                if flag == 0:
                    for bbox_to_finish in bboxes_to_finish:
                        if bbox_to_finish[4] == sys.maxsize or bbox_to_finish[6] == sys.maxsize:
                            new_bboxes.append(bbox_to_finish)

        if i != 0:
            bboxes_to_finish = new_bboxes

    return ready_bboxes


# cell_img - image fragment of one cell
# returns bboxes of text in cell: [x, y, width, height] - (lower_left, width, height)
def extract_text_bboxes(cell_img):
    err7, err14 = 7, 14
    result_contours = []

    height, width = cell_img.shape[0:2]
    img_shape = height + err14, width + err14, 3
    img_array = np.zeros(img_shape, dtype=np.uint8)

    # drawing cell borders
    cv2.rectangle(img=img_array, pt1=(0, 0), pt2=(width + err14, height + err14), color=(255, 255, 255), thickness=30)

    img_array[7:height + err7, 7:width + err7] = cell_img

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


# input: table bboxes, detected cells bboxes, original image
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
    for no, c in enumerate(x_lines):
        vertical_lines.append([c, table[1], c, table[3]])  # [x, min y, x, max y]
    for no, c in enumerate(y_lines):
        horizontal_lines.append([table[0], c, table[2], c])  # [min x, y, max x, y]

    final_cells_bboxes = bboxes_based_on_lines(horizontal_lines, vertical_lines)

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

    return table, ready_boxes_in_rows


def prepare_table(table, ready_boxes_in_rows, page):
    upper_left = Point2D(table[0], table[3])
    lower_right = Point2D(table[2], table[1])
    bbox = BBox(upper_left, lower_right)
    table = Table(bbox, page)

    for final in ready_boxes_in_rows:
        row = Row()

        for box in final:
            upper_left = Point2D(box[0], box[3])
            lower_right = Point2D(box[2], box[1])
            bbox = BBox(upper_left, lower_right)
            cell = Cell("", bbox, page)
            row.addCell(cell)

        table.addRow(row)

    return table


class BorderlessTableCellRecognizer:

    def recognize_borderless(self, document):
        result = Document(document.width, document.height, document.pages)
        tables = document.tables()

        for table in tables:
            # neural net returns detected cell bboxes in random order in single row of table
            rows = table.rows()
            image = document.pages()[table.page_index()]
            table_bbox, cells_bboxes = recognize(image, table.bbox(), rows[0])

            table = prepare_table(table_bbox, cells_bboxes, table.page_index())
            result.add_table(table)

        return result

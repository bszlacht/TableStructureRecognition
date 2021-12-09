import json

from service.data.Document import Cell, Row, Table, Document


class Converter:

    @staticmethod
    def convert_to_json(document):
        result = {}
        table_num = 1

        for table in document.get_tables():
            t = {}
            row_num = 1
            for row in table.get_rows():
                r = []
                for cell in row.get_cells():
                    r.append(cell.get_text())
                t["row" + str(row_num)] = r
                row_num += 1
            result["table" + str(table_num)] = t
            table_num += 1
        return json.dumps(result)


# code for tests

cell_1_1 = Cell("text1")
cell_1_2 = Cell("text2")
cell_1_3 = Cell("text3")
cell_2_1 = Cell("text4")
cell_2_2 = Cell("text5")
cell_2_3 = Cell("text6")

row1 = Row()
row1.add_cell(cell_1_1)
row1.add_cell(cell_1_2)
row1.add_cell(cell_1_3)

row2 = Row()
row2.add_cell(cell_2_1)
row2.add_cell(cell_2_2)
row2.add_cell(cell_2_3)

table = Table()
table.add_row(row1)
table.add_row(row2)

document = Document()
document.add_table(table)

print(Converter.convert_to_json(document))

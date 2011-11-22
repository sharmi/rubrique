from PyQt4.QtGui import QInputDialog

class EditTable(object):
    """Not to be used alone.  Used to abtract the table 
    editing features of Rubrique into a concise section"""
    def preliminaryCheck(fn):
        def table_fun(self):
            textCursor = self.editView.textCursor()
            table = textCursor.currentTable()
            if not table:
                return
            cell = table.cellAt(textCursor)
            rowIndex = cell.row()
            columnIndex = cell.column()
            return fn(self, textCursor, table, cell, rowIndex, columnIndex)
        return table_fun

    @preliminaryCheck
    def insertRowsBefore(self, textCursor, table, cell, rowIndex, columnIndex):
        rows, ok = QInputDialog.getInt(self, "Insert Rows", 'Enter Number of Rows', value=1)
        if ok and rows > 0:
                table.insertRows(rowIndex, rows)

    @preliminaryCheck
    def insertRowsAfter(self, textCursor, table, cell, rowIndex, columnIndex):
        rows, ok = QInputDialog.getInt(self, "Insert Rows", 'Enter Number of Rows', value=1)
        if ok and rows > 0:
            if (rowIndex + 1) < table.rows():
                table.insertRows(rowIndex + 1, rows)
            else:
                table.appendRows(rows)

    @preliminaryCheck
    def insertColumnsBefore(self, textCursor, table, cell, rowIndex, columnIndex):
        cols, ok = QInputDialog.getInt(self, "Insert Columns", 'Enter Number of Columns', value=1)
        if ok and cols > 0:
                table.insertColumns(columnIndex, cols)

    @preliminaryCheck
    def insertColumnsAfter(self, textCursor, table, cell, rowIndex, columnIndex):
        cols, ok = QInputDialog.getInt(self, "Insert Columns", 'Enter Number of Columns', value=1)
        if ok and cols > 0:
            if (columnIndex + 1) < table.columns():
                table.insertColumns(columnIndex+1, cols)
            else:        
                #table.insertColumns(columnIndex+1, cols)  It works, still would like to do it the other way
                table.appendColumns(cols)

    @preliminaryCheck
    def deleteColumns(self, textCursor, table, cell, rowIndex, columnIndex):
        cols, ok = QInputDialog.getInt(self, "Delete Columns", 'Enter Number of Columns to be deleted, starting from the current column', value=1)
        if ok and cols > 0:
            table.removeColumns(columnIndex, cols)

    @preliminaryCheck
    def deleteRows(self, textCursor, table, cell, rowIndex, columnIndex):
        rows, ok = QInputDialog.getInt(self, "Delete Rows", 'Enter Number of Rows to be deleted, starting from the current row', value=1)
        if ok and rows > 0:
            table.removeRows(rowIndex, rows)
    @preliminaryCheck
    def mergeCells(self, textCursor, table, cell, rowIndex, columnIndex):
        print "merge cells called"
        print rowIndex, columnIndex
        table.mergeCells(textCursor)
        #table.mergeCells(0, 0, 1, 2)

    @preliminaryCheck
    def splitCell(self, textCursor, table, cell, rowIndex, columnIndex):
        #table.splitCell(0, 0, 2, 1)
        #return Actually the rowNum and colsNum do not have any influence.  The merged cell is just split into the original cells
        table.splitCell(rowIndex, columnIndex, 0, 0)

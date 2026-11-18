from PyQt6.QtWidgets import (QGraphicsView, QGraphicsScene, QGraphicsRectItem, QGraphicsTextItem, QInputDialog, QGraphicsItem, 
                             QDialog, QVBoxLayout, QHBoxLayout, QComboBox, QPushButton, QTableWidget, QTableWidgetItem, 
                             QTabWidget, QWidget, QLabel, QTextEdit, QLineEdit, QGraphicsLineItem, QGraphicsPixmapItem, QMessageBox)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QPixmap, QPen

class ClassEditorDialog(QDialog):
    """
    Окно редактирования класса
    """
    def __init__(self, model, currentNodeId, parent = None):
        super().__init__(parent)
        self.model = model
        self.currentNodeId = currentNodeId
        self.setWindowTitle("Редактор класса")
        self.resize(650, 500)
        mainLayout = QVBoxLayout(self)

        topLayout = QHBoxLayout()
        topLayout.addWidget(QLabel("Выбранный класс:"))
        self.classCombo = QComboBox()

        for nid, node in self.model.nodes.items():
            self.classCombo.addItem(f"[{node.nodeType}] {node.name}", nid)
            if nid == self.currentNodeId:
                self.classCombo.setCurrentIndex(self.classCombo.count() - 1)

        self.classCombo.currentIndexChanged.connect(self.onClassSwitched)
        topLayout.addWidget(self.classCombo)
        mainLayout.addLayout(topLayout)

        self.tabs = QTabWidget()
        
        # Вкладка Атрибуты
        self.attrWidget = QWidget()
        attrLayout = QVBoxLayout(self.attrWidget)
        self.attrTable = QTableWidget(0, 3)
        self.attrTable.setHorizontalHeaderLabels(["Видимость", "Имя атрибута", "Тип данных"])
        attrLayout.addWidget(self.attrTable)
        
        attrBtnLayout = QHBoxLayout()
        btnAddAttr = QPushButton("Добавить атрибут")
        btnDelAttr = QPushButton("Удалить выбранный")
        btnAddAttr.clicked.connect(lambda: self.addRow(self.attrTable, isOp=False))
        btnDelAttr.clicked.connect(lambda: self.delRow(self.attrTable))
        attrBtnLayout.addWidget(btnAddAttr)
        attrBtnLayout.addWidget(btnDelAttr)
        attrLayout.addLayout(attrBtnLayout)
        self.tabs.addTab(self.attrWidget, "Атрибуты")

        # Вкладка Операции
        self.opWidget = QWidget()
        opLayout = QVBoxLayout(self.opWidget)
        self.opTable = QTableWidget(0, 4)
        self.opTable.setHorizontalHeaderLabels(["Видимость", "Имя метода", "Параметры ()", "Возвращаемый тип"])
        opLayout.addWidget(self.opTable)
        
        opBtnLayout = QHBoxLayout()
        btnAddOp = QPushButton("Добавить операцию")
        btnDelOp = QPushButton("Удалить выбранную")
        btnAddOp.clicked.connect(lambda: self.addRow(self.opTable, isOp=True))
        btnDelOp.clicked.connect(lambda: self.delRow(self.opTable))
        opBtnLayout.addWidget(btnAddOp)
        opBtnLayout.addWidget(btnDelOp)
        opLayout.addLayout(opBtnLayout)
        self.tabs.addTab(self.opWidget, "Операции (Методы)")

        # Вкладка Документация
        self.docWidget = QWidget()
        docLayout = QVBoxLayout(self.docWidget)
        docLayout.addWidget(QLabel("Описание / Документация класса:"))
        self.docTextEdit = QTextEdit()
        docLayout.addWidget(self.docTextEdit)
        self.tabs.addTab(self.docWidget, "Документация")

        mainLayout.addWidget(self.tabs)

        # Панель типов
        typeLayout = QHBoxLayout()
        self.newTypeInput = QLineEdit()
        self.newTypeInput.setPlaceholderText("Новый тип (например, MyClass)")
        btnAddType = QPushButton("Добавить в коллекцию типов")
        btnAddType.clicked.connect(self.addNewGlobalType)
        typeLayout.addWidget(self.newTypeInput)
        typeLayout.addWidget(btnAddType)
        mainLayout.addLayout(typeLayout)

        # Кнопки сохранения
        bottomButtons = QHBoxLayout()
        btnSave = QPushButton("Сохранить изменения")
        btnCancel = QPushButton("Отмена")
        btnSave.clicked.connect(self.saveAndClose)
        btnCancel.clicked.connect(self.reject)
        bottomButtons.addWidget(btnSave)
        bottomButtons.addWidget(btnCancel)
        mainLayout.addLayout(bottomButtons)

        self.loadClassData(self.currentNodeId)

    def loadClassData(self, nodeId):
        node = self.model.nodes.get(nodeId)
        if not node: return
        
        self.attrTable.setRowCount(0)
        self.opTable.setRowCount(0)

        for attr in node.attributes:
            row = self.attrTable.rowCount()
            self.attrTable.insertRow(row)
            
            visCombo = QComboBox()
            visCombo.addItems(["+", "-", "#"])
            visCombo.setCurrentText(attr.get('vis', '+'))
            self.attrTable.setCellWidget(row, 0, visCombo)

            self.attrTable.setItem(row, 1, QTableWidgetItem(attr.get('name', '')))

            typeCombo = QComboBox()
            typeCombo.addItems(self.model.availableTypes)
            typeCombo.setCurrentText(attr.get('type', 'int'))
            self.attrTable.setCellWidget(row, 2, typeCombo)

        for op in node.operations:
            row = self.opTable.rowCount()
            self.opTable.insertRow(row)
            
            visCombo = QComboBox()
            visCombo.addItems(["+", "-", "#"])
            visCombo.setCurrentText(op.get('vis', '+'))
            self.opTable.setCellWidget(row, 0, visCombo)

            self.opTable.setItem(row, 1, QTableWidgetItem(op.get('name', '')))
            
            params = op.get('params', '()')
            if not params.startswith('('): params = f"({params})"
            self.opTable.setItem(row, 2, QTableWidgetItem(params))

            typeCombo = QComboBox()
            typeCombo.addItems(self.model.availableTypes)
            typeCombo.setCurrentText(op.get('type', 'void'))
            self.opTable.setCellWidget(row, 3, typeCombo)

        self.docTextEdit.setPlainText(node.documentation)

    def onClassSwitched(self, index):
        nodeId = self.classCombo.itemData(index)
        if nodeId is not None:
            self.currentNodeId = nodeId
            self.loadClassData(nodeId)

    def addRow(self, table, isOp):
        row = table.rowCount()
        table.insertRow(row)
        
        visCombo = QComboBox()
        visCombo.addItems(["+", "-", "#"])
        table.setCellWidget(row, 0, visCombo)

        table.setItem(row, 1, QTableWidgetItem("newField" if not isOp else "newMethod"))
        
        if isOp:
            table.setItem(row, 2, QTableWidgetItem("()"))
            typeCombo = QComboBox()
            typeCombo.addItems(self.model.availableTypes)
            table.setCellWidget(row, 3, typeCombo)
        else:
            typeCombo = QComboBox()
            typeCombo.addItems(self.model.availableTypes)
            table.setCellWidget(row, 2, typeCombo)

    def delRow(self, table):
        currentRow = table.currentRow()
        if currentRow >= 0:
            table.removeRow(currentRow)

    def addNewGlobalType(self):
        newType = self.newTypeInput.text().strip()
        if newType:
            self.model.addTypeToCollection(newType)
            self.newTypeInput.clear()
            self.loadClassData(self.currentNodeId)
            QMessageBox.information(self, "Успех", f"Тип '{newType}' добавлен в глобальную коллекцию!")

    def saveAndClose(self):
        attributes = []
        for r in range(self.attrTable.rowCount()):
            vis = self.attrTable.cellWidget(r, 0).currentText()
            nameItem = self.attrTable.item(r, 1)
            name = nameItem.text().strip() if nameItem else "unnamed"
            typeCombo = self.attrTable.cellWidget(r, 2)
            typeVal = typeCombo.currentText() if typeCombo else "int"
            attributes.append({'vis': vis, 'name': name, 'type': typeVal})

        operations = []
        for r in range(self.opTable.rowCount()):
            vis = self.opTable.cellWidget(r, 0).currentText()
            nameItem = self.opTable.item(r, 1)
            name = nameItem.text().strip() if nameItem else "unnamed"
            
            paramItem = self.opTable.item(r, 2)
            params = paramItem.text().strip() if paramItem else "()"
            if not params.startswith('('): params = f"({params})"

            typeCombo = self.opTable.cellWidget(r, 3)
            typeVal = typeCombo.currentText() if typeCombo else "void"
            operations.append({'vis': vis, 'name': name, 'params': params, 'type': typeVal})

        documentation = self.docTextEdit.toPlainText()

        self.model.updateClassData(self.currentNodeId, attributes, operations, documentation)
        self.accept()
        
class IconButton(QGraphicsPixmapItem):
    def __init__(self, pixmap_path, callback, parent=None):
        super().__init__(QPixmap(pixmap_path).scaled(12, 12, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation), parent)
        self.callback = callback
    
    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            self.callback()
            event.accept()

class NodeRectItem(QGraphicsRectItem):
    """
    Графический элемент прямоугольника для отображения элемента диаграммы на сцене.
    Поддерживает выделение, перемещение и обработку двойного клика.
    """
    def __init__(self, nodeId, nodeType, name, x, y, callbacks):
        """
        Инициализирует прямоугольник элемента.

        Аргументы:
        renameCallback -- функция обратного вызова для отправки нового имени в модель.
        moveCallback -- функция обратного вызова для отправки новых координат в модель.
        """
        self.nodeWidth = 180.0
        super().__init__(0.0, 0.0, self.nodeWidth, 60.0) 
        self.nodeId = nodeId
        self.callbacks = callbacks 
        
        self.setPos(x, y)
        self.setFlag(QGraphicsItem.GraphicsItemFlag.ItemIsSelectable, True)
        self.setFlag(QGraphicsItem.GraphicsItemFlag.ItemIsMovable, True)
        self.setFlag(QGraphicsItem.GraphicsItemFlag.ItemSendsGeometryChanges, True)

        self.nameItem = QGraphicsTextItem(name, self)
        self.nameItem.setPos(5.0, 5.0)

        self.addBtn = IconButton("plus.png", self.openEditor, self)
        self.addBtn.setPos(self.nodeWidth - 15, 5)
        self.addBtn.hide() 
        self.contentItems = []

    def hoverEnterEvent(self, event):
        self.addBtn.show()
        super().hoverEnterEvent(event)

    def hoverLeaveEvent(self, event):
        self.addBtn.hide()
        super().hoverLeaveEvent(event)

    def itemChange(self, change, value):
        if change == QGraphicsItem.GraphicsItemChange.ItemPositionHasChanged:
            if hasattr(self, 'nodeId'):
                self.callbacks['move'](self.nodeId, value.x(), value.y())
        return super().itemChange(change, value)

    def mouseDoubleClickEvent(self, event):
        self.openEditor()
        super().mouseDoubleClickEvent(event)

    def openEditor(self):
        """
        Открывает диалог для добавления атрибута или операции
        """
        view = self.scene().views()[0]
        dialog = ClassEditorDialog(self.callbacks['modelRef'], self.nodeId, view)
        dialog.exec()

    def updateVisualName(self, newName):
        """
        Обновляет текст внутри класса
        """
        self.textItem.setPlainText(newName)

    def updateContent(self, attributes, operations):
        """
        Динамическая перерисовка внутри класса
        """
        for item in self.contentItems:
            self.scene().removeItem(item)
        self.contentItems.clear()

        currentY = 30.0 

        line1 = QGraphicsLineItem(0, currentY, self.nodeWidth, currentY, self)
        self.contentItems.append(line1)
        currentY += 5

        for attr in attributes:
            text = f"{attr['vis']} {attr['name']}: {attr['type']}"
            item = QGraphicsTextItem(text, self)
            item.setPos(5.0, currentY)
            self.contentItems.append(item)
            currentY += 18
        
        line2 = QGraphicsLineItem(0, currentY, self.nodeWidth, currentY, self)
        self.contentItems.append(line2)
        currentY += 5

        for op in operations:
            params = op.get('params', '()')
            text = f"{op['vis']} {op['name']}{params}: {op['type']}"
            item = QGraphicsTextItem(text, self)
            item.setPos(5.0, currentY)
            self.contentItems.append(item)
            currentY += 18

        newHeight = max(60, currentY + 10)
        self.setRect(0.0, 0.0, self.nodeWidth, float(newHeight))

class CanvasView(QGraphicsView):
    """
    Графическое поле для отображения сцены.
    Перехватывает нажатия ЛКМ по пустой области для создания новых элементов.
    """
    def __init__(self, parent=None):
        """
        Инициализирует графическое поле, устанавливает базовый тип создаваемого элемента по умолчанию.
        """
        super().__init__(parent)
        self.model = None
        new_scene = QGraphicsScene(self)
        self.setScene(new_scene)
        self.setSceneRect(0, 0, 1200, 900)
        self.currentNodeType = "Class" 
        self.isAddMode = False
        self.setDragMode(QGraphicsView.DragMode.RubberBandDrag)
        self.setMouseTracking(True)

    def setModel(self, model):
        """
        Связывает графическое поле и модель данных.
        """
        self.model = model

    def setAddMode(self, enabled):
        self.isAddMode = enabled
        if enabled:
            self.setDragMode(QGraphicsView.DragMode.NoDrag)
            self.setCursor(Qt.CursorShape.CrossCursor) 
        else:
            self.setDragMode(QGraphicsView.DragMode.RubberBandDrag)
            self.setCursor(Qt.CursorShape.ArrowCursor)

    def keyPressEvent(self, event):
        if event.key() == Qt.Key.Key_Delete and self.model:
            selected = self.scene().selectedItems()
            nodeIds = [item.nodeId for item in selected if isinstance(item, NodeRectItem)]
            if nodeIds:
                self.model.deleteNodes(nodeIds)
        super().keyPressEvent(event)        

    def mousePressEvent(self, event):
        """
        Обрабатывает нажатией левой кнопки мыши по холсту. 
        Если клик пришелся на пустое место, то запрашивает у модели создание нового элемента в вычисленных координатах сцены.
        """
        if self.model:
            click_pos = event.position().toPoint() if hasattr(event, 'position') else event.pos()
            itemAtClick = self.itemAt(click_pos)
            
            if self.isAddMode and itemAtClick is None and event.button() == Qt.MouseButton.LeftButton:
                scene_pos = self.mapToScene(click_pos)
                self.model.addNode(self.currentNodeType, scene_pos.x(), scene_pos.y())
                event.accept()
                return 
        super().mousePressEvent(event)
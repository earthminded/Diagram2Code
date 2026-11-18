import sys
from PyQt6.QtWidgets import QApplication, QMainWindow, QListWidgetItem, QWidget, QHBoxLayout, QLabel, QPushButton, QTreeWidgetItem
from PyQt6.QtCore import Qt
from ui_mainwindow import Ui_MainWindow
from PyQt6.QtGui import QIcon
from model import DiagramModel
from canvas import NodeRectItem, ClassEditorDialog

class MainWindow(QMainWindow):
    """
    Основное окно приложения.
    Отвечает за сборку интерфейса из Qt Designer, связывает элементы управления с моделью данных.
    """
    def __init__(self, model):
        """
        Инициализирует главное окно, и устанавливает обработчики для сигналов от модели данных.
        """
        super().__init__()
        self.model = model
        
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)
        self.ui.canvas.setModel(self.model)

        self.graphicsItems = {}
        self.treeItems = {}
        self.ui.classTree.setHeaderHidden(True)
        self.ui.classTree.itemDoubleClicked.connect(self.onTreeItemDoubleClicked)

        self.ui.clearButton.clicked.connect(lambda: self.model.clearModel())
        self.ui.actionAddNode.toggled.connect(self.ui.canvas.setAddMode)

        self.model.nodeAdded.connect(self.onNodeAdded)
        self.model.nodeRenamed.connect(self.onNodeRenamed)
        self.model.nodeDeleted.connect(self.onNodeDeleted)
        self.model.nodeUpdated.connect(self.onNodeUpdated)
        self.model.modelCleared.connect(self.onModelCleared)

    def onNodeAdded(self, nodeId, nodeType, name, x, y):
        """
        Обработчик сигнала добавления нового элемента в модель.
        Отрисовывает прямоугольник на графическом поле и добавляет текстовую запись в боковой список.
        """
        callbacks = {
            'move': self.model.moveNode,
            'modelRef': self.model
        }
        rectItem = NodeRectItem(nodeId, nodeType, name, x, y, callbacks)
        self.ui.canvas.scene().addItem(rectItem)
        self.graphicsItems[nodeId] = rectItem

        classItem = QTreeWidgetItem(self.ui.classTree)
        classItem.setData(0, Qt.ItemDataRole.UserRole, nodeId)
        
        attrParent = QTreeWidgetItem(classItem)
        attrParent.setText(0, "Атрибуты")
        opParent = QTreeWidgetItem(classItem)
        opParent.setText(0, "Операции")
        
        classItem.setExpanded(True)
        self.treeItems[nodeId] = {'class': classItem, 'attr': attrParent, 'op': opParent}

        container = QWidget()
        hLayout = QHBoxLayout(container)
        hLayout.setContentsMargins(0, 0, 5, 0)
        
        label = QLabel(f"[{nodeType}] {name}")
        delBtn = QPushButton()
        delBtn.setIcon(QIcon("trash.png"))
        delBtn.setFixedSize(20, 20)
        delBtn.setStyleSheet("border: none;")
        delBtn.clicked.connect(lambda: self.model.deleteNodes([nodeId]))
        
        hLayout.addWidget(label)
        hLayout.addStretch()
        hLayout.addWidget(delBtn)
        
        self.ui.classTree.setItemWidget(classItem, 0, container)

    def onNodeRenamed(self, nodeId, newName):
        """
        Обработчик сигнала переименования узла в модели.
        Обновляет визуальное отображение имени в прямоугольнике на холсте и в соответствующей строке бокового списка
        """
        if nodeId in self.graphicsItems:
                self.graphicsItems[nodeId].updateVisualName(newName)
        if nodeId in self.treeItems:
                node = self.model.nodes[nodeId]
                widget = self.ui.classTree.itemWidget(self.treeItems[nodeId]['class'], 0)
                if widget:
                    for child in widget.findChildren(QLabel):
                        child.setText(f"[{node.nodeType}] {newName}")

    def onNodeUpdated(self, nodeId):
        """
        Обрабочик обновления узла в модели
        """
        if nodeId in self.graphicsItems:
            node = self.model.nodes[nodeId]
            self.graphicsItems[nodeId].updateContent(node.attributes, node.operations)
            
            items = self.treeItems[nodeId]
            
            items['attr'].takeChildren()
            for attr in node.attributes:
                child = QTreeWidgetItem(items['attr'])
                child.setText(0, f"🔹 {attr['vis']} {attr['name']}: {attr['type']}")
                
            items['op'].takeChildren()
            for op in node.operations:
                params = op.get('params', '()')
                child = QTreeWidgetItem(items['op'])
                child.setText(0, f"🔸 {op['vis']} {op['name']}{params}: {op['type']}")
                
            items['attr'].setExpanded(True)
            items['op'].setExpanded(True)

    def onTreeItemDoubleClicked(self, item, column):
        classTreeItem = item
        while classTreeItem.parent() is not None:
            classTreeItem = classTreeItem.parent()
            
        nodeId = classTreeItem.data(0, Qt.ItemDataRole.UserRole)
        if nodeId is not None:
            dialog = ClassEditorDialog(self.model, nodeId, self)
            dialog.exec()

    def onNodeDeleted(self, nodeId):
        """
        Обработчик сигнала удаления одного элемента
        """
        if nodeId in self.graphicsItems:
            item = self.graphicsItems.pop(nodeId)
            self.ui.canvas.scene().removeItem(item)
            
        if nodeId in self.treeItems:
            treeInfo = self.treeItems.pop(nodeId)
            rootItem = treeInfo['class']
            index = self.ui.classTree.indexOfTopLevelItem(rootItem)
            if index != -1:
                self.ui.classTree.takeTopLevelItem(index)


    def onModelCleared(self):
        """
        Обработчик сигнала очистки модели.
        Удаляет все графические элементы со сцены и полностью очищает боковой список.
        """
        for item in self.graphicsItems.values():
            self.ui.canvas.scene().removeItem(item)
        self.graphicsItems.clear()
        if self.ui.canvas.scene(): self.ui.canvas.scene().clear()
        self.ui.classTree.clear()
        self.treeItems.clear()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    
    diagramModel = DiagramModel()
    window = MainWindow(diagramModel)
    window.show()
    
    sys.exit(app.exec())
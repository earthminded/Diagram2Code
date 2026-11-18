from PyQt6.QtCore import QObject, pyqtSignal

class DiagramNode:
    """
    Класс-контейнер для хранения данных об одном элементе диаграммы.
    """
    def __init__(self, nodeId, nodeType, name, x, y):
        """
        Инициализирует новый элемент.

        Аргументы:
        nodeId -- Уникальный айди каждого отдельного элемента.
        nodeType -- Тип элемента.
        nodeName -- Текущее имя элемента.
        x -- Координата по оси X на графическом поле.
        y -- Координата по оси Y на графическом поле.
        """
        self.nodeId = nodeId
        self.nodeType = nodeType 
        self.name = name
        self.x = x
        self.y = y
        self.attributes = [] 
        self.operations = []
        self.documentation = ""

class DiagramModel(QObject):
    """
    Главная модель данных. Хранит состояние всех элементов диаграммы.
    """
    nodeAdded = pyqtSignal(int, str, str, float, float) 
    nodeRenamed = pyqtSignal(int, str)
    nodeMoved = pyqtSignal(int, float, float)
    modelCleared = pyqtSignal()
    nodeDeleted = pyqtSignal(int)
    nodeUpdated = pyqtSignal(int)
    typesUpdated = pyqtSignal(list)

    def __init__(self):
        """
        Инициализирует пустую модель и счётчик индентификаторов.
        """
        super().__init__()
        self.nodes = {}
        self.nodeCounter = 1
        self.availableTypes = ["int", "float", "double", "string", "bool", "void", "char"]

    def addNode(self, nodeType, x, y):
        """
        Создаёт новый элемент заданного типа в указанных координатах.
        """
        nodeId = self.nodeCounter
        self.nodeCounter += 1
        name = f"{nodeType}{nodeId}" 
        self.nodes[nodeId] = DiagramNode(nodeId, nodeType, name, x, y)
        self.nodeAdded.emit(nodeId, nodeType, name, x, y)

    def renameNode(self, nodeId, newName):
        """
        Обновляет имя существующего элемента по его ID.
        """
        if nodeId in self.nodes and newName:
            self.nodes[nodeId].name = newName
            self.nodeRenamed.emit(nodeId, newName)
            self.nodeUpdated.emit(nodeId)

    def moveNode(self, nodeId, x, y):
        """
        Обновляет координаты существующего элемениа при его перемещении.
        """
        if nodeId in self.nodes:
            self.nodes[nodeId].x = x
            self.nodes[nodeId].y = y
            self.nodeMoved.emit(nodeId, x, y)

    def deleteNodes(self, nodeIds):
        """
        Пакетное удаление элементов
        """
        for nid in nodeIds:
            if nid in self.nodes:
                del self.nodes[nid]
                self.nodeDeleted.emit(nid)

    def addTypeToCollection(self, newType):
        """
        Добавление нового типа в глобальную коллекцию
        """
        newType = newType.strip()
        if newType and newType not in self.availableTypes:
            self.availableTypes.append(newType)
            self.typesUpdated.emit(self.availableTypes)

    def updateClassData(self, nodeId, attributes, operations, documentation):
        """
        Полное обновление данных класса из окна редактора
        """
        if nodeId in self.nodes:
            self.nodes[nodeId].attributes = attributes
            self.nodes[nodeId].operations = operations
            self.nodes[nodeId].documentation = documentation
            self.nodeUpdated.emit(nodeId)

    def clearModel(self):
        """
        Полностью очищает все данные модели, сбрасывает счетчик идентификаторов
        и даёт сигнал полной очистки для обновления интерфейса.
        """
        self.nodes.clear()
        self.nodeCounter = 1
        self.modelCleared.emit()
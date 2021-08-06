import enum
import typing
import pandas as pd
from collections import defaultdict, namedtuple
from PyQt5 import QtCore
from PyQt5.Qt import Qt

BoxOptions = namedtuple('BoxOptions', 'rows columns separator')


# -------------------- ItemSelection --------------------
class ItemSelection(enum.Enum):
    # selection constants
    CLEAR = 0
    PREVIOUS = 1
    NEXT = 2

    @staticmethod
    def selector():
        switcher = defaultdict(lambda pos: lambda: -1,
                               {ItemSelection.CLEAR: lambda pos: -1,
                                ItemSelection.PREVIOUS: lambda pos: pos - 1,
                                ItemSelection.NEXT: lambda pos: pos + 1})
        return switcher


# -------------------- QAbstractTableModel --------------------
class AbstractDataFrameModel(QtCore.QAbstractTableModel):
    """ Parent abstract DataFrame-based model class for QTableView (map and list) """
    def __init__(self, df: pd.DataFrame, update_function: typing.Callable = None):
        """ Initialize model
            :param df
                model data as DataFrame
            :param update_function(index: QModelIndex):
                function for updating dependent models;
                specify this for the model that is being edited by the user (by default, ListModel), so that the
                changes are translated to the dependent models (MapModel)
        """
        super(AbstractDataFrameModel, self).__init__()
        self._df = None
        self._df = df
        self._update_dependent_models = update_function

    def rowCount(self, parent=None):
        return self._df.shape[0]

    def columnCount(self, parent=None):
        return self._df.shape[1]

    def headerData(self, section: int, orientation: Qt.Orientation, role: int = ...):
        if role == Qt.DisplayRole:
            if orientation == Qt.Horizontal:
                return self._df.columns[section]
            if orientation == Qt.Vertical:
                return str(self._df.index[section])
        if role == Qt.TextAlignmentRole:
            return Qt.AlignCenter

    def setData(self, index: QtCore.QModelIndex, value: typing.Any, role: int = ...) -> bool:
        if not index.isValid():
            return False
        if role == Qt.EditRole:
            self._df.iloc[index.row(), index.column()] = value
            # call function to update dependent models
            if self._update_dependent_models is not None:
                self._update_dependent_models(index)
            return True
        return False

    @property
    def df(self):
        return self._df

    @df.setter
    def df(self, value):
        # update whole model
        self.beginResetModel()
        self._df = value
        self.endResetModel()

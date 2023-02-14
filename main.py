import cx_Oracle
from design import *
from PyQt5.QtWidgets import QMainWindow
from PyQt5 import QtCore, QtGui


class Pesquisa(QMainWindow, Ui_MainWindow):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setupUi(self)
        self.setFixedSize(self.size())
        self.btn_pesquisa.clicked.connect(lambda: self.preecher_tabela())
        self.btn_limpeza.clicked.connect(lambda: self.limpar())
        self.validador = QtGui.QIntValidator()
        self.validador.setRange(10000, 39999)
        self.entrada.setValidator(self.validador)
        self.setWindowTitle('FLIGHT CHECK')

    @staticmethod
    def db_connection():
        connection = cx_Oracle.connect("name/password@banco")
        cursor = connection.cursor()
        return cursor

    def pesquisar_fazenda(self):
        codigo = self.entrada.text()
        cursor = self.db_connection()
        query = '''
            SELECT FAZENDA, DATA_VOO, TIPO FROM (SELECT SUBSTR(GEOTEC_VANT_REL_HIST_VOO.CHAVE, 0, 5) FAZENDA, 
            SUBSTR(GEOTEC_VANT_REL_HIST_VOO.CHAVE, 6) TALHAO, 
            TO_CHAR(TO_DATE(SUBSTR(GEOTEC_VANT_REL_PLAN_VOO.FIM_VOO, 0, 10), 'YYYY/MM/DD'), 'DD/MM/YYYY') DATA_VOO,
            GEOTEC_VANT_REL_PLAN_VOO.TIPO_VOO TIPO
            FROM GEOTEC_VANT_REL_HIST_VOO, GEOTEC_VANT_REL_PLAN_VOO 
            WHERE GEOTEC_VANT_REL_HIST_VOO.ID_VOO = GEOTEC_VANT_REL_PLAN_VOO.OBJECTID) A
            GROUP BY FAZENDA, DATA_VOO, TIPO
        '''
        cursor.execute(query)
        res = [list(x) for x in cursor.fetchall()]
        dados = [res[x] for x in range(len(res)) if codigo in res[x]]
        return dados

    def preecher_tabela(self):
        if not self.entrada.text():
            self.msg_erro()
            return
        dados = self.pesquisar_fazenda()
        if not dados:
            self.msg_erro()
            return
        model = QtGui.QStandardItemModel(len(dados), 3)
        headers = ['CÓDIGO', 'DATA VOO', 'OPERAÇÃO']
        model.setHorizontalHeaderLabels(headers)
        self.table.horizontalHeader().setStretchLastSection(True)
        for row in range(len(dados)):
            for column in range(3):
                item = QtGui.QStandardItem(str(dados[row][column]))
                model.setItem(row, column, item)
                model.item(row, column).setEditable(False)
        self.table.setModel(model)

    def limpar(self):
        self.msg_erro() if not self.entrada.text() else self.entrada.clear()
        if self.table.model():
            self.table.model().deleteLater()
        else:
            pass

    def msg_erro(self):
        msg = QtWidgets.QMessageBox()
        msg.setWindowTitle('ERRO!')
        if not self.entrada.text():
            msg.setText('CAMPO VAZIO, FAVOR PREENCHER')
        else:
            msg.setText('FAZENDA NÃO ENCONTRADA')
        msg.exec()


if __name__ == '__main__':
    import sys
    app = QtCore.QCoreApplication.instance()
    if not app:
        app = QtWidgets.QApplication(sys.argv)
    p = Pesquisa()
    p.show()
    sys.exit(app.exec_())

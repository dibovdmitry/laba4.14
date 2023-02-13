#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from PySide2.QtSql import QSqlDatabase, QSqlQuery, QSqlTableModel
from PySide2.QtWidgets import (
    QTableView,
    QApplication,
    QHBoxLayout,
    QGridLayout,
    QPushButton,
    QWidget,
    QLineEdit,
    QFrame,
    QLabel,
    QHeaderView,
    QDateEdit,
    QTabWidget,
)
from PySide2.QtCore import (
    Signal,
)
from PySide2.QtCore import QSortFilterProxyModel, Qt, QRect
from sqlalchemy import create_engine
from sqlalchemy import (
    MetaData,
    Table,
    Column,
    Text,
    ForeignKey,
    insert,
    select,
    delete,
)
import sys


class DateBase:
    def __init__(self) -> None:
        self.engine = create_engine("sqlite:///hospitall.db")
        self.engine.connect()
        metadata = MetaData()
        self.Patient = Table(
            "Patient",
            metadata,
            Column("ФИО", Text(), nullable=False),
            Column("Дата_Рождения", Text(), nullable=False),
            Column("Полис", Text(), nullable=False),
            Column("СНИЛС", Text(), nullable=False),
        )

        self.Doctor = Table(
            "Doctor",
            metadata,
            Column("Врач", Text(), primary_key=True),
            Column("ФИО_Врача", Text(), nullable=False),
            Column("Заболевание_Пациента", Text(), nullable=False),
            Column("Жалобы", Text(), nullable=False),
        )

        self.Docs = Table(
            "Docs",
            metadata,
            Column("Врач", ForeignKey(self.Doctor.c.Врач)),
            Column("Пациент", ForeignKey(self.Patient.c.ФИО)),
            Column("Запись", Text(), nullable=False),
            Column("Время", Text(), nullable=False),
        )
        metadata.create_all(self.engine)
        db = QSqlDatabase.addDatabase("QSQLITE")
        db.setDatabaseName("hospitall.db")
        if not db.open():
            return False
        self.conn = self.engine.connect()

        if not self.table_is_empty():
            ins = insert(self.Patient)
            r = self.conn.execute(
                ins,
                ФИО="Арбузов Артём Михайлович",
                Дата_Рождения="20.10.1987",
                Полис="1923761282000012",
                СНИЛС="188-188-188 32",
            )
            r = self.conn.execute(
                ins,
                ФИО="Дыбов Дмитрий Вячеславович",
                Дата_Рождения="26.05.2002",
                Полис="2817218192192891",
                СНИЛС="122-345-584 32",
            )
            r = self.conn.execute(
                ins,
                ФИО="Васильев Иван Сергеевич",
                Дата_Рождения="15.07.1999",
                Полис="4958343358444588",
                СНИЛС="245-462-768 75",
            )
            ins = insert(self.Doctor)
            r = self.conn.execute(
                ins,
                Врач="Окулист",
                ФИО_Врача="Иванов Руслан Викторович",
                Заболевание_Пациента="Катаракта",
                Жалобы="Частые глазные боли",
            )

            r = self.conn.execute(
                ins,
                Врач="Эндокринолог",
                ФИО_Врача="Вараева Ольга Александровна",
                Заболевание_Пациента="Сахарный Диабет",
                Жалобы="Тошнота, Усталость",
            )
            r = self.conn.execute(
                ins,
                Врач="Хирург",
                ФИО_Врача="Арбузов Артём Михайлович",
                Заболевание_Пациента="Скалиоз",
                Жалобы="Боль в пояснице",
            )
            ins = insert(self.Docs)
            r = self.conn.execute(
                ins,
                Врач="Окулист",
                Пациент="Арбузов Артём Михайлович",
                Запись="12.12.2022",
                Время="11:30",
            )
            r = self.conn.execute(
                ins,
                Врач="Эндокринолог",
                Пациент="Дыбов Дмитрий Вячеславович",
                Запись="15.12.2022",
                Время="9:30"
            )
            r = self.conn.execute(
                ins,
                Врач="Хирург",
                Пациент="Васильев Иван Сергеевич",
                Запись="11.01.2023",
                Время="15:00"
            )

    def table_is_empty(self):
        data = self.Patient.select()
        table_data = self.conn.execute(data)
        return table_data.fetchall()


class TableView:
    tabBarClicked = Signal(int)

    def __init__(self, parent, db):
        self.parent = parent
        self.db = db
        self.SetupUI()
        self.current_tab = "Patient"
        self.tab_id = "ФИО"

    def SetupUI(self):
        self.parent.setGeometry(400, 500, 1000, 650)
        self.parent.setWindowTitle("База данных поликлиники")
        self.main_conteiner = QGridLayout()
        self.frame1 = QFrame()
        self.frame2 = QFrame()
        self.frame2.setVisible(False)
        self.main_conteiner.addWidget(self.frame1, 0, 0)
        self.main_conteiner.addWidget(self.frame2, 0, 0)
        self.frame1.setStyleSheet(
            """
            font: times new roman;
            font-size: 15px;
            """
        )
        self.frame2.setStyleSheet(
            """
            font: times new roman;
            font-size: 15px;
            """
        )
        self.table_view = QTableView()
        self.table_view.setModel(self.tablePatient())
        self.table_view2 = QTableView()
        self.table_view2.setModel(self.tableDoctor())
        self.table_view3 = QTableView()
        self.table_view3.setModel(self.tableDocs())
        self.table_view.horizontalHeader().setSectionResizeMode(0, QHeaderView.Stretch)
        self.table_view.horizontalHeader().setSectionResizeMode(1, QHeaderView.Stretch)
        self.table_view.horizontalHeader().setSectionResizeMode(2, QHeaderView.Stretch)
        self.table_view.horizontalHeader().setSectionResizeMode(3, QHeaderView.Stretch)
        self.table_view3.horizontalHeader().setSectionResizeMode(0, QHeaderView.Stretch)
        self.table_view3.horizontalHeader().setSectionResizeMode(1, QHeaderView.Stretch)
        self.table_view3.horizontalHeader().setSectionResizeMode(2, QHeaderView.Stretch)
        self.table_view3.horizontalHeader().setSectionResizeMode(3, QHeaderView.Stretch)
        self.table_view2.horizontalHeader().setSectionResizeMode(0, QHeaderView.Stretch)
        self.table_view2.horizontalHeader().setSectionResizeMode(1, QHeaderView.Stretch)
        self.table_view2.horizontalHeader().setSectionResizeMode(2, QHeaderView.Stretch)
        self.table_view2.horizontalHeader().setSectionResizeMode(3, QHeaderView.Stretch)
        self.layout_main = QGridLayout(self.frame1)
        self.layh = QHBoxLayout()
        self.btn_add = QPushButton("Добавить")
        self.btn_del = QPushButton("Удалить")
        self.layh.addWidget(self.btn_add)
        self.layh.addWidget(self.btn_del)
        self.tab_conteiner = QTabWidget()
        self.tab_conteiner.addTab(self.table_view, "Пациенты")
        self.tab_conteiner.addTab(self.table_view2, "Врачи")
        self.tab_conteiner.addTab(self.table_view3, "Записи")
        self.layout_main.addWidget(self.tab_conteiner, 0, 0)
        self.layout_main.addLayout(self.layh, 1, 0)
        self.parent.setLayout(self.main_conteiner)
        self.btn_del.clicked.connect(self.delete)
        self.btn_add.clicked.connect(self.add)
        self.layout_grid = QGridLayout(self.frame2)
        self.btn_add2 = QPushButton("Записаться на приём")
        self.btn_add2.setFixedWidth(300)
        self.btn_otmena = QPushButton("Отмена")
        self.line_name = QLineEdit()
        self.name = QLabel("ФИО врача: ")
        self.doc_num_line = QLineEdit()
        self.doc_num = QLabel("Должность врача: ")
        self.color_line = QLineEdit()
        self.color = QLabel("Номер СНИЛС: ")
        self.dateb_line = QLineEdit()
        self.dateb = QLabel("Заболевание пациента: ")
        self.line_pasport = QLineEdit()
        self.pasport = QLabel("Жалобы: ")
        self.vin_line = QLineEdit()
        self.vin = QLabel("ФИО пациента: ")
        self.marka = QLabel("Дата рождения пациента: ")
        self.marka_line = QDateEdit()
        self.marka_line.setCalendarPopup(True)
        self.marka_line.setTimeSpec(Qt.LocalTime)
        self.marka_line.setGeometry(QRect(220, 31, 133, 20))
        self.model_line = QLineEdit()
        self.models = QLabel("Номер полиса: ")
        self.docs_reg = QLabel("Дата записи: ")
        self.docs_reg_line = QDateEdit()
        self.docs_reg_line.setCalendarPopup(True)
        self.docs_reg_line.setTimeSpec(Qt.LocalTime)
        self.docs_reg_line.setGeometry(QRect(220, 31, 133, 20))
        self.cate_line = QLineEdit()
        self.cate = QLabel("Время записи: ")
        self.layout_grid.addWidget(self.line_name, 0, 1)
        self.layout_grid.addWidget(self.name, 0, 0)
        self.layout_grid.addWidget(self.doc_num, 1, 0)
        self.layout_grid.addWidget(self.doc_num_line, 1, 1)
        self.layout_grid.addWidget(self.dateb, 2, 0)
        self.layout_grid.addWidget(self.dateb_line, 2, 1)
        self.layout_grid.addWidget(self.marka_line, 3, 1)
        self.layout_grid.addWidget(self.marka, 3, 0)
        self.layout_grid.addWidget(self.model_line, 4, 1)
        self.layout_grid.addWidget(self.models, 4, 0)
        self.layout_grid.addWidget(self.line_pasport, 5, 1)
        self.layout_grid.addWidget(self.pasport, 5, 0)
        self.layout_grid.addWidget(self.vin_line, 6, 1)
        self.layout_grid.addWidget(self.vin, 6, 0)
        self.layout_grid.addWidget(self.color_line, 7, 1)
        self.layout_grid.addWidget(self.color, 7, 0)
        self.layout_grid.addWidget(self.docs_reg_line, 8, 1)
        self.layout_grid.addWidget(self.docs_reg, 8, 0)
        self.layout_grid.addWidget(self.cate, 9, 0)
        self.layout_grid.addWidget(self.cate_line, 9, 1)
        self.layout_grid.addWidget(self.btn_add2, 10, 1)
        self.layout_grid.addWidget(self.btn_otmena, 10, 0)
        self.btn_otmena.clicked.connect(self.back)
        self.btn_add2.clicked.connect(self.add_data)
        self.tab_conteiner.tabBarClicked.connect(self.handle_tabbar_clicked)

    def tablePatient(self):
        self.raw_model = QSqlTableModel()
        self.query = self.db.Patient.select()
        self.sqlquery = QSqlQuery()
        self.sqlquery.exec_(str(self.query))
        self.raw_model.setQuery(self.sqlquery)
        self.current_tab = "Patient"
        self.model = QSortFilterProxyModel()
        self.model.setSourceModel(self.raw_model)
        return self.model

    def tableDoctor(self):
        self.raw_model = QSqlTableModel()
        self.query = self.db.Doctor.select()
        self.sqlquery = QSqlQuery()
        self.sqlquery.exec_(str(self.query))
        self.raw_model.setQuery(self.sqlquery)
        self.current_tab = "Doctor"
        self.model = QSortFilterProxyModel()
        self.model.setSourceModel(self.raw_model)
        return self.model

    def tableDocs(self):
        self.raw_model = QSqlTableModel()
        self.query = self.db.Docs.select()
        self.sqlquery = QSqlQuery()
        self.sqlquery.exec_(str(self.query))
        self.raw_model.setQuery(self.sqlquery)
        self.current_tab = "Docs"
        self.model = QSortFilterProxyModel()
        self.model.setSourceModel(self.raw_model)
        return self.model

    def add(self):
        self.frame1.setVisible(False)
        self.frame2.setVisible(True)

    def back(self):
        self.frame1.setVisible(True)
        self.frame2.setVisible(False)

    def update(self):
        self.table_view.setModel(self.tablePatient())
        self.table_view2.setModel(self.tableDoctor())
        self.table_view3.setModel(self.tableDocs())

    def add_data(self):
        ins = insert(self.db.Patient)
        r = self.db.conn.execute(
            ins,
            ФИО=self.vin_line.text(),
            Дата_Рождения=self.marka_line.text(),
            Полис=self.model_line.text(),
            СНИЛС=self.color_line.text(),
        )
        ins = insert(self.db.Doctor)
        r = self.db.conn.execute(
            ins,
            Врач=self.doc_num_line.text(),
            ФИО_Врача=self.line_name.text(),
            Заболевание_Пациента=self.dateb_line.text(),
            Жалобы=self.line_pasport.text(),
        )
        ins = insert(self.db.Docs)
        r = self.db.conn.execute(
            ins,
            Врач=self.doc_num_line.text(),
            Пациент=self.vin_line.text(),
            Запись=self.docs_reg_line.text(),
            Время=self.cate_line.text(),
        )
        self.update()
        self.frame1.setVisible(True)
        self.frame2.setVisible(False)

    def cell_click(self):
        if self.current_tab == "Patient":
            return self.table_view.model().data(self.table_view.currentIndex())
        if self.current_tab == "Docs":
            return self.table_view3.model().data(self.table_view3.currentIndex())
        if self.current_tab == "Doctor":
            return self.table_view2.model().data(self.table_view2.currentIndex())

    def delete(self):
        if self.current_tab == "Patient":
            del_item = delete(self.db.Patient).where(
                self.db.Patient.c.ФИО.like(self.cell_click())
            )
            r = self.db.conn.execute(del_item)
        if self.current_tab == "Docs":
            del_item = delete(self.db.Docs).where(
                self.db.Docs.c.Врач.like(self.cell_click())
            )
            r = self.db.conn.execute(del_item)
        if self.current_tab == "Doctor":
            del_item = delete(self.db.Doctor).where(
                self.db.Doctor.c.Врач.like(self.cell_click())
            )
            r = self.db.conn.execute(del_item)
        self.update()

    def handle_tabbar_clicked(self, index):
        if index == 0:
            self.current_tab = "Patient"
            self.tab_id = "ФИО"
        elif index == 1:
            self.current_tab = "Doctor"
            self.tab_id = "Врач"
        else:
            self.tab_id = "Врач"
            self.current_tab = "Docs"


class MainWindow(QWidget):
    def __init__(self) -> None:
        QWidget.__init__(self)
        my_datebase = DateBase()
        self.main_view = TableView(self, my_datebase)


def main():
    app = QApplication(sys.argv)
    main_window = MainWindow()
    main_window.show()
    sys.exit(app.exec_())


if __name__ == "__main__":
    main()
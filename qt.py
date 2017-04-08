import sys
from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from PyQt5.QtCore import *
import subprocess
import os
import datetime
from datetime import *


COST = 5


class Example(QWidget):

    def __init__(self):
        super().__init__()
        self.initUI()

    def initUI(self):
        self.resize(800, 400)
        self.center()
        self.setWindowTitle('Seat Reservation')
        self.setWindowIcon(QIcon('web.png'))
        # This is the list containing seats already registered by others
        self.res = []
        try:
            data = open("data.txt", "r")
        except:
            data = open("data.txt", "w+")
        for line in data.readlines():
            linelist = line.split(",")[1:]
            self.res.extend([x.strip() for x in linelist])
        data.close()
        # this is the list used to store current seats slection
        self.userres = []
        # using nested layouts. A grid layout inside boxlaout
        mainLayout = QVBoxLayout(self)
        snackmenu = QHBoxLayout()
        self.Icecream = QCheckBox("Icecream: 6$")
        snackmenu.addWidget(self.Icecream)
        self.popcorn = QCheckBox("Pop corn: 5$")
        snackmenu.addWidget(self.popcorn)
        self.salad = QCheckBox("Fruit Salad: 4$")
        snackmenu.addWidget(self.salad)
        self.veggies = QCheckBox("Veggies: 5$")
        snackmenu.addWidget(self.veggies)
        self.puffs = QCheckBox("Puffs: 5$")
        snackmenu.addWidget(self.puffs)
        # Grid layout is used to print grid/table like structures easily
        grid = QGridLayout()
        # this is for gap of tha aisle
        grid.setColumnStretch(4, 10)
        # add grid layout inside the box layout
        mainLayout.addLayout(grid)
        mainLayout.addLayout(snackmenu)
        # this is the space left at top for screen
        mainLayout.insertSpacing(0, 60)
        # function to draw seats in grid layout
        self.drawSeats(grid)
        reserveButton = QPushButton("Proceed to Payment")  # button for payment
        reserveButton.clicked.connect(self.payment)
        mainLayout.addWidget(reserveButton)
        self.show()

    def payment(self):
        if len(self.userres) == 0:  # no seats are selected
            QMessageBox.about(self, "Notice",
                              "Please book atleast one seat")
            return
        price = 0
        snacks = []
        if self.veggies.isChecked():
            price = price + 5
            snacks.append("Veggies")
        if self.Icecream.isChecked():
            price = price + 6
            snacks.append("Icecream")
        if self.puffs.isChecked():
            price = price + 5
            snacks.append("Puffs")
        if self.popcorn.isChecked():
            price = price + 5
            snacks.append("Popcorn")
        if self.salad.isChecked():
            price = price + 4
            snacks.append("Fruit Salad")

        self.popup = Payments(self.userres, price, snacks)
        self.popup.setGeometry(100, 100, 500, 300)
        self.popup.show()
        self.close()

    def drawSeats(self, grid):
        self.seats = []
        for i in range(9):
            k = 0
            for j in range(9):
                if j == 4:
                    self.seats.append('')  # this leave gap for aisle
                    continue
                seatno = chr(65 + i) + str(k)  # it is the seat number
                self.seats.append(seatno)
                k = k + 1
        positions = [(i, j) for i in range(9) for j in range(9)]
        # this position contains grid location for seats from 0,0 to 9,9
        for position, seat in zip(positions, self.seats):
            if seat == '':
                continue
            button = QPushButton(seat)
            button.setText(seat)
            # if seat number is already reserved print red
            if seat in self.res:
                button.setStyleSheet("Background-color:red")
            else:  # not reserved so print green
                button.setStyleSheet("Background-color:green")
            button.clicked.connect(self.reserve)
            grid.addWidget(button, position[0], position[1])

    def reserve(self):  # this is called whenever a seat is clicked
        sender = self.sender()
        color = str(sender.palette().color(1).name())
        if color == "#ff0000":  # red it can't be reserved
            QMessageBox.about(self, sender.text(),
                              "Sorry the seat is already reserved")
            return
        # green, add to selection list and change to blue
        elif color == "#008000":
            self.userres.append(sender.text())
            sender.setStyleSheet("Background-color:blue")
        else:  # blue, remove from selection list and change to green
            self.userres.remove(sender.text())
            sender.setStyleSheet("Background-color:green")

    def center(self):
        qr = self.frameGeometry()
        cp = QDesktopWidget().availableGeometry().center()
        qr.moveCenter(cp)
        self.move(qr.topLeft())

    def paintEvent(self, event):
        painter = QPainter()
        painter.begin(self)
        painter.setPen(QColor(0, 0, 0, 127))
        painter.setBrush(QColor(0, 0, 0, 127))
        painter.drawRect(150, 0, 500, 50)
        painter.setFont(QFont("SanSerif", 20))
        painter.drawText(350, 25, "Screen")
        painter.end()


class Payments(QWidget):
    def __init__(self, res, price, snacks):
        super().__init__()
        self.res = res
        self.price = price
        self.snacks = snacks
        self.initUI()

    def initUI(self):
        self.setWindowTitle("Payment")
        self.center()
        name = QLabel("Card Holder's Name")
        cost = QLabel("Total Cost: {}$".format(len(self.res) * COST + self.price))
        cardNumber = QLabel("Card Number")
        cvv = QLabel("Card CVV")

        self.cost = {"Icecream": 6,
                     "Veggies": 5,
                     "Puffs": 5,
                     "Popcorn": 5,
                     "Fruit Salad": 4
                     }
        self.nameEdit = QLineEdit()
        self.cardNumberEdit = QLineEdit()
        self.cardNumberEdit.setPlaceholderText("XXXX-XXXX-XXXX-XXXX")
        self.cardNumberEdit.setMaxLength(19)
        self.cvvEdit = QLineEdit()
        self.cvvEdit.setPlaceholderText("XXX")
        self.cvvEdit.setMaxLength(3)

        grid = QGridLayout()
        grid.setVerticalSpacing(10)
        grid.addWidget(cost, 4, 1)
        grid.addWidget(name, 1, 0)
        grid.addWidget(self.nameEdit, 1, 1)
        grid.addWidget(cardNumber, 2, 0)
        grid.addWidget(self.cardNumberEdit, 2, 1)
        grid.addWidget(cvv, 3, 0)
        grid.addWidget(self.cvvEdit, 3, 1)
        button = QPushButton("Submit")
        button.clicked.connect(self.quit)
        grid.addWidget(button, 4, 0)
        self.setLayout(grid)
        self.show()

    def quit(self):
        file = open("bill.txt", "w+")
        file.write("      Theatre seat reservation\n")
        file.write("       " + str(datetime.now()) + "\n")
        file.write("--------------------------------------------\n")
        file.write("|        Products        |   Nos.  | Total |\n")
        file.write("============================================\n")
        file.write("|        {0:11}     |    {1}    |   {2}  |\n".format(
            "Seats", str(len(self.res)), len(self.res) * COST))
        for i in self.snacks:
            file.write("|        {0:11}     |    {1}    |   {2}   |\n".
                       format(i, 1, self.cost[i]))
        file.write("--------------------------------------------\n")
        file.write("                           Amount Paid:{}$\n".format(self.price+len(self.res)*COST))
        file.write("Seat Numbers:" + " ".join(self.res) + "\n")
        if os.name == "posix":
            lpr = subprocess.Popen("/usr/bin/lpr", stdin=subprocess.PIPE)
            lpr.stdin.write(bytes(file.read(), 'utf-8'))
        else:
            os.startfile("bill.txt", "print")
        file.close()
        data = open("data.txt", "a")
        data.write(str(self.nameEdit.text()) + "," + ",".join(self.res) + "\n")
        data.close()
        QMessageBox.about(self, "Thank you",
                          "You have successfully booked the tickets")
        self.close()

    def center(self):
        qr = self.frameGeometry()
        cp = QDesktopWidget().availableGeometry().center()
        qr.moveCenter(cp)
        self.move(qr.topLeft())


if __name__ == '__main__':

    app = QApplication(sys.argv)
    ex = Example()
    sys.exit(app.exec_())

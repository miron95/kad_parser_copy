import tkinter.font
from tkinter import *


class InterCaptcha:

    def __init__(self):
        self.win = Tk()
        self.win.title("Окно ввода капчи")
        self.label = Label(self.win, text = 'Введите капчу, чтобы продолжить:', font = 20)
        self.enter_field = Entry(self.win, width = 20)
        self.button = Button(self.win, text = 'Ввести', command = self.enter_captcha)
        self.perem = str()

        self.img = PhotoImage(file = 'captcha.png')
        self.label_img = Label(self.win, image = self.img)

        self.label.pack()
        self.label_img.pack()
        self.enter_field.pack()
        self.button.pack()
        self.button.bind()

    def enter_captcha(self):
        self.perem = self.enter_field.get()
        self.win.destroy()

    def quit(self):
        self.win.quit()

    def run(self):
        self.win.mainloop()


class InitialWindow:

    def __init__(self):
        self.win = Tk()
        self.selected = IntVar()
        self.fontsize = tkinter.font.Font(family = "Arial", size = 12)
        self.win.title("Окно начального заполнения")
        self.label_choise = Label(self.win, text = 'Выберете где получать капчу:', font = self.fontsize)
        self.label_date_from = Label(self.win, text = 'Введите дату начала периода (дд.мм.гггг)', font = self.fontsize)
        self.label_date_to = Label(self.win, text = 'Введите дату конца периода (дд.мм.гггг)', font = self.fontsize)
        self.choise_tg = Radiobutton(self.win, text = 'Telegram', value = 0, variable = self.selected,
                                     font = self.fontsize)
        self.choise_loc = Radiobutton(self.win, text = 'Локально', value = 1, variable = self.selected,
                                      font = self.fontsize)
        self.enter_date_from = Entry(self.win, width = 25, font = self.fontsize)
        self.enter_date_to = Entry(self.win, width = 25, font = self.fontsize)
        self.button = Button(self.win, text = 'Ввести начальные данные', command = self.enter, font = self.fontsize)
        self.perem = []

        self.label_choise.grid(columnspan = 3, pady = 5)
        self.choise_tg.grid(column = 0, row = 1)
        self.choise_loc.grid(column = 1, row = 1)

        self.label_date_from.grid(column = 0, row = 2, pady = 5, padx = 4)
        self.enter_date_from.grid(column = 1, row = 2, padx = 4)
        self.label_date_to.grid(column = 0, row = 3, pady = 5, padx = 4)
        self.enter_date_to.grid(column = 1, row = 3, padx = 4)

        self.button.grid(column = 0, row = 4, columnspan = 2, pady = 5)

    def enter(self):
        choise = str(self.selected.get())
        date_from = self.enter_date_from.get()
        date_to = self.enter_date_to.get()
        self.perem = choise, date_from, date_to
        print(self.perem)
        self.win.destroy()

    def quit(self):
        self.win.quit()

    def run(self):
        self.win.mainloop()

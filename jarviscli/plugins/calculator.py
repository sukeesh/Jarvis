import math
from plugin import plugin


@plugin("gui calculator")
class Calculator:
    """
    Opens GUI Calculator.

    {Note: Trigonometric ratios take value in degrees.}
    """

    def __call__(self, jarvis, s):
        try:
            import tkinter as tk
        except ModuleNotFoundError:
            jarvis.say("Tkinter not installed!")

        self.a = 0
        self.operator = ""

        """Calculator window"""
        self.calcwin = tk.Tk()
        self.calcwin.title('Jarvis Calculator')
        self.calcwin.geometry("350x450")
        self.calcwin.resizable(False, False)
        self.calcwin.attributes('-type', 'dialog')
        self.calcwin.attributes('-topmost', True)
        self.calcwin.config(bg="blue")

        """Buttons and other widgets"""
        self.num = tk.Entry(self.calcwin, width=18,
                            font=("Arial black", 20))
        self.num.place(x=17, y=45)
        self.num.focus_set()

        self.buffer = tk.Label(self.calcwin, bg="yellow", width=27,
                               fg="red", anchor='w', font=("", 13))
        self.buffer.place(x=23, y=10)

        self.ans = tk.Label(self.calcwin, bg="light green", width=17,
                            fg="black", font=("Arial black", 20))
        self.ans.place(x=27, y=95)

        self.plusbtn = tk.Button(self.calcwin, text="+",
                                 font=("Elephant", 20), command=self.plus)
        self.plusbtn.config(width=3)
        self.plusbtn.place(x=8, y=165)

        self.minusbtn = tk.Button(
            self.calcwin, text="-", font=("Elephant", 20),
            command=self.minus)
        self.minusbtn.config(width=3)
        self.minusbtn.place(x=93, y=165)

        self.multbtn = tk.Button(
            self.calcwin, text="x", font=("Elephant", 20),
            command=self.mult)
        self.multbtn.config(width=3)
        self.multbtn.place(x=178, y=165)

        self.divbtn = tk.Button(
            self.calcwin, text="/", font=("Elephant", 20),
            command=self.div)
        self.divbtn.config(width=3)
        self.divbtn.place(x=263, y=165)

        self.sqrootbtn = tk.Button(
            self.calcwin, text="sqrt", font=("Elephant", 20),
            command=self.sqroot)
        self.sqrootbtn.config(height=1, width=3)
        self.sqrootbtn.place(x=8, y=245)

        self.factbtn = tk.Button(
            self.calcwin, text="!", font=("Elephant", 20),
            command=self.fact)
        self.factbtn.config(width=3)
        self.factbtn.place(x=93, y=245)

        self.powerbtn = tk.Button(
            self.calcwin, text="x^y", font=("Elephant", 20),
            command=self.power)
        self.powerbtn.config(height=1, width=3)
        self.powerbtn.place(x=178, y=245)

        self.c_btn = tk.Button(self.calcwin, text="C",
                               font=("Elephant", 20),
                               command=self.c)
        self.c_btn.config(height=1, width=3)
        self.c_btn.place(x=263, y=245)

        self.sinbtn = tk.Button(
            self.calcwin, text="sin", font=("Elephant", 20),
            command=self.sin)
        self.sinbtn.config(height=1, width=3)
        self.sinbtn.place(x=8, y=325)

        self.cosbtn = tk.Button(
            self.calcwin, text="cos", font=("Elephant", 20),
            command=self.cos)
        self.cosbtn.config(height=1, width=3)
        self.cosbtn.place(x=93, y=325)

        self.tanbtn = tk.Button(
            self.calcwin, text="tan", font=("Elephant", 20),
            command=self.tan)
        self.tanbtn.config(height=1, width=3)
        self.tanbtn.place(x=178, y=325)

        self.equalbtn = tk.Button(
            self.calcwin, text="=", font=("Elephant", 20),
            command=lambda: self.equal(0))
        self.equalbtn.config(width=3)
        self.equalbtn.place(x=263, y=325)

        self.exitbtn = tk.Button(
            self.calcwin, text="EXIT", bg="red", fg="white",
            command=lambda: self.exit(0))
        self.exitbtn.place(x=150, y=405)

        self.keybinds()
        self.calcwin.mainloop()

    def plus(self):
        self.a = self.num.get()
        self.num.delete(0, 'end')
        self.num.focus_set()
        self.operator = "+"
        self.buffer["text"] = str(self.a) + " " + str(self.operator)

    def minus(self):
        self.a = self.num.get()
        self.num.delete(0, 'end')
        self.num.focus_set()
        self.operator = "-"
        self.buffer["text"] = str(self.a) + " " + str(self.operator)

    def mult(self):
        self.a = self.num.get()
        self.num.delete(0, 'end')
        self.num.focus_set()
        self.operator = "x"
        self.buffer["text"] = str(self.a) + " " + str(self.operator)

    def div(self):
        self.a = self.num.get()
        self.num.delete(0, 'end')
        self.num.focus_set()
        self.operator = "/"
        self.buffer["text"] = str(self.a) + " " + str(self.operator)

    def sqroot(self):
        try:
            self.a = self.num.get()
            self.buffer["text"] = "sqrt(" + str(self.a) + ")"
            if float(self.a) >= 0:
                self.an = math.sqrt(float(self.a))
                if len(str(self.an)) > 17:
                    self.ans["text"] = str(round(self.an, 4))
                else:
                    self.ans["text"] = str(math.sqrt(float(self.a)))
            else:
                self.ans["text"] = "Not a real number"
        except ValueError:
            self.ans["text"] = "Invalid Input "
        except TypeError:
            self.ans["text"] = "Invalid Input "
        except OverflowError:
            self.ans["text"] = "Out of range"

    def fact(self):
        try:
            self.a = self.num.get()
            self.buffer["text"] = str(self.a) + "!"
            if float(self.a) >= 0:
                self.an = str(math.factorial(float(self.a)))
                self.ans["text"] = self.an
                if len(self.an) > 17:
                    self.ans["text"] = "Out of Range"
            else:
                self.ans["text"] = "Error"
        except ValueError:
            self.ans["text"] = "Invalid Input "
        except TypeError:
            self.ans["text"] = "Invalid Input "
        except OverflowError:
            self.ans["text"] = "Out of range"

    def power(self):
        self.a = self.num.get()
        self.num.delete(0, 'end')
        self.num.focus_set()
        self.operator = "^"
        self.buffer["text"] = str(self.a) + str(self.operator)

    def sin(self):
        try:
            self.a = float(self.num.get()) / 57.2958  # convert to deg
            self.buffer["text"] = "sin(" + str(self.num.get()) + ")"
            self.an = str(round(math.sin(float(self.a)), 4))
            self.ans["text"] = self.an
            if len(self.an) > 17:
                self.ans["text"] = "Out of Range"
        except ValueError:
            self.ans["text"] = "Invalid Input "
        except TypeError:
            self.ans["text"] = "Invalid Input "
        except OverflowError:
            self.ans["text"] = "Out of range"

    def cos(self):
        try:
            self.a = float(self.num.get()) / 57.2958  # convert to deg
            self.buffer["text"] = "cos(" + str(self.num.get()) + ")"
            self.an = str(round(math.cos(float(self.a)), 4))
            self.ans["text"] = self.an
            if len(self.an) > 17:
                self.ans["text"] = "Out of Range"
        except ValueError:
            self.ans["text"] = "Invalid Input "
        except TypeError:
            self.ans["text"] = "Invalid Input "
        except OverflowError:
            self.ans["text"] = "Out of range"

    def tan(self):
        try:
            self.a = float(self.num.get()) / 57.2958  # convert to deg
            self.buffer["text"] = "tan(" + str(self.num.get()) + ")"
            self.an = str(round(math.tan(float(self.a)), 4))
            self.ans["text"] = self.an
            if len(self.an) > 17:
                self.ans["text"] = "Out of Range"
        except ValueError:
            self.ans["text"] = "Invalid Input "
        except TypeError:
            self.ans["text"] = "Invalid Input "
        except OverflowError:
            self.ans["text"] = "Out of range"

    def c(self):
        """clear button for calculator"""
        self.a = 0
        self.b = 0
        self.num.delete(0, 'end')
        self.ans["text"] = ""
        self.buffer["text"] = ""

    def equal(self, event):
        try:
            self.b = self.num.get()
            if self.operator == "+":
                self.an = str(float(self.a) + float(self.b))
                if len(self.an) < 17:
                    self.ans["text"] = self.an
                else:
                    self.ans["text"] = "Out of Range"
            elif self.operator == "-":
                self.an = str(float(self.a) - float(self.b))
                if len(self.an) < 17:
                    self.ans["text"] = self.an
                else:
                    self.ans["text"] = "Out of Range"
            elif self.operator == "x":
                self.an = str(float(self.a) * float(self.b))
                if len(self.an) < 17:
                    self.ans["text"] = self.an
                else:
                    self.ans["text"] = "Out of Range"
            elif self.operator == "^":
                self.an = str(math.pow(float(self.a), float(self.b)))
                if len(self.an) < 17:
                    self.ans["text"] = self.an
                else:
                    self.ans["text"] = "Out of Range"
            elif self.operator == "/":
                if float(self.b) != 0:
                    self.an = str(round(float(self.a) / float(self.b), 3))
                    if len(self.an) < 17:
                        self.ans["text"] = self.an
                    else:
                        self.ans["text"] = "Out of Range"
                else:
                    self.ans["text"] = "Not a number"
        except ValueError:
            self.ans["text"] = "Invalid Input "
        except TypeError:
            self.ans["text"] = "Invalid Input "
        except OverflowError:
            self.ans["text"] = "Out of range"

    def exit(self, event):
        self.calcwin.destroy()

    def keybinds(self):
        self.calcwin.bind('<Return>', self.equal)
        self.calcwin.bind('<Escape>', self.exit)

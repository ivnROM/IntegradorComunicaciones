import tkinter as tk
import calendar

class CalendarWidget(tk.Frame):
    def __init__(self, parent, year, month, **kwargs):
        super().__init__(parent, **kwargs)

        self.cal_frame = tk.Frame(self)
        self.cal_frame.pack(side="top", fill="x")

        self.redraw(year, month)

    def redraw(self, year, month):

        for child in self.cal_frame.winfo_children():
            child.destroy()

        for col, day in enumerate(("Lu", "Ma", "Mi", "Ju", "Vi", "Sa", "Do")):
            label = tk.Label(self.cal_frame, text=day)
            label.grid(row=0, column=col, sticky="nsew")

        cal = calendar.monthcalendar(year, month)
        for row, week in enumerate(cal):
            for col, day in enumerate(week):
                text = "" if day == 0 else day
                state = "normal" if day > 0 else "disabled"
                cell = tk.Button(self.cal_frame, text=text, state=state, command=lambda day=day: self.set_day(day))
                cell.grid(row=row+1, column=col, sticky="nsew")

    def set_day(self, num):
        print(f"you selected day {num}")

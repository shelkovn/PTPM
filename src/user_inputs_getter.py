from abc import ABC, abstractmethod
import tkinter as tk
from tkinter import messagebox

class UserInterface(ABC):
    @abstractmethod
    def set_controller(self, controller):
        """register controller."""
        pass

    @abstractmethod
    def show_error(self, message: str):
        pass
    
    @abstractmethod
    def get_user_data(self) -> list[str]:
        """get 3 sides as list of strings"""
        pass

    @abstractmethod
    def draw_triangle(self, coords: list[tuple[int, int]]):
        """draw the triangle."""
        pass

    @abstractmethod
    def run_ui(self):
        """start the ui"""
        pass

class TkinterInterface(UserInterface):
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("triange 3000 pro edition max")
        self.root.geometry("350x250")
        self.root.resizable(False, False)

        self.controller = None
        self._submit_clicked = tk.BooleanVar(value=False)
        self._collected_raw_strings = None

        self.center_frame = tk.Frame(self.root, padx=15, pady=10)
        self.center_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        self.trigger_btn = tk.Button(
            self.center_frame, 
            text="start", 
            command=self._on_start_scenario_click,
            bg="lightyellow"
        )
        self.trigger_btn.grid(row=0, column=0, columnspan=2, sticky="ew", pady=(0, 10))
        
        self.entries = []
        labels_text = ["side A:", "side B:", "side C:"]
        
        for i, text in enumerate(labels_text):
            lbl = tk.Label(self.center_frame, text=text)
            lbl.grid(row=i+1, column=0, sticky="e", pady=2)
            
            entry = tk.Entry(self.center_frame, width=10, state="disabled")
            entry.grid(row=i+1, column=1, pady=2, padx=5)
            self.entries.append(entry)
            
        self.submit_btn = tk.Button(
            self.center_frame, 
            text="submit", 
            command=self._on_submit_click, 
            state="disabled"
        )
        self.submit_btn.grid(row=4, column=0, columnspan=2, pady=10)
        
        self.right_frame = tk.Frame(self.root, padx=10, pady=10)
        self.right_frame.pack(side=tk.RIGHT, fill=tk.BOTH)
        
        self.info_label = tk.Label(self.right_frame, text="awaiting...", font=("Arial", 9, "bold"))
        self.info_label.pack(pady=2)
        
        self.canvas = tk.Canvas(self.right_frame, width=100, height=100, bg="white", highlightthickness=1, highlightbackground="gray")
        self.canvas.pack(anchor="center")

    def set_controller(self, controller):
        self.controller = controller

    def _on_start_scenario_click(self):
        if self.controller:
            self.trigger_btn.config(state="disabled")
            self.controller.start_new_scenario()
            self.trigger_btn.config(state="normal")

    def _on_submit_click(self):
        self._collected_raw_strings = [entry.get().strip() for entry in self.entries]
        self._submit_clicked.set(True)

    def get_user_data(self) -> list[str] | None:
        for entry in self.entries:
            entry.config(state="normal")
            entry.delete(0, tk.END)
        self.submit_btn.config(state="normal")
        
        self.info_label.config(text="awaiting input...")
        
        self._submit_clicked.set(False)
        self._collected_raw_strings = None
        
        self.root.wait_variable(self._submit_clicked)
        
        for entry in self.entries:
            entry.config(state="disabled")
        self.submit_btn.config(state="disabled")
        
        return self._collected_raw_strings

    def draw_triangle(self, coords: list[tuple[int, int]], info_text: str):
        self.canvas.delete("all")
        self.info_label.config(text=info_text)
        
        flat_coords = [coord for point in coords for coord in point]
        self.canvas.create_polygon(flat_coords, fill="#d1e7dd", outline="#0f5132", width=2)

    def show_error(self, message: str):
        self.info_label.config(text="Ошибка!")
        messagebox.showerror("Ошибка приложения", message)

    def run_ui(self):
        self.root.mainloop()

if __name__ == "__main__":
    app = TkinterInterface()
    app.run_ui()
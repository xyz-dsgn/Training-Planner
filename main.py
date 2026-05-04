# training_planner.py

import tkinter as tk
from tkinter import ttk, messagebox
import json
import os
from datetime import datetime
import re

class TrainingPlanner:
    def __init__(self, root):
        self.root = root
        self.root.title("Training Planner - План тренировок")
        self.root.geometry("800x600")
        self.root.resizable(True, True)
        
        # Data storage
        self.trainings = []
        self.data_file = "data.json"
        
        # Training types
        self.training_types = ["Бег", "Плавание", "Велотренировка", "Силовая", "Йога", "Другое"]
        
        # Load existing data
        self.load_data()
        
        # Setup UI
        self.setup_ui()
        
        # Refresh table
        self.refresh_table()
    
    def setup_ui(self):
        # Main container
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Input Frame
        input_frame = ttk.LabelFrame(main_frame, text="Добавить тренировку", padding="10")
        input_frame.grid(row=0, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=5)
        
        # Date input
        ttk.Label(input_frame, text="Дата (ГГГГ-ММ-ДД):").grid(row=0, column=0, sticky=tk.W, padx=5, pady=5)
        self.date_var = tk.StringVar()
        self.date_entry = ttk.Entry(input_frame, textvariable=self.date_var, width=15)
        self.date_entry.grid(row=0, column=1, padx=5, pady=5)
        
        # Training type
        ttk.Label(input_frame, text="Тип тренировки:").grid(row=0, column=2, sticky=tk.W, padx=5, pady=5)
        self.type_var = tk.StringVar()
        self.type_combo = ttk.Combobox(input_frame, textvariable=self.type_var, values=self.training_types, width=20)
        self.type_combo.grid(row=0, column=3, padx=5, pady=5)
        
        # Duration
        ttk.Label(input_frame, text="Длительность (мин):").grid(row=0, column=4, sticky=tk.W, padx=5, pady=5)
        self.duration_var = tk.StringVar()
        self.duration_entry = ttk.Entry(input_frame, textvariable=self.duration_var, width=10)
        self.duration_entry.grid(row=0, column=5, padx=5, pady=5)
        
        # Add button
        self.add_button = ttk.Button(input_frame, text="Добавить тренировку", command=self.add_training)
        self.add_button.grid(row=0, column=6, padx=10, pady=5)
        
        # Filter Frame
        filter_frame = ttk.LabelFrame(main_frame, text="Фильтрация", padding="10")
        filter_frame.grid(row=1, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=5)
        
        # Filter by type
        ttk.Label(filter_frame, text="Фильтр по типу:").grid(row=0, column=0, padx=5, pady=5)
        self.filter_type_var = tk.StringVar(value="Все")
        filter_types = ["Все"] + self.training_types
        self.filter_type_combo = ttk.Combobox(filter_frame, textvariable=self.filter_type_var, values=filter_types, width=20)
        self.filter_type_combo.grid(row=0, column=1, padx=5, pady=5)
        self.filter_type_combo.bind('<<ComboboxSelected>>', lambda e: self.refresh_table())
        
        # Filter by date
        ttk.Label(filter_frame, text="Фильтр по дате:").grid(row=0, column=2, padx=5, pady=5)
        self.filter_date_var = tk.StringVar()
        self.filter_date_entry = ttk.Entry(filter_frame, textvariable=self.filter_date_var, width=15)
        self.filter_date_entry.grid(row=0, column=3, padx=5, pady=5)
        
        # Filter buttons
        self.apply_filter_button = ttk.Button(filter_frame, text="Применить фильтр", command=self.refresh_table)
        self.apply_filter_button.grid(row=0, column=4, padx=5, pady=5)
        
        self.clear_filter_button = ttk.Button(filter_frame, text="Очистить фильтры", command=self.clear_filters)
        self.clear_filter_button.grid(row=0, column=5, padx=5, pady=5)
        
        # Table Frame
        table_frame = ttk.LabelFrame(main_frame, text="Список тренировок", padding="10")
        table_frame.grid(row=2, column=0, columnspan=3, sticky=(tk.W, tk.E, tk.N, tk.S), pady=5)
        
        # Create Treeview
        columns = ("Дата", "Тип тренировки", "Длительность (мин)")
        self.tree = ttk.Treeview(table_frame, columns=columns, show="headings", height=15)
        
        # Define headings
        self.tree.heading("Дата", text="Дата")
        self.tree.heading("Тип тренировки", text="Тип тренировки")
        self.tree.heading("Длительность (мин)", text="Длительность (мин)")
        
        # Define columns
        self.tree.column("Дата", width=150)
        self.tree.column("Тип тренировки", width=200)
        self.tree.column("Длительность (мин)", width=150)
        
        # Add scrollbar
        scrollbar = ttk.Scrollbar(table_frame, orient=tk.VERTICAL, command=self.tree.yview)
        self.tree.configure(yscrollcommand=scrollbar.set)
        
        # Grid layout for table
        self.tree.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        scrollbar.grid(row=0, column=1, sticky=(tk.N, tk.S))
        
        # Buttons Frame
        buttons_frame = ttk.Frame(main_frame)
        buttons_frame.grid(row=3, column=0, columnspan=3, pady=10)
        
        # Delete button
        self.delete_button = ttk.Button(buttons_frame, text="Удалить выбранную тренировку", command=self.delete_training)
        self.delete_button.grid(row=0, column=0, padx=5)
        
        # Save button
        self.save_button = ttk.Button(buttons_frame, text="Сохранить в JSON", command=self.save_data)
        self.save_button.grid(row=0, column=1, padx=5)
        
        # Load button
        self.load_button = ttk.Button(buttons_frame, text="Загрузить из JSON", command=self.load_data)
        self.load_button.grid(row=0, column=2, padx=5)
        
        # Configure grid weights
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        main_frame.columnconfigure(0, weight=1)
        main_frame.rowconfigure(2, weight=1)
        table_frame.columnconfigure(0, weight=1)
        table_frame.rowconfigure(0, weight=1)
    
    def validate_date(self, date_string):
        """Validate date format (YYYY-MM-DD)"""
        pattern = r'^\d{4}-\d{2}-\d{2}$'
        if not re.match(pattern, date_string):
            return False
        try:
            datetime.strptime(date_string, '%Y-%m-%d')
            return True
        except ValueError:
            return False
    
    def validate_duration(self, duration_string):
        """Validate duration (positive number)"""
        try:
            duration = float(duration_string)
            return duration > 0
        except ValueError:
            return False
    
    def add_training(self):
        """Add a new training record"""
        date = self.date_var.get().strip()
        training_type = self.type_var.get()
        duration = self.duration_var.get().strip()
        
        # Validate inputs
        if not date:
            messagebox.showerror("Ошибка", "Пожалуйста, введите дату")
            return
        
        if not self.validate_date(date):
            messagebox.showerror("Ошибка", "Неверный формат даты. Используйте ГГГГ-ММ-ДД")
            return
        
        if not training_type:
            messagebox.showerror("Ошибка", "Пожалуйста, выберите тип тренировки")
            return
        
        if not duration:
            messagebox.showerror("Ошибка", "Пожалуйста, введите длительность")
            return
        
        if not self.validate_duration(duration):
            messagebox.showerror("Ошибка", "Длительность должна быть положительным числом")
            return
        
        # Add training
        training = {
            "date": date,
            "type": training_type,
            "duration": float(duration)
        }
        
        self.trainings.append(training)
        self.save_data()
        self.refresh_table()
        
        # Clear inputs
        self.date_var.set("")
        self.type_var.set("")
        self.duration_var.set("")
        
        messagebox.showinfo("Успех", "Тренировка успешно добавлена!")
    
    def delete_training(self):
        """Delete selected training record"""
        selected_item = self.tree.selection()
        if not selected_item:
            messagebox.showwarning("Предупреждение", "Пожалуйста, выберите тренировку для удаления")
            return
        
        # Get the index of the selected item
        item = selected_item[0]
        values = self.tree.item(item, 'values')
        
        # Find and remove the training
        for i, training in enumerate(self.trainings):
            if (training['date'] == values[0] and 
                training['type'] == values[1] and 
                str(training['duration']) == values[2]):
                del self.trainings[i]
                break
        
        self.save_data()
        self.refresh_table()
        messagebox.showinfo("Успех", "Тренировка удалена!")
    
    def refresh_table(self):
        """Refresh the table with current filters"""
        # Clear current items
        for item in self.tree.get_children():
            self.tree.delete(item)
        
        # Apply filters
        filter_type = self.filter_type_var.get()
        filter_date = self.filter_date_var.get().strip()
        
        filtered_trainings = self.trainings.copy()
        
        # Filter by type
        if filter_type != "Все":
            filtered_trainings = [t for t in filtered_trainings if t['type'] == filter_type]
        
        # Filter by date
        if filter_date:
            filtered_trainings = [t for t in filtered_trainings if t['date'] == filter_date]
        
        # Sort by date
        filtered_trainings.sort(key=lambda x: x['date'])
        
        # Add to table
        for training in filtered_trainings:
            self.tree.insert("", tk.END, values=(
                training['date'],
                training['type'],
                f"{training['duration']:.1f}"
            ))
    
    def clear_filters(self):
        """Clear all filters"""
        self.filter_type_var.set("Все")
        self.filter_date_var.set("")
        self.refresh_table()
    
    def save_data(self):
        """Save data to JSON file"""
        try:
            with open(self.data_file, 'w', encoding='utf-8') as f:
                json.dump(self.trainings, f, ensure_ascii=False, indent=2)
            return True
        except Exception as e:
            messagebox.showerror("Ошибка", f"Не удалось сохранить данные: {str(e)}")
            return False
    
    def load_data(self):
        """Load data from JSON file"""
        if not os.path.exists(self.data_file):
            self.trainings = []
            return
        
        try:
            with open(self.data_file, 'r', encoding='utf-8') as f:
                self.trainings = json.load(f)
            self.refresh_table()
            return True
        except Exception as e:
            messagebox.showerror("Ошибка", f"Не удалось загрузить данные: {str(e)}")
            self.trainings = []
            return False

def main():
    root = tk.Tk()
    app = TrainingPlanner(root)
    root.mainloop()

if __name__ == "__main__":
    main()
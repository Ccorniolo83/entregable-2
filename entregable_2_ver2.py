import tkinter as tk
from tkinter import messagebox, filedialog, simpledialog
import csv
import requests
import json
import os
import pandas as pd
import matplotlib.pyplot as plt

class LoginWindow(tk.Toplevel):
    def __init__(self, parent):
        super().__init__(parent)
        self.title("Inicio de Sesión")
        self.geometry("300x200")

        self.label_user = tk.Label(self, text="Usuario:")
        self.label_user.pack(pady=5)
        self.entry_user = tk.Entry(self)
        self.entry_user.pack(pady=5)

        self.label_password = tk.Label(self, text="Contraseña:")
        self.label_password.pack(pady=5)
        self.entry_password = tk.Entry(self, show="*")
        self.entry_password.pack(pady=5)

        self.button_login = tk.Button(self, text="Iniciar Sesión", command=self.verify_credentials)
        self.button_login.pack(pady=5)

        self.button_register = tk.Button(self, text="Registrar Usuario", command=self.register_user)
        self.button_register.pack(pady=5)

        self.parent = parent

    def load_users(self):
        if os.path.exists('auth_usuarios.json'):
            with open('auth_usuarios.json', 'r') as file:
                users = json.load(file)
                if isinstance(users, dict):
                    return users
        return {}

    def save_users(self, users):
        with open('auth_usuarios.json', 'w') as file:
            json.dump(users, file, indent=4)

    def verify_credentials(self):
        user = self.entry_user.get()
        password = self.entry_password.get()
        users = self.load_users()
        if user in users and users[user] == password:
            self.parent.deiconify()
            self.destroy()
        else:
            messagebox.showerror("Error", "Credenciales incorrectas")

    def register_user(self):
        user = self.entry_user.get()
        password = self.entry_password.get()
        if user and password:
            users = self.load_users()
            if user in users:
                messagebox.showerror("Error", "El usuario ya existe")
            else:
                users[user] = password
                self.save_users(users)
                messagebox.showinfo("Éxito", "Usuario registrado correctamente")
        else:
            messagebox.showerror("Error", "Debe ingresar un usuario y una contraseña")

class App(tk.Tk):
    def __init__(self):
        super().__init__()
        self.withdraw()
        self.title("Gestión de Precios y Ventas")
        self.geometry("800x600")

        # Contenedor principal
        self.container = tk.Frame(self)
        self.container.pack(fill="both", expand=True)

        # Panel de herramientas
        self.toolbar = tk.Frame(self.container)
        self.toolbar.pack(fill="x")

        # Botones de herramientas
        self.button_analizar = tk.Button(self.toolbar, text="Analizar Ventas", command=self.analizar_ventas)
        self.button_analizar.pack(side="left", padx=10, pady=10)

        self.button_actualizar = tk.Button(self.toolbar, text="Actualizar Precios", command=self.actualizar_precios)
        self.button_actualizar.pack(side="left", padx=10, pady=10)

        self.button_graficar = tk.Button(self.toolbar, text="Mostrar Gráfico de Precios", command=self.graficar_historial)
        self.button_graficar.pack(side="left", padx=10, pady=10)

        # Panel de contenido
        self.content = tk.Frame(self.container)
        self.content.pack(fill="both", expand=True)

        self.productos = []

    def analizar_ventas(self):
        # Código para analizar ventas
        archivo = filedialog.askopenfilename(filetypes=[("CSV files", "*.csv")])
    
        if archivo:
            datos = pd.read_csv(archivo)
            datos['Fecha'] = pd.to_datetime(datos['Fecha'])

            # Pedir al usuario un rango de fechas
            fecha_inicio = simpledialog.askstring("Fecha Inicio", "Ingresa la fecha de inicio (YYYY-MM-DD):")
            fecha_fin = simpledialog.askstring("Fecha Fin", "Ingresa la fecha de fin (YYYY-MM-DD):")
        
            # Filtrar los datos por el rango de fechas
            datos_filtrados = datos[(datos['Fecha'] >= fecha_inicio) & (datos['Fecha'] <= fecha_fin)]
            datos_filtrados['Ingresos'] = datos_filtrados['Cantidad'] * datos_filtrados['Precio']
        
            # Resumen de ventas dentro del rango de fechas
            resumen = datos_filtrados.groupby('Producto')[['Cantidad', 'Ingresos']].sum()
            messagebox.showinfo("Ventas por Fecha", f"Ventas en el rango seleccionado:\n{resumen.to_string()}")

    def actualizar_precios(self):
        try:
            respuesta = requests.get('https://api.dolarsi.com/api.php?type=valoresprincipales')
            datos = respuesta.json()
            precio_dolar = datos[0]['casa']['venta']

            for i in range(len(self.productos)):
                self.productos[i][2] = str(float(self.productos[i][2]) * float(precio_dolar))

            with open('productos.csv', 'w', newline='') as archivo:
                writer = csv.writer(archivo)
                writer.writerows(self.productos)

            messagebox.showinfo("Precio actualizado", "El precio ha sido actualizado correctamente.")
        except requests.exceptions.RequestException as e:
            messagebox.showerror("Error", f"No se pudo actualizar el precio: {e}")

    def graficar_historial(self):
        try:
            fechas, precios = [], []
            with open('historial_precios.csv') as file:
                reader = csv.reader(file)
                for row in reader:
                    fechas.append(row[0])
                    precios.append([float(p) for p in row[1:]])
            
            plt.figure(figsize=(10, 5))
            for i in range(len(precios[0])):
                plt.plot(fechas, [p[i] for p in precios], label=f'Producto {i+1}')
            plt.xlabel('Fecha')
            plt.ylabel('Precio en pesos')
            plt.title('Variación de Precios')
            plt.xticks(rotation=45)
            plt.legend()
            plt.tight_layout()
            plt.show()
        except FileNotFoundError:
            messagebox.showerror("Error", "No se encontró el historial de precios.")

    def run(self):
        self.mainloop()

if __name__ == "__main__":
    app = App()
    login_window = LoginWindow(app)
    app.run()

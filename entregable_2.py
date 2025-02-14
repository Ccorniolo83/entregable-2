import tkinter as tk
from tkinter import messagebox
import json
import csv
import requests

from script import actualizar_y_mostrar, analizar_ventas, graficar_historial, login
# creo la clase AplicacionComercial
class AplicacionComercial:
    def __init__(self):
        self.ventana = tk.Tk()
        self.ventana.title("Aplicación Comercial")
        self.usuarios = self.cargar_usuarios()
        self.productos = self.cargar_productos()

        # Creo frame para la validacion de usuario
        self.frame_login = tk.Frame(self.ventana)
        self.frame_login.pack(pady=10)
        self.etiqueta_usuario = tk.Label(self.frame_login, text="Usuario:")
        self.etiqueta_usuario.pack()
        self.entrada_usuario = tk.Entry(self.frame_login)
        self.entrada_usuario.pack()
        self.etiqueta_contraseña = tk.Label(self.frame_login, text="Contraseña:")
        self.etiqueta_contraseña.pack()
        self.entrada_contraseña = tk.Entry(self.frame_login, show="*")
        self.entrada_contraseña.pack()
        self.boton_login = tk.Button(self.frame_login, text="Login", command=self.verificar_credenciales)
        self.boton_login.pack()

        # Creo frame para el listado de productos
        self.frame_productos = tk.Frame(self.ventana)
        self.frame_productos.pack_forget()
        self.etiqueta_productos = tk.Label(self.frame_productos, text="Lista de productos:")
        self.etiqueta_productos.pack()
        self.lista_productos = tk.Listbox(self.frame_productos)
        self.lista_productos.pack()
        self.etiqueta_precio = tk.Label(self.frame_productos, text="Precio:")
        self.etiqueta_precio.pack()
        self.entrada_precio = tk.Entry(self.frame_productos)
        self.entrada_precio.pack()
        self.boton_ver_productos = tk.Button(self.frame_productos, text="Ver productos", command=self.ver_productos)
        self.boton_ver_productos.pack()
        self.boton_modificar_producto = tk.Button(self.frame_productos, text="Modificar producto", command=self.modificar_producto)
        self.boton_modificar_producto.pack()

        # Creo frame para la actializacion de precio de peso a dolar actual
        self.frame_actualizar_precio = tk.Frame(self.ventana)
        self.frame_actualizar_precio.pack_forget()
        self.etiqueta_actualizar_precio = tk.Label(self.frame_actualizar_precio, text="Actualizar precio:")
        self.etiqueta_actualizar_precio.pack()
        self.boton_actualizar_precio = tk.Button(self.frame_actualizar_precio, text="Actualizar precio", command=self.actualizar_precio)
        self.boton_actualizar_precio.pack()

    def cargar_usuarios(self):
        try:
            with open('auth_usuarios.json') as archivo:
                return json.load(archivo)
        except FileNotFoundError:
            return {}

    def cargar_productos(self):
        try:
            with open('productos.csv', 'r') as archivo:
                reader = csv.reader(archivo)
                return list(reader)
        except FileNotFoundError:
            return []

    def verificar_credenciales(self):
        usuario = self.entrada_usuario.get()
        contraseña = self.entrada_contraseña.get()
        if usuario in self.usuarios and self.usuarios[usuario] == contraseña:
            messagebox.showinfo("Login exitoso", "Bienvenido!")
            self.frame_login.pack_forget()
            self.frame_productos.pack(pady=10)
            self.frame_actualizar_precio.pack(pady=10)
        else:
            messagebox.showerror("Login fallido", "Usuario o contraseña incorrectos.")

    def ver_productos(self):
        self.lista_productos.delete(0, tk.END)
        for producto in self.productos:
            self.lista_productos.insert(tk.END, producto)

    def modificar_producto(self):
        indice = self.lista_productos.curselection()
        if indice:
            producto = self.productos[indice[0]]
            self.productos[indice[0]] = [producto[0], producto[1], self.entrada_precio.get()]
            with open('productos.csv', 'w', newline='') as archivo:
                writer = csv.writer(archivo)
                writer.writerows(self.productos)
            messagebox.showinfo("Producto modificado", "El producto ha sido modificado correctamente.")
        else:
            messagebox.showerror("Error", "Seleccione un producto para modificar.")

    def actualizar_precio(self):
        respuesta = requests.get('https://api.dolarsi.com/api.php?type=valoresprincipales')
        datos = respuesta.json()
        precio_dolar = datos[0]['casa']['venta']
        for i in range(len(self.productos)):
            self.productos[i][2] = str(float(self.productos[i][2]) * float(precio_dolar))
        with open('productos.csv', 'w', newline='') as archivo:
            writer = csv.writer(archivo)
            writer.writerows(self.productos)
    def actualizar_precio(self):
        respuesta = requests.get('https://api.dolarsi.com/api.php?type=valoresprincipales')
        datos = respuesta.json()
        precio_dolar = datos[0]['casa']['venta']
        for i in range(len(self.productos)):
            self.productos[i][2] = str(float(self.productos[i][2]) * float(precio_dolar))
        with open('productos.csv', 'w', newline='') as archivo:
            writer = csv.writer(archivo)
            writer.writerows(self.productos)
        messagebox.showinfo("Precio actualizado", "El precio ha sido actualizado correctamente.")

    def run(self):
        self.ventana.mainloop()

# Interfaz gráfica
if __name__ == "__main__":
    app = tk.Tk()
    app.title("Gestión de Precios y Ventas")

    if login():
        tk.Button(app, text="Analizar Ventas", command=analizar_ventas).pack(pady=10)
        tk.Button(app, text="Actualizar Precios", command=actualizar_y_mostrar).pack(pady=10)
        tk.Button(app, text="Mostrar Gráfico de Precios", command=graficar_historial).pack(pady=10)

        app.mainloop()
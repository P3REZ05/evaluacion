from flask import Flask, render_template, request, redirect, url_for, flash
import os
import mysql.connector

# Importa tu módulo database
import database as db

template_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), 'templates'))
app = Flask(__name__, template_folder=template_dir)
app.secret_key = 'your_secret_key'

# Define el tamaño de la página
PAGE_SIZE = 10

# Función para obtener productos paginados
def get_productos_paginados(pagina):
    offset = (pagina - 1) * PAGE_SIZE
    cursor = db.database.cursor()
    cursor.execute(f"SELECT * FROM producto LIMIT {PAGE_SIZE} OFFSET {offset}")
    productos = cursor.fetchall()
    
    # Convertir datos a diccionario
    insertObject = []
    columnNames = [column[0] for column in cursor.description]
    
    for record in productos:
        insertObject.append(dict(zip(columnNames, record)))
    
    cursor.close()
    return insertObject

@app.route('/inventario')
def inventario():
    pagina = request.args.get('pagina', 1, type=int)
    productos = get_productos_paginados(pagina)
    
    cursor = db.database.cursor()
    cursor.execute("SELECT * FROM proveedores")
    proveedores = cursor.fetchall()
    
    # Convertir datos a diccionario
    proveedores_dict = []
    columnNames = [column[0] for column in cursor.description]
    
    for record in proveedores:
        proveedores_dict.append(dict(zip(columnNames, record)))
    
    cursor.close()
    return render_template('inventario.html', data=productos, proveedores=proveedores_dict, pagina=pagina)

@app.route('/inventario/guardar', methods=['POST'])
def guardar_producto():
    nombre_producto = request.form['nombre_producto']
    descripcion_producto = request.form['descripcion_producto']
    valor_producto = request.form['valor_producto']
    cantidad_inicial = request.form['cantidad_inicial']
    ID_proveedor = request.form['ID_proveedor']

    if nombre_producto and descripcion_producto and valor_producto and cantidad_inicial and ID_proveedor:
        try:
            cursor = db.database.cursor()
            sql = "INSERT INTO producto (nombre_producto, descripcion_producto, valor_producto, cantidad_inicial, ID_proveedor) VALUES (%s, %s, %s, %s, %s)"
            data = (nombre_producto, descripcion_producto, valor_producto, cantidad_inicial, ID_proveedor)
            cursor.execute(sql, data)
            db.database.commit()
        except mysql.connector.errors.IntegrityError:
            flash('Error: El producto ya existe.', 'error')
        except mysql.connector.errors.DataError:
            flash('Error: Uno de los valores es demasiado largo.', 'error')

    return redirect(url_for('inventario'))

@app.route('/eliminar_producto/<int:id>')
def eliminar_producto(id):
    cursor = db.database.cursor()
    sql = "DELETE FROM producto WHERE ID_producto = %s"
    data = (id,)
    cursor.execute(sql, data)
    db.database.commit()
    return redirect(url_for('inventario'))

@app.route('/editar_producto/<int:id>', methods=['POST'])
def editar_producto(id):
    nombre_producto = request.form['nombre_producto']
    descripcion_producto = request.form['descripcion_producto']
    valor_producto = request.form['valor_producto']
    cantidad_inicial = request.form['cantidad_inicial']
    ID_proveedor = request.form['ID_proveedor']

    if nombre_producto and descripcion_producto and valor_producto and cantidad_inicial and ID_proveedor:
        try:
            cursor = db.database.cursor()
            sql = "UPDATE producto SET nombre_producto = %s, descripcion_producto = %s, valor_producto = %s, cantidad_inicial = %s, ID_proveedor = %s WHERE ID_producto = %s"
            data = (nombre_producto, descripcion_producto, valor_producto, cantidad_inicial, ID_proveedor, id)
            cursor.execute(sql, data)
            db.database.commit()
        except mysql.connector.errors.IntegrityError:
            flash('Error: El producto ya existe.', 'error')
        except mysql.connector.errors.DataError:
            flash('Error: Uno de los valores es demasiado largo.', 'error')

    return redirect(url_for('inventario'))

# Filtrar productos
@app.route('/filtrar_productos', methods=['POST'])
def filtrar_productos():
    proveedor = request.form['proveedor']
    precio = request.form['precio']
    cantidad = request.form['cantidad']
    
    query = "SELECT * FROM producto WHERE 1=1"
    filters = []
    
    if proveedor:
        query += " AND ID_proveedor = %s"
        filters.append(proveedor)
    if precio:
        query += " AND valor_producto <= %s"
        filters.append(precio)
    if cantidad:
        query += " AND cantidad_inicial >= %s"
        filters.append(cantidad)
    
    cursor = db.database.cursor()
    cursor.execute(query, tuple(filters))
    productos = cursor.fetchall()
    
    # Convertir datos a diccionario
    productos_dict = []
    columnNames = [column[0] for column in cursor.description]
    
    for record in productos:
        productos_dict.append(dict(zip(columnNames, record)))
    
    cursor.close()
    return render_template('productos_filtrados.html', data=productos_dict)

if __name__ == '__main__':
    app.run(debug=True)

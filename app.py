from flask import Flask, render_template, jsonify, request, Response
import pymysql
from datetime import datetime
import os

app = Flask(__name__)

app.config["MYSQL_HOST"] = "localhost"
app.config["MYSQL_USER"] = "root"
app.config["MYSQL_PASSWORD"] = ""
app.config["MYSQL_DB"] = "ar_furniture"
app.config["MYSQL_CURSORCLASS"] = "DictCursor"

db = pymysql.connect(
    host=app.config["MYSQL_HOST"],
    user=app.config["MYSQL_USER"],
    password=app.config["MYSQL_PASSWORD"],
    db=app.config["MYSQL_DB"],
)


app.config["DEBUG"] = True


class DatabaseConnection:
    def _enter_(self):
        self.connection = db.cursor()
        return self.connection

    def _exit_(self, exc_type, exc_value, traceback):
        self.connection.close()


@app.route("/")
def home():
    data = {"header": "dashboard"}
    return render_template("dashboard.html", header_data=data)


@app.route("/barang")
def barang():
    try:
        # with DatabaseConnection() as cursor:
        cursor = db.cursor()
        cursor.execute("SELECT * FROM furniture")
        res = cursor.fetchall()

        data = {"header": "barang", "result": res}

        return render_template("barang.html", header_data=data)
    except db.Error as e:
        db.rollback()
        error_message = "An error occurred: " + str(e)
        response = jsonify({"status": "error", "message": error_message})
        return response


@app.route("/api-barang", methods=["GET"])
def api_barang():
    try:
        cursor = db.cursor()
        cursor.execute("SELECT * FROM furniture")
        res = cursor.fetchall()

        # Create a list to hold dictionaries for each row
        data_list = []

        # Iterate through the result set and create a dictionary for each row
        for row in res:
            data_dict = {
                "id": row[0],  # Replace "id" with the actual column name
                "nama_produk": row[
                    1
                ],  # Replace "nama_produk" with the actual column name
                "deskripsi": row[2],  # Replace "deskripsi" with the actual column name
                "objek_3d": row[3],  # Replace "objek_3d" with the actual column name
                "panjang": row[4],  # Replace "panjang" with the actual column name
                "tinggi": row[5],  # Replace "tinggi" with the actual column name
                "lebar": row[6],  # Replace "lebar" with the actual column name
                "gambar": row[7],  # Replace "gambar" with the actual column name
            }
            data_list.append(data_dict)

        # Create a dictionary with the result list
        data = {"result": data_list}

        response = jsonify(data)
        return response
    except db.Error as e:
        db.rollback()
        error_message = "An error occurred: " + str(e)
        response = jsonify({"status": "error", "message": error_message})
        return response


@app.route("/input_barang", methods=["POST"])
def input_barang():
    if request.method == "POST":
        nama_barang = request.form["nama_barang"]
        panjang = request.form["panjang"]
        lebar = request.form["lebar"]
        tinggi = request.form["tinggi"]
        deskripsi = request.form["deskripsi"]

        image = request.files["gambar"]
        objek_3d = request.files["objek_3d"]

        try:
            current_datetime = datetime.now()
            formatted_datetime = current_datetime.strftime("%Y%m%d%H%M%S")

            image_name = "img" + formatted_datetime + ".jpg"
            objek_name = "obj" + formatted_datetime + ".obj"

            image.save(os.path.join("data", image_name))
            objek_3d.save(os.path.join("data", objek_name))

            cursor = db.cursor()
            cursor.execute(
                "INSERT INTO furniture(nama_produk, deskripsi, objek_3d, panjang, tinggi, lebar, gambar) VALUES (%s,%s,%s,%s,%s,%s,%s)",
                (
                    nama_barang,
                    deskripsi,
                    objek_name,
                    panjang,
                    tinggi,
                    lebar,
                    image_name,
                ),
            )

            db.commit()
            cursor.close()

            response = jsonify({"status": "success"})
            return response

        except db.Error as e:
            db.rollback()
            error_message = "An error occurred: " + str(e)
            print(error_message)
            response = jsonify({"status": "error", "message": error_message})
            return response


@app.route("/update_barang", methods=["POST"])
def update_barang():
    if request.method == "POST":
        id = request.form["id"]
        nama = request.form["nama_barang_new"]
        panjang = request.form["panjang_new"]
        lebar = request.form["lebar_new"]
        tinggi = request.form["tinggi_new"]
        deskripsi = request.form["deskripsi_new"]

        try:
            cursor = db.cursor()
            cursor.execute(
                "UPDATE furniture SET nama_produk = %s, deskripsi = %s, panjang = %s, tinggi = %s, lebar = %s WHERE id = %s",
                (
                    nama,
                    deskripsi,
                    panjang,
                    tinggi,
                    lebar,
                    id,
                ),
            )

            db.commit()
            cursor.close()

            response = jsonify({"status": "success"})
            return response

        except db.Error as e:
            db.rollback()
            error_message = "An error occurred: " + str(e)
            print(error_message)
            response = jsonify({"status": "error", "message": error_message})
            return response


@app.route("/hapus_objek", methods=["POST"])
def hapus_objek():
    if request.method == "POST":
        id = request.form["id"]
        gambar = request.form["gambar"]
        objek = request.form["objek"]

        try:
            cursor = db.cursor()
            cursor.execute("DELETE FROM furniture WHERE id = %s", (id,))
            db.commit()

            if os.path.exists("data/" + gambar) and os.path.exists("data/" + objek):
                os.remove("data/" + gambar)
                os.remove("data/" + objek)

            response = jsonify(
                {
                    "status": "success",
                    "msg": "Berhasil Hapus objek!",
                }
            )
            return response

        except db.Error as e:
            db.rollback()
            error_message = "An error occurred: " + str(e)
            response = jsonify({"status": "error", "message": error_message})
            return response


if __name__ == "__main__":
    app.run(debug=True)

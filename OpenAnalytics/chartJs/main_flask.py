from flask import Flask, render_template, jsonify
from flask_cors import CORS, cross_origin
from OpenAnalytics.AirTable.airTable_main import consultorioFlask

app = Flask(__name__)
# CORS(app)
data_server = consultorioFlask()

# @app.route('/')
# def hello_world():
#     df = consultorio_2021.getBalanceCuentasDataFrame()
#     data = {"Efectivo": df["Efectivo Total"].sum(), "Diana": df["Diana BBVA Total"].sum(), "Mercado Pago": df["Mercado Pago Total"].sum(), "Santander": df["Santander Total"].sum(), "Hirvin":df["Hirvin (BBVA) Total"].sum()}
#     return render_template("index.html", data_cuentas=data)



@app.route('/saldos')
@cross_origin()
def get_saldos():
    # data = {"efectivo":15, "dianaBBVA":25, "hirvinBBVA":35, "santander":45}
    return jsonify(data_server.processBalance())

# @app.route('/dataBalance')
# def get_data():
#     df = consultorio_2021.getBalanceDataFrame()
#     # genereta chart object
#     datasets_balance = [
#         {
#             "label": "Ingresos",
#             "backgroundColor": "#DEE120",
#             "borderColor": "#DEE120",
#             "data": df["Pago Final (Registrado)"].tolist(),
#         },
#         {
#             "label": "Gastos",
#             "backgroundColor": "#2920E1",
#             "borderColor": "#2920E1",
#             "data": df["Cantidad"].tolist(),
#         },
#     ]

#     # get data ganancia
#     datasets_ganancia = [
#         {
#             "label": "Ganancia",
#             "backgroundColor": "#DEE120",
#             "borderColor": "#DEE120",
#             "data": df["ganancia"].tolist(),
#         }
#     ]

#     data_balance = {
#         "labels": df["month_name"].tolist(),
#         "datasets": datasets_balance,
#     }
#     data_ganancia = {
#         "labels": df["month_name"].tolist(),
#         "datasets": datasets_ganancia,
#     }

#     data = {"dataBalance": data_balance, "dataGanancias": data_ganancia}
#     return jsonify({"data":data})

if __name__ == '__main__':
    app.run(debug=True)
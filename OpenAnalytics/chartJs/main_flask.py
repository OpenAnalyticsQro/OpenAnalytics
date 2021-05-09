from flask import Flask, render_template, jsonify
from OpenAnalytics.AirTable.airTable_main import consultorio2021

app = Flask(__name__)
consultorio_2021 = consultorio2021()



@app.route('/')
def hello_world():
    df = consultorio_2021.getBalanceCuentasDataFrame()
    data = {"Efectivo": df["Efectivo Total"].sum(), "Diana": df["Diana Total"].sum(), "Mercado Pago": df["Mercado Pago Total"].sum(), "Santander": df["Santander Total"].sum(), "Hirvin":df["Hirvin (BBVA) Total"].sum()}
    return render_template("index.html", data_cuentas=data)


@app.route('/dataBalance')
def get_data():
    df = consultorio_2021.getBalanceDataFrame()
    # genereta chart object
    datasets_balance = [
        {
            "label": "Ingresos",
            "backgroundColor": "#DEE120",
            "borderColor": "#DEE120",
            "data": df["Pago Final (Registrado)"].tolist(),
        },
        {
            "label": "Gastos",
            "backgroundColor": "#2920E1",
            "borderColor": "#2920E1",
            "data": df["Cantidad"].tolist(),
        },
    ]

    # get data ganancia
    datasets_ganancia = [
        {
            "label": "Ganancia",
            "backgroundColor": "#DEE120",
            "borderColor": "#DEE120",
            "data": df["ganancia"].tolist(),
        }
    ]

    data_balance = {
        "labels": df["month_name"].tolist(),
        "datasets": datasets_balance,
    }
    data_ganancia = {
        "labels": df["month_name"].tolist(),
        "datasets": datasets_ganancia,
    }

    data = {"dataBalance": data_balance, "dataGanancias": data_ganancia}
    return jsonify({"data":data})

if __name__ == '__main__':
    app.run(debug=True)
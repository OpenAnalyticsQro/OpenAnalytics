from numpy.lib.shape_base import column_stack
from OpenAnalytics.AirTable import air_table_log as log
import matplotlib.pyplot as plt
import pandas as pd
import requests
from os import EX_SOFTWARE, rename, system
from OpenAnalytics.ENV import (
    ENV_AIR_TABLE_PATH,
    AIR_TABLE_ID_DATA,
    AIR_TABLE_API_KEY_DATA,
)
from dotenv import load_dotenv
from os import getenv
from numpy import NaN

log.debug("Airtable testing")

AIR_TABLE_SUCCESS_CODE = 200

AIR_TABLE_ERRORS_CODES = {
    400: "Bad Request, The request encoding is invalid; the request can't be parsed as a valid JSON.",
    401: "Unauthorized, Accessing a protected resource without authorization or with invalid credentials.",
    402: "Payment Required, The account associated with the API key making requests hits a quota that can be increased by upgrading the Airtable account plan.",
    403: "Forbidden, Accessing a protected resource with API credentials that don't have access to that resource.",
    404: "Not Found, Route or resource is not found. This error is returned when the request hits an undefined route, or if the resource doesn't exist (e.g. has been deleted).",
    413: "Request Entity Too LargeThe request exceeded the maximum allowed payload size. You shouldn't encounter this under normal use.",
    422: "Invalid RequestThe request data is invalid. This includes most of the base-specific validations. You will receive a detailed error message and code pointing to the exact issue.",
    500: "Internal Server Error, The server encountered an unexpected condition.",
    502: "Bad Gateway, Airtable's servers are restarting or an unexpected outage is in progress. You should generally not receive this error, and requests are safe to retry.",
    503: "Service Unavailable, The server could not process your request in time. The server could be temporarily unavailable, or it could have timed out processing your request. You should retry the request with backoffs.",
}

AIR_TABLE_NAME = "Consultas"
AIR_TABLE_ENDPOINT = "https://api.airtable.com/v0/{}/{}"
AIR_TABLE_ENDPOINT_RECORD = "https://api.airtable.com/v0/{}/{}/{}"

headers = {"Authorization": f"Bearer {getenv(AIR_TABLE_API_KEY_DATA)}"}

params = {"maxRecords": None, "view": "Consultas"}


class airTableApi(object):
    __airTableId = None
    __airTableApiKey = None

    def __init__(self, airTableID=None, airTableApiKey=None):
        load_dotenv(ENV_AIR_TABLE_PATH)
        if airTableApiKey is None:
            self.__airTableApiKey = getenv(AIR_TABLE_API_KEY_DATA)
        else:
            self.__airTableApiKey = airTableApiKey
        if airTableID is None:
            self.__airTableId = getenv(AIR_TABLE_ID_DATA)
        else:
            self.__airTableId = airTableID
        log.debug(
            f"New airTable, TableID: {self.__airTableId}  APIKey: {self.__airTableApiKey}"
        )

    def validEndPointParameters(self):
        if self.__airTableId is None:
            log.error(f"airTableApi()- invalid airTableId: {self.__airTableId}")
            return False
        if self.__airTableApiKey is None:
            log.error(f"airTableApi()- invalid airTableApiKey: {self.__airTableApiKey}")
            return False
        return True

    def getListRecords(
        self,
        tableName=None,
        maxRecords=None,
        view=None,
        pageSize=None,
        sort=None,
        fields=None,
        filterByFormula=None,
        offset=None,
    ):
        if tableName is None:
            log.error(f"get_list_records()- invalid tableName: {tableName}")
            return None
        if self.validEndPointParameters() is False:
            return None
        air_table_endpoint = AIR_TABLE_ENDPOINT.format(self.__airTableId, tableName)

        log.debug(f"endpoint: {air_table_endpoint}")
        air_table_headers = {"Authorization": f"Bearer {self.__airTableApiKey}"}
        air_table_params = {
            "maxRecords": maxRecords,
            "view": view,
            "pageSize": pageSize,
            "sort": sort,
            "fields": fields,
            "filterByFormula": filterByFormula,
            "offset": offset,
        }

        response = requests.get(
            air_table_endpoint, headers=air_table_headers, params=air_table_params
        )
        if response.status_code != AIR_TABLE_SUCCESS_CODE:
            log.error(AIR_TABLE_ERRORS_CODES[response.status_code])
            return None

        return response.json()

    def retriveRecord(self, tableName=None, recordId=None):
        if tableName is None:
            log.error(f"retriveRecord()- invalid tableName: {tableName}")
            return None
        if recordId is None:
            log.error(f"retriveRecord() - invalid recordID: {recordId}")
        if self.validEndPointParameters() is False:
            return None
        air_table_endpoint = AIR_TABLE_ENDPOINT_RECORD.format(
            self.__airTableId, tableName, recordId
        )
        # log.debug(f"endpoint: {air_table_endpoint}")
        air_table_headers = {"Authorization": f"Bearer {self.__airTableApiKey}"}
        response = requests.get(air_table_endpoint, headers=air_table_headers)
        if response.status_code != AIR_TABLE_SUCCESS_CODE:
            log.error(AIR_TABLE_ERRORS_CODES[response.status_code])
            return None

        return response.json()

    def getDF(self, table=None, view=None, filter=None):
        offset = 0
        buffer = []
        while offset is not None:
            data = self.getListRecords(tableName=table, view=view, offset=offset)
            # print(data)
            if data is not None:
                for row in data["records"]:
                    row.update(row.get("fields"))
                    row.pop("fields")
                    buffer.append(row)
            offset = data.get("offset")
            log.debug(f"getConsultasDF() - fetching next page, offset: {offset}")
        df = pd.DataFrame(buffer)
        if filter is None:
            return df
        else:
            return df[filter]


class pacientesConsultorioTable(airTableApi):
    __pacientesTable = "Pacientes"

    def __init__(self):
        super().__init__()

    def getPacienteSimpleNameFromRecordId(self, recordId=None):
        data = self.retriveRecord(tableName=self.__pacientesTable, recordId=recordId)
        if data is None:
            return None
        return f'{data["fields"].get("Nombre")} {data["fields"].get("Apellidos")}'


class pagosConsultorioTable(airTableApi):
    __pagosTable = "Pagos"
    # views
    __pagosView = "Pagos"

    def __init__(self):
        super().__init__()

    def getPagosDF(self, save_to=None):
        df = self.getDF(
            table=self.__pagosTable,
            view=self.__pagosView,
            filter=["Fecha", "Concepto", "Pago", "Cantidad", "Cuenta de Pago", "IVA"],
        )
        df.Fecha = pd.to_datetime(df.Fecha)
        df["year"] = df.Fecha.dt.year
        df["month"] = df.Fecha.dt.month
        df["week"] = df.Fecha.dt.isocalendar().week
        df["month_name"] = df.Fecha.dt.strftime("%B %Y")
        df["week_name"] = df.Fecha.dt.strftime("Semana-%W-%Y")
        df["Cantidad"] = pd.to_numeric(df["Cantidad"])
        if save_to is not None:
            df.to_csv(save_to)
        return df


class traspasosCuentasTable(airTableApi):
    __traspasosTable = "Traspasos Cuentas"
    # viewa
    __traspasosView = "Traspasos"

    def __init__(self):
        super().__init__()

    def getTraspasosDF(self, save_to=None):
        df = self.getDF(
            table=self.__traspasosTable,
            view=self.__traspasosView,
            filter=["id", "Fecha", "Cantidad", "Cuenta retiro", "Cuenta Abono",],
        )
        df.Fecha = pd.to_datetime(df.Fecha)
        df["year"] = df.Fecha.dt.year
        df["month"] = df.Fecha.dt.month
        df["week"] = df.Fecha.dt.isocalendar().week
        df["month_name"] = df.Fecha.dt.strftime("%B %Y")
        df["week_name"] = df.Fecha.dt.strftime("Semana-%W-%Y")
        if save_to is not None:
            df.to_csv(save_to)
        # print(df)
        return df


class consultasConsultorioTable(airTableApi):
    __consultasTable = "Consultas"
    # views
    __pacientesJennyView = "PX Jenny"
    __consultasView = "Consultas"

    def __init__(self):
        super().__init__()

    def getPacientesJennyView(self):
        pacientesTable = pacientesConsultorioTable()
        data = self.getListRecords(
            tableName=self.__consultasTable, view=self.__pacientesJennyView
        )
        total = 0
        if data is not None:
            for row in data["records"]:
                if row["fields"].get("Paciente") is not None:
                    # print(row["fields"])
                    name = pacientesTable.getPacienteSimpleNameFromRecordId(
                        recordId=row["fields"]["Paciente"][0]
                    )
                else:
                    name = ""
                if row["fields"].get("Pago Final (Registrado)") is not None:
                    pago_final = float(row["fields"]["Pago Final (Registrado)"])
                else:
                    pago_final = 0
                fecha = row["fields"]["Fecha"]
                ganancia = float(row["fields"]["Ganancia Especialista"])
                comision = row["fields"]["Comision Especialista"]
                dentista = row["fields"]["Dentista"]
                # print(
                #     f"{fecha}   {name:35} ${pago_final:8.2f} {dentista} {comision:5} ${ganancia:8.2f}"
                # )
                total += float(row["fields"]["Ganancia Especialista"])
            # print(f"la ganancai de jenny es: {total}")

    def getConsultasDF(self, save_to=None):
        df = self.getDF(
            table=self.__consultasTable,
            view=self.__consultasView,
            filter=[
                "id",
                "Paciente",
                "Fecha",
                "Tratamiento",
                "Dentista",
                "Forma Pago",
                "Pago Final (Registrado)",
            ],
        )
        df.Fecha = pd.to_datetime(df.Fecha)
        df["year"] = df.Fecha.dt.year
        df["month"] = df.Fecha.dt.month
        df["week"] = df.Fecha.dt.isocalendar().week
        df["month_name"] = df.Fecha.dt.strftime("%B %Y")
        df["week_name"] = df.Fecha.dt.strftime("Semana-%W-%Y")
        df["Pago Final (Registrado)"] = pd.to_numeric(df["Pago Final (Registrado)"])
        if save_to is not None:
            df.to_csv(save_to)
        return df


class consultorio2021:
    def __init__(self, from_data=False):
        if from_data is False:
            self.consultasTable = consultasConsultorioTable()
            self.pagosTable = pagosConsultorioTable()
            self.traspasosTable = traspasosCuentasTable()
            self.__from_data = from_data
        else:
            # load form files
            pass

    def getBalanceDataFrame(self):
        consultas_df = self.consultasTable.getConsultasDF()
        pagos_df = self.pagosTable.getPagosDF()

        # group data frames
        df_consultas_month = consultas_df.groupby(
            ["month_name"], sort=False, as_index=False
        )[["Pago Final (Registrado)"]].sum()
        df_pagos_month = pagos_df.groupby(["month_name"], sort=False, as_index=False)[
            ["Cantidad"]
        ].sum()

        # generate balance
        df_balance_month = pd.merge(
            df_consultas_month, df_pagos_month, on="month_name", how="outer"
        )
        df_balance_month["ganancia"] = (
            df_balance_month["Pago Final (Registrado)"] - df_balance_month["Cantidad"]
        )

        return df_balance_month

    # period => "month_name|week_name"
    def getBalanceCuentasDataFrame(self, period="month_name"):
        consultas_df = self.consultasTable.getConsultasDF()
        pagos_df = self.pagosTable.getPagosDF()
        traspasos_df = self.traspasosTable.getTraspasosDF()

        # procesar consultas
        # consultas_df
        data_consultas = consultas_df.groupby(
            [period, "Forma Pago"], as_index=False, sort=False
        )["Pago Final (Registrado)"].sum()
        data_consultas.set_index("Forma Pago", inplace=True)
        # print(consultas_df)

        # procesas pagos
        data_pagos = pagos_df.groupby(
            [period, "Cuenta de Pago"], as_index=False, sort=False
        )["Cantidad"].sum()
        data_pagos.set_index("Cuenta de Pago", inplace=True)
        # print(data_pagos)

        # Procesa IVA
        data_iva = pagos_df.groupby(
            [period, "Cuenta de Pago"], as_index=False, sort=False
        )["IVA"].sum()
        data_iva.set_index("Cuenta de Pago", inplace=True)
        # print(data_iva)

        # procesar traspasos
        data_retiros = traspasos_df.groupby(
            [period, "Cuenta retiro"], as_index=False, sort=False
        )["Cantidad"].sum()
        data_retiros.set_index("Cuenta retiro", inplace=True)
        # print(data_retiros)

        data_abonos = traspasos_df.groupby(
            [period, "Cuenta Abono"], as_index=False, sort=False
        )["Cantidad"].sum()
        data_abonos.set_index("Cuenta Abono", inplace=True)
        # print(data_abonos)

        estado_cuentas = pd.DataFrame()
        estado_cuentas[period] = ""

        # procesar Efectivo
        cuentas = [
            "Efectivo",
            "Diana BBVA",
            "Clip",
            "Santander",
            "Hirvin (BBVA)",
            "Caja Fuerte",
            "Mercado Pago",
        ]
        for cuenta in cuentas:
            # Procesar consultas
            if cuenta in data_consultas.index:
                left_data = data_consultas.loc[[f"{cuenta}"]].rename(
                    columns={"Pago Final (Registrado)": f"Ingresos {cuenta}"}
                )
                estado_cuentas = pd.merge(
                    estado_cuentas,
                    left_data,
                    left_on=period,
                    right_on=period,
                    how="outer",
                )
            else:
                estado_cuentas[f"Ingresos {cuenta}"] = NaN
            # Procesar Pagos
            if cuenta in data_pagos.index:
                rigth_data = data_pagos.loc[[f"{cuenta}"]].rename(
                    columns={"Cantidad": f"Pagos {cuenta}"}
                )
                estado_cuentas = pd.merge(
                    estado_cuentas,
                    rigth_data,
                    left_on=period,
                    right_on=period,
                    how="outer",
                )
            else:
                estado_cuentas[f"Pagos {cuenta}"] = NaN
            # Procesar IVA
            if cuenta in data_iva.index:
                rigth_data = data_iva.loc[[f"{cuenta}"]].rename(
                    columns={"IVA": f"IVA {cuenta}"}
                )
                estado_cuentas = pd.merge(
                    estado_cuentas,
                    rigth_data,
                    left_on=period,
                    right_on=period,
                    how="outer",
                )
            else:
                estado_cuentas[f"IVA {cuenta}"] = NaN
            # Procesar Retiros
            if cuenta in data_retiros.index:
                retiros_data = data_retiros.loc[[f"{cuenta}"]].rename(
                    columns={"Cantidad": f"Retiros {cuenta}"}
                )
                estado_cuentas = pd.merge(
                    estado_cuentas,
                    retiros_data,
                    left_on=period,
                    right_on=period,
                    how="outer",
                )
            else:
                estado_cuentas[f"Retiros {cuenta}"] = NaN
            # Procesar Abonos
            if cuenta in data_abonos.index:
                abonos_data = data_abonos.loc[[f"{cuenta}"]].rename(
                    columns={"Cantidad": f"Abonos {cuenta}"}
                )
                estado_cuentas = pd.merge(
                    estado_cuentas,
                    abonos_data,
                    left_on=period,
                    right_on=period,
                    how="outer",
                )
            else:
                estado_cuentas[f"Abonos {cuenta}"] = NaN

            estado_cuentas.fillna(0, inplace=True)
            estado_cuentas[f"{cuenta} Total"] = (
                estado_cuentas[f"Ingresos {cuenta}"]
                - estado_cuentas[f"Pagos {cuenta}"]
                + estado_cuentas[f"Abonos {cuenta}"]
                - estado_cuentas[f"Retiros {cuenta}"]
                - estado_cuentas[f"IVA {cuenta}"]
            )
            # Print
            # log.info(
            #     f"{cuenta}, Ingresos: {estado_cuentas[f'Ingresos {cuenta}'].sum()} Pagos: {estado_cuentas[f'Pagos {cuenta}'].sum()} Abonos: {estado_cuentas[f'Abonos {cuenta}'].sum()} Retiros: {estado_cuentas[f'Retiros {cuenta}'].sum()} Total: {estado_cuentas[f'{cuenta} Total'].sum()}"
            # )

        # actualizado totales errores
        # clip se deposita en la cuenta de Diana BBVA
        estado_cuentas["Diana BBVA Total"] = (
            estado_cuentas["Diana BBVA Total"] + estado_cuentas["Clip Total"]
        )

        log.info(
            f"Totales, Efectivo:{estado_cuentas[f'Efectivo Total'].sum()} Diana BBVA: {estado_cuentas['Diana BBVA Total'].sum()} Hirvin:{estado_cuentas['Hirvin (BBVA) Total'].sum()} Santander: {estado_cuentas['Santander Total'].sum()} Mercado Pago: {estado_cuentas['Mercado Pago Total'].sum()} Caja Fuerte: {estado_cuentas['Caja Fuerte Total'].sum()}"
        )

        return estado_cuentas


class consultorioFlask(object):
    def __init__(self):
        self.__consultorio = consultorio2021()
        self.__balance = None
        self.__cuentas = cuentas = [
            "Efectivo",
            "Diana BBVA",
            "Clip",
            "Santander",
            "Hirvin (BBVA)",
            "Caja Fuerte",
            "Mercado Pago",
        ]
        self._cuentas_color = { 
            "Efectivo":"#009688",
            "Diana BBVA":"#4fc3f7",
            "Clip":"#ffa726",
            "Santander":"#c62828",
            "Hirvin (BBVA)":"#7986cb",
            "Caja Fuerte":"#7986cb",
            "Mercado Pago":"#fdd835",
        }

    def getConsultorioDF(self):
        return self.__consultorio

    def processBalance(self):
        self.__balance = self.__consultorio.getBalanceCuentasDataFrame(
            period="month_name"
        )
        # print(self.__balance["Efectiv Total"].sum().round(2))
        data = {}
        chart_labels = (self.__balance["month_name"].to_list(),)
        for cuenta in self.__cuentas:
            data[cuenta] = {}
            data[cuenta]["table"] = []
            data[cuenta]["titulo"] = cuenta
            data[cuenta]["total"] = self.__balance[f"{cuenta} Total"].sum().round(2)
            data[cuenta]["data_graph"] = {
                "datasets": [
                {
                    "backgroundColor": self._cuentas_color[cuenta],
                    "data": self.__balance[f"{cuenta} Total"].cumsum().to_list(),
                    "borderWidth":1,
                    "fill": True,
                    "cubicInterpolationMode": 'monotone',
                },
                
                ],
                "labels": chart_labels[0],
            }
            # Calculando ingresos totales
            if "Ingresos Total" in self.__balance.keys():
                self.__balance["Ingresos Total"] = (
                    self.__balance[f"Ingresos {cuenta}"]
                    + self.__balance["Ingresos Total"]
                )
            else:
                self.__balance["Ingresos Total"] = self.__balance[f"Ingresos {cuenta}"]
            # calculando Pagos Totales (se suma cada cuenta por ciclo)
            if "Pagos Total" in self.__balance.keys():
                self.__balance[f"Pagos Total"] = (
                    self.__balance[f"Pagos {cuenta}"] + self.__balance["Pagos Total"]
                )
            else:
                self.__balance[f"Pagos Total"] = self.__balance[f"Pagos {cuenta}"]

            # generando tablas
            # print(f"procesing {cuenta}")
            for index in self.__balance.index:
                row = {
                    "period": self.__balance["month_name"].iloc[index],
                    "ingresos": self.__balance[f"Ingresos {cuenta}"].iloc[index],
                    "abonos": self.__balance[f"Abonos {cuenta}"].iloc[index],
                    "pagos": self.__balance[f"Pagos {cuenta}"].iloc[index],
                    "retiros": self.__balance[f"Retiros {cuenta}"].iloc[index],
                }
                # print(row)
                data[cuenta]["table"].append(row)
        
        # calculado Fondo Total
        print(self.__balance["Ingresos Total"])
        print(self.__balance["Pagos Total"])
        self.__balance["Fondo"] = self.__balance["Ingresos Total"] - self.__balance["Pagos Total"]
        print(self.__balance["Fondo"])
        print(self.__balance["Fondo"].cumsum().to_list())

        # generando Totales Chart
        data["Totales"] = {}
        data["Totales"]["data_graph"] = {
            "labels": chart_labels[0],
            "datasets": [
                # Ingresos Totales
                {
                    "label": "Ingresos",
                    "data": self.__balance["Ingresos Total"].to_list(),
                    "borderColor": "#0091ea",
                    "backgroundColor": "#80d8ff",
                },
                #  Pagos Totales
                {
                    "label": "Pagos",
                    "data": self.__balance["Pagos Total"].to_list(),
                    "borderColor": "#e040fb",
                    "backgroundColor": "#ea80fc",
                },
            ],
        }
        # generando Totales Chart
        data["Totales2"] = {}
        data["Totales2"]["data_graph"] = {
            "labels": chart_labels[0],
            "datasets": [
                {
                    "type": "line",
                    "label": "primera",
                    "borderColor": "#e040fb",
                    "data": self.__balance["Fondo"].cumsum().to_list(),
                    "borderWidth": 3,
                },
                {
                    "type": "bar",
                    "label": "Ingresos",
                    "backgroundColor": ["#03a9f4"],
                    "borderColor": ["#c62828"],
                    "data": self.__balance["Ingresos Total"].to_list(),
                    # "borderWidth": 1,
                },
                {
                    # "type": "bar",
                    "label": "Pagos",
                    "backgroundColor": ["#ffab91"],
                     "borderColor": ["#ffab91"],
                    "data": self.__balance["Pagos Total"].to_list(),
                    "borderWidth": 1,
                },
            ],
            
        }
        # generando Tipos de Pagos Chart
        data["Tipos_Pagos"] = {}
        data["Tipos_Pagos"]["data_graph"] = {
            "datasets": [
                {
                    "label": "Total",
                    "backgroundColor": ["#009688", "#7986cb"],
                    "data": [
                        self.__balance["Ingresos Efectivo"].sum(),
                        self.__balance["Ingresos Diana BBVA"].sum()
                        + self.__balance["Ingresos Clip"].sum()
                        + self.__balance["Ingresos Mercado Pago"].sum()
                        + self.__balance["Ingresos Santander"].sum(),
                    ],
                    "borderWidth": 1,
                },
                {
                    "label": "Cuentas",
                    "backgroundColor": [
                        "#009688",  # efectivo
                        "#7986cb",  # Depositos/Transferencias/Tarjeta
                        "#4fc3f7",  # Diana BBVA
                        "#ffa726",  # Clip
                        "#fdd835",  # Mercado Pago
                        "#c62828",  # Santander
                    ],
                    "data": [
                        self.__balance["Ingresos Efectivo"].sum(),
                        0,
                        self.__balance["Ingresos Diana BBVA"].sum(),
                        self.__balance["Ingresos Clip"].sum(),
                        self.__balance["Ingresos Mercado Pago"].sum(),
                        self.__balance["Ingresos Santander"].sum(),
                    ],
                    "borderWidth": 1,
                },
            ],
            "labels": [
                "Efectivo",
                "Deposito/Transferencia/Tarjeta",
                "Diana BBVA",
                "Clip",
                "Mercado Pago",
                "Santander",
            ],
        }
        return data

        # data = {"efectivo": {"titulo": "Efectivo", "total": 0}}
        # print(data)


# consultasTable = consultasConsultorioTable()
# df = consultasTable.getConsultasDF(save_to="/home/hirvin/Documents/Dev/OpenAnalytics/OpenAnalytics/AirTable/local_consultas.csv")
# # consultasTable.getPacientesJennyView()

# pagosTable = pagosConsultorioTable()
# df = pagosTable.getPagosDF(save_to="/home/hirvin/Documents/Dev/OpenAnalytics/OpenAnalytics/AirTable/local_pagos.csv")


def getBalanceData():
    # read data frames
    df_consultas = pd.read_csv(
        "/home/hirvin/Documents/Dev/OpenAnalytics/OpenAnalytics/AirTable/local_consultas.csv"
    )
    df_pagos = pd.read_csv(
        "/home/hirvin/Documents/Dev/OpenAnalytics/OpenAnalytics/AirTable/local_pagos.csv"
    )

    # group data frames
    df_consultas_month = df_consultas.groupby(
        ["month_name"], sort=False, as_index=False
    )[["Pago Final (Registrado)"]].sum()
    df_pagos_month = df_pagos.groupby(["month_name"], sort=False, as_index=False)[
        ["Cantidad"]
    ].sum()

    # generate balance
    df_balance_month = pd.merge(
        df_consultas_month, df_pagos_month, on="month_name", how="outer"
    )
    df_balance_month["ganancia"] = (
        df_balance_month["Pago Final (Registrado)"] - df_balance_month["Cantidad"]
    )

    # genereta chart object
    datasets_balance = [
        {
            "label": "Ingresos",
            "backgroundColor": "#DEE120",
            "borderColor": "#DEE120",
            "data": df_balance_month["Pago Final (Registrado)"].tolist(),
        },
        {
            "label": "Gastos",
            "backgroundColor": "#2920E1",
            "borderColor": "#2920E1",
            "data": df_balance_month["Cantidad"].tolist(),
        },
    ]

    # get data ganancia

    datasets_ganancia = [
        {
            "label": "Ganancia",
            "backgroundColor": "#DEE120",
            "borderColor": "#DEE120",
            "data": df_balance_month["ganancia"].tolist(),
        }
    ]

    data_balance = {
        "labels": df_balance_month["month_name"].tolist(),
        "datasets": datasets_balance,
    }
    data_ganancia = {
        "labels": df_balance_month["month_name"].tolist(),
        "datasets": datasets_ganancia,
    }
    log.info({"dataBalance": data_balance, "dataGanancias": data_ganancia})
    return {"dataBalance": data_balance, "dataGanancias": data_ganancia}

    # print(data2)


# fig, ax = plt.subplots()
# ax.plot(df_consultas_month["month_name"], df_consultas_month["Pago Final (Registrado)"], df_consultas_month["month_name"], df_pagos_month["Cantidad"])
# plt.show()
if __name__ == "__main__":
    data_server = consultorioFlask()
    data_server.processBalance()
    # consultorio_2021 = consultorio2021()
    # data = consultorio_2021.getBalanceCuentasDataFrame(period="month_name")
    # print([data])
    # print(data[['Hirvin (BBVA) Total', 'Diana BBVA Total', 'Efectivo Total', 'Santander Total', 'Caja Fuerte Total']])
    # print(f" Ingresos: {data['Ingresos Diana (BBVA)'].sum() + data['Ingresos Clip'].sum()} Pagos: {data['Pagos Diana (BBVA)'].sum()} Abonos: {data['Abonos Diana(BBVA)'].sum()} Retiros: {data['Retiros Diana(BBVA)'].sum()} Efectivo Total: {data['Mercado Pago Total'].sum()}")


# const rows2 = [
#     {name:"Enero", calories:10, fat:6.0, carbs:24, protein:4.0},
#     {name:"Febrero", calories:10, fat:9.0, carbs:37, protein:4.3},
#     {name:"Marzo", calories:262, fat:16.0, carbs:24, protein:6.0},
#     {name:"Abril", calories:305, fat:3.7, carbs:67, protein:4.3},
#     {name:"Mayo", calories:356, fat:16.0, carbs:49, protein:3.9},
#   ];

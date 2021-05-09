from OpenAnalytics.AirTable import air_table_log as log
import matplotlib.pyplot as plt
import pandas as pd
import requests
from os import system
from OpenAnalytics.ENV import ENV_AIR_TABLE_PATH, AIR_TABLE_ID_DATA, AIR_TABLE_API_KEY_DATA
from dotenv import load_dotenv
from os import getenv

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
        log.debug(f"New airTable, TableID: {self.__airTableId}  APIKey: {self.__airTableApiKey}")

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
            filter=["Fecha", "Concepto", "Pago", "Cantidad", "Cuenta de Pago"],
        )
        df.Fecha = pd.to_datetime(df.Fecha)
        df["year"] = df.Fecha.dt.year
        df["month"] = df.Fecha.dt.month
        df["week"] = df.Fecha.dt.isocalendar().week
        df["month_name"] = df.Fecha.dt.strftime("%B %Y")
        df["Cantidad"] = pd.to_numeric(df["Cantidad"])
        if save_to is not None:
            df.to_csv(save_to)
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
                print(
                    f"{fecha}   {name:35} ${pago_final:8.2f} {dentista} {comision:5} ${ganancia:8.2f}"
                )
                total += float(row["fields"]["Ganancia Especialista"])
            print(f"la ganancai de jenny es: {total}")

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
        df["Pago Final (Registrado)"] = pd.to_numeric(df["Pago Final (Registrado)"])
        if save_to is not None:
            df.to_csv(save_to)
        return df


class consultorio2021:
    def __init__(self, from_data=False):
        if from_data is False:
            self.consultasTable = consultasConsultorioTable()
            self.pagosTable = pagosConsultorioTable()
            self.__from_data = from_data

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
    
    def getBalanceCuentasDataFrame(self):
        consultas_df = self.consultasTable.getConsultasDF()
        pagos_df = self.pagosTable.getPagosDF()

        data_consultas = consultas_df.groupby(["month_name","Forma Pago"], as_index=False)["Pago Final (Registrado)"].sum()
        data_consultas.set_index("Forma Pago", inplace=True)
        # print(data_consultas)


        data_pagos = pagos_df.groupby(["month_name","Cuenta de Pago"], as_index=False)["Cantidad"].sum()
        data_pagos.set_index("Cuenta de Pago", inplace=True)
        # print(data_pagos)

        # procesar Efectivo
        left_data = data_consultas.loc[['Efectivo']].rename(columns={"Pago Final (Registrado)":"Ingresos Efectivo"})
        rigth_data = data_pagos.loc[['Efectivo']].rename(columns={"Cantidad":"Pagos Efectivo"})
        estado_cuentas = pd.merge(left_data, rigth_data, left_on='month_name', right_on='month_name', how='outer')
        estado_cuentas.fillna(0, inplace=True)
        estado_cuentas["Efectivo Total"] = estado_cuentas["Ingresos Efectivo"] - estado_cuentas["Pagos Efectivo"]

        # procesar Clip
        rigth_data = data_consultas.loc[['Clip']].rename(columns={"Pago Final (Registrado)":"Ingresos Clip"})
        estado_cuentas.fillna(0, inplace=True)
        estado_cuentas = pd.merge(estado_cuentas, rigth_data, left_on='month_name', right_on='month_name', how='outer')

        # procesar Diana BBVA
        left_data = data_consultas.loc[['Diana BBVA']].rename(columns={"Pago Final (Registrado)":"Ingresos Diana (BBVA)"})
        rigth_data = data_pagos.loc[['Diana (BBVA)']].rename(columns={"Cantidad":"Pagos Diana (BBVA)"})
        estado_cuentas = pd.merge(estado_cuentas, left_data, left_on='month_name', right_on='month_name', how='outer')
        estado_cuentas = pd.merge(estado_cuentas, rigth_data, left_on='month_name', right_on='month_name', how="outer")
        estado_cuentas.fillna(0, inplace=True)
        estado_cuentas["Diana Total"] = estado_cuentas["Ingresos Diana (BBVA)"] + estado_cuentas["Ingresos Clip"] - estado_cuentas["Pagos Diana (BBVA)"] 

        # procesar Mercado Pago
        left_data = data_consultas.loc[['Mercado Pago']].rename(columns={"Pago Final (Registrado)":"Ingresos Mercado Pago"})
        rigth_data = data_pagos.loc[['Mercado Pago']].rename(columns={"Cantidad":"Pagos Mercado Pago"})
        estado_cuentas = pd.merge(estado_cuentas, left_data, left_on='month_name', right_on='month_name', how='outer')
        estado_cuentas = pd.merge(estado_cuentas, rigth_data, left_on='month_name', right_on='month_name', how="outer")
        estado_cuentas.fillna(0, inplace=True)
        estado_cuentas["Mercado Pago Total"] = estado_cuentas["Ingresos Mercado Pago"] - estado_cuentas["Pagos Mercado Pago"]

        # procesar Santander
        left_data = data_consultas.loc[['Santander']].rename(columns={"Pago Final (Registrado)":"Ingresos Santander"})
        rigth_data = data_pagos.loc[['Santander']].rename(columns={"Cantidad":"Pagos Santander"})
        estado_cuentas = pd.merge(estado_cuentas, left_data, left_on='month_name', right_on='month_name', how='outer')
        estado_cuentas = pd.merge(estado_cuentas, rigth_data, left_on='month_name', right_on='month_name', how="outer")
        estado_cuentas.fillna(0, inplace=True)
        estado_cuentas["Santander Total"] = estado_cuentas["Ingresos Santander"] - estado_cuentas["Pagos Santander"]

        # procesar Hirvin BBVA
        rigth_data = data_pagos.loc[['Hirvin (BBVA)']].rename(columns={"Cantidad":"Pagos Hirvin (BBVA)"})
        estado_cuentas = pd.merge(estado_cuentas, rigth_data, left_on='month_name', right_on='month_name', how="outer")
        estado_cuentas.fillna(0, inplace=True)
        estado_cuentas["Hirvin (BBVA) Total"] = estado_cuentas["Pagos Hirvin (BBVA)"]

        return estado_cuentas



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
    consultorio_2021 = consultorio2021()
    data = consultorio_2021.getBalanceCuentasDataFrame()
    print(data['Efectivo Total'].sum())



    
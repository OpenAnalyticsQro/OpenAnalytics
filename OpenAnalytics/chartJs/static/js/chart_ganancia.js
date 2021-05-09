let url_data_ganancia = "http://127.0.0.1:5000/dataBalance";

const configGanancia = {
  type: "line",
  data: {},
  options: {},
};

var myChartGanacia = new Chart(document.getElementById("myChartGanancia"), configGanancia);

$.getJSON(url_data_ganancia, function (data) {
    myChartGanacia.data = data["data"]["dataGanancias"];
    myChartGanacia.update();
});

let url_data_balance = "http://127.0.0.1:5000/dataBalance";

const config = {
  type: "line",
  data: {},
  options: {},
};

var myChartBalance = new Chart(document.getElementById("myChartBalance"), config);

$.getJSON(url_data_balance, function (data) {
  myChartBalance.data = data["data"]["dataBalance"];
  myChartBalance.update();
});

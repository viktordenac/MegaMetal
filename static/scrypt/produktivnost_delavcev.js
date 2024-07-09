const now = new Date();
const year = now.getFullYear();
const month = (now.getMonth() + 1).toString().padStart(2, '0'); // Adding 1 since getMonth() returns 0-11

const fromMonth = `${year}-01`;
const toMonth = `${year}-${month}`;



function setDefaultMonthsGrafi() {
    document.getElementById('from_date_graf').value = fromMonth;
    document.getElementById('to_date_graf').value = toMonth;
}

function setDefaultMonthsTable() {
    document.getElementById('from_date_table').value = toMonth;
    document.getElementById('to_date_table').value = toMonth;
    document.getElementById('from_delavec_date_table').value = fromMonth;
    document.getElementById('to_delavec_date_table').value = toMonth;
}

var myChart; // Declare the chart variable globally
var delavecChart; // Declare the chart variable globally

function fetchProduktivnostDataForGraf() {
    var from_selectedMonth = document.getElementById('from_date_graf').value;
    var from_year = from_selectedMonth.split('-')[0];
    var from_month = from_selectedMonth.split('-')[1];
    var to_selectedMonth = document.getElementById('to_date_graf').value;
    var to_year = to_selectedMonth.split('-')[0];
    var to_month = to_selectedMonth.split('-')[1];
    var from_firstDayOfMonth = new Date(from_year, from_month - 1, 1);
    var to_lastDayOfMonth = new Date(to_year, to_month, 1);
    var from_date = from_firstDayOfMonth.toISOString().split('T')[0];
    var to_date = to_lastDayOfMonth.toISOString().split('T')[0];

    var xhr = new XMLHttpRequest();
    xhr.open('GET', '/produktivnost_grafi_load?from_date=' + from_date + '&to_date=' + to_date);
    xhr.onload = function () {
        if (xhr.status === 200) {
            var response = JSON.parse(xhr.responseText);
            console.log(response);
            displayOddelkiProduktivnostChart(response);
        } else {
            console.error('Request failed. Status: ' + xhr.status);
        }
    };
    xhr.send();
}

function fetchDataTableForTables() {
    var from_selectedMonth = document.getElementById('from_date_table').value;
    var from_year = from_selectedMonth.split('-')[0];
    var from_month = from_selectedMonth.split('-')[1];
    var to_selectedMonth = document.getElementById('to_date_table').value;
    var to_year = to_selectedMonth.split('-')[0];
    var to_month = to_selectedMonth.split('-')[1];
    var from_firstDayOfMonth = new Date(from_year, from_month - 1, 1);
    var to_lastDayOfMonth = new Date(to_year, to_month, 1);
    var from_date = from_firstDayOfMonth.toISOString().split('T')[0];
    var to_date = to_lastDayOfMonth.toISOString().split('T')[0];
    var xhr = new XMLHttpRequest();
    xhr.open('GET', '/produktivnost_table_load?from_date=' + from_date + '&to_date=' + to_date);
    xhr.onload = function () {
        if (xhr.status === 200) {
            var response = JSON.parse(xhr.responseText);
            var top_five = response.table_data_top;
            var bottom_five = response.table_data_bottom;
            console.log("TABLE" + top_five);
            console.log("TABLE" + bottom_five);
            displayTable(top_five, 'top5Table');
            displayTable(bottom_five, 'bottom5Table');
            //displayDataFrame(response.df); // Pass the DataFrame JSON to displayDataFrame function
        } else {
            console.error('Request failed. Status: ' + xhr.status);
        }
    };
    xhr.send();
}

function displayOddelkiProduktivnostChart(response) {
    if (myChart) {
        myChart.destroy();
    }
    // Render graph data
    const graphData = response.graph_data;
    const colors = response.colors;
    const labels = response.labels;

    // Prepare data for Chart.js
    const datasets = [];
    const places = Object.keys(colors);

    places.forEach(place => {
        const placeData = labels.map(label => graphData[label][place] || null);
        datasets.push({
            label: place,
            data: placeData,
            backgroundColor: colors[place],
            borderColor: 'rgba(75, 192, 192, 1)',
            borderWidth: 1
        });
    });

    // Create chart using Chart.js
    const ctx = document.getElementById('oddelkiProduktivnostChart').getContext('2d');
    myChart = new Chart(ctx, {
        type: 'bar',
        data: {
            labels: labels,
            datasets: datasets
        },
        options: {
            plugins: {
                tooltip: {
                    titleFont: { // Set the font size for the tooltip header
                        size: 18 // Adjust the font size as needed
                    },
                    bodyFont: { // Set the font size for the tooltip
                        size: 18 // Adjust the font size as needed
                    }
                }
            },
            scales: {
                y: {
                    beginAtZero: true
                }
            }
        }
    });
}

function displayTable(data, tableId) {
    var tableHtml = '';
    console.log("NEKJ", data.length)

    if (data.length === 0) {
        tableHtml = '<p>No info to show</p>';
    } else {
        // Create table headers
        tableHtml = '<table border="1">';
        tableHtml += '<tr>';
        for (var key in data[0]) {
            if (key === 'MJESEC_GODINA') {
                tableHtml += '<th>' + "DATUM" + '</th>';
            } else if (key === 'average_produktivnost') {
                tableHtml += '<th>' + "POVPREČNA PRODUKTIVNOST" + '</th>';
            } else {
                tableHtml += '<th>' + key + '</th>';
            }
        }
        tableHtml += '</tr>';

        // Add table rows
        data.forEach(function (item) {
            tableHtml += '<tr>';
            for (var key in item) {
                console.log("KEY", key)
                // Check if the value is a date and format it if necessary
                if (key === 'MJESEC_GODINA') {
                    tableHtml += '<td>' + formatDate(item[key]) + '</td>';
                } else if (key === 'DELAVEC') {
                    tableHtml += '<td><button class="delavecButton" onclick="displayChartForPerson(\'' + item[key] + '\')">' + item[key] + '</button></td>';
                } else {
                    tableHtml += '<td>' + item[key] + '</td>';
                }
            }
            tableHtml += '</tr>';
        });

        // Close table
        tableHtml += '</table>';
    }

    // Display the table in the designated div
    document.getElementById(tableId).innerHTML = tableHtml;
}

function displayChartForPerson(delavecName) {
    nameOfDelavec = delavecName
    console.log(nameOfDelavec)
    document.getElementById('workerChartTitle').innerText = delavecName;
    document.getElementById('refreshWorkerGraphButton').style.display = 'inline-block';
    document.getElementById('removeWorkerGraphButton').style.display = 'inline-block';
    var from_date = document.getElementById('from_delavec_date_table').value;
    var to_date = document.getElementById('to_delavec_date_table').value;
    var xhr = new XMLHttpRequest();
    xhr.open('GET', '/produktivnost_grafi_delavec_load?from_date=' + from_date + '&to_date=' + to_date + '&delavec=' + delavecName);
    xhr.onload = function () {
        if (xhr.status === 200) {
            var response = JSON.parse(xhr.responseText);
            if (response.error) {
                alert(response.error);
                return;
            }
            // Extract data from the response
            var delavecPodatki = response.delavecPodatki;

            // Extract MJESEC_GODINA and average_produktivnost arrays
            var mjesecGodina = delavecPodatki.map(function (item) {
                return formatDate(item.MJESEC_GODINA);
            });
            var average_produktivnost = delavecPodatki.map(function (item) {
                return item.average_produktivnost;
            });

            if (delavecChart) {
                delavecChart.destroy();
            }

            // Create a bar chart
            var ctx = document.getElementById('delavecChart').getContext('2d');
            delavecChart = new Chart(ctx, {
                type: 'bar',
                data: {
                    labels: mjesecGodina,
                    datasets: [{
                        label: 'Average Produktivnost',
                        data: average_produktivnost,
                        backgroundColor: 'rgba(54, 162, 235, 0.2)',
                        borderColor: 'rgba(54, 162, 235, 1)',
                        borderWidth: 1
                    }]
                },
                options: {
                    plugins: {
                        tooltip: {
                            titleFont: { // Set the font size for the tooltip header
                                size: 18 // Adjust the font size as needed
                            },
                            bodyFont: { // Set the font size for the tooltip
                                size: 18 // Adjust the font size as needed
                            }
                        }
                    },
                    scales: {
                        y: {
                            beginAtZero: true
                        }
                    }
                }
            });

        } else {
            confirm('Request failed. Status: ' + xhr.status);
        }
    };
    xhr.onerror = function () {
        console.error('Request error');
    };
    xhr.send();
    console.log("Displaying chart for: " + delavecName);
}

function formatDate(dateString) {
    const months = [
        "Januar", "Februar", "Marec", "April", "Maj", "Junij",
        "Julij", "Avgust", "September", "Oktober", "November", "December"
    ];

    const date = new Date(dateString);
    const year = date.getFullYear();
    const month = months[date.getMonth()];

    return year + " " + month;
}

function removeWorkerGraph() {
    document.getElementById('workerChartTitle').innerText = '';
    if (delavecChart) {
        delavecChart.destroy();
    }
    document.getElementById('refreshWorkerGraphButton').style.display = 'none';
    document.getElementById('removeWorkerGraphButton').style.display = 'none';
}
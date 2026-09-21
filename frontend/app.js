const API_BASE = "http://127.0.0.1:8000";

const selector = document.getElementById("bearingSelector");
const connectionStatus = document.getElementById("connectionStatus");

let charts = {
    rms: null,
    kurtosis: null,
    peak: null,
    crest: null,
    health: null
};


async function getLatest(bearingId) {
    const response = await fetch(
        `${API_BASE}/api/bearings/${bearingId}/latest`
    );

    if (!response.ok) {
        throw new Error("Could not load latest observation.");
    }

    return response.json();
}


async function getHistory(bearingId) {
    const response = await fetch(
        `${API_BASE}/api/bearings/${bearingId}/history?limit=100`
    );

    if (!response.ok) {
        throw new Error("Could not load observation history.");
    }

    return response.json();
}


function setConnectionState(connected) {
    const dot = document.querySelector(".connection-dot");

    if (connected) {
        connectionStatus.textContent = "Connected";
        dot.style.background = "#70d6a0";
    } else {
        connectionStatus.textContent = "Disconnected";
        dot.style.background = "#d66f70";
    }
}


function updateMetrics(latest) {

    document.getElementById("rms").textContent =
        latest.features.rms.toFixed(6);

    document.getElementById("kurtosis").textContent =
        latest.features.kurtosis.toFixed(6);

    document.getElementById("peakToPeak").textContent =
        latest.features.peak_to_peak.toFixed(6);

    document.getElementById("crestFactor").textContent =
        latest.features.crest_factor.toFixed(6);

    document.getElementById("healthScore").textContent =
        latest.health.score.toFixed(1);

    document.getElementById("healthCondition").textContent =
        latest.health.condition.toUpperCase();

    document.getElementById("timestamp").textContent =
        formatTimestamp(latest.timestamp);

    updateHealthVisuals(
        latest.health.condition
    );
}


function updateHealthVisuals(condition) {

    const indicator =
        document.getElementById("stateIndicator");

    const conditionElement =
        document.getElementById("healthCondition");

    const normalized =
        condition.toLowerCase();

    indicator.className =
        "state-indicator";

    conditionElement.className =
        "state-value";

    if (normalized === "healthy") {

        indicator.classList.add("healthy");

        conditionElement.classList.add(
            "healthy-text"
        );

    } else if (normalized === "degraded") {

        indicator.classList.add("degraded");

        conditionElement.classList.add(
            "degraded-text"
        );

    } else if (normalized === "severe") {

        indicator.classList.add("severe");

        conditionElement.classList.add(
            "severe-text"
        );

    } else if (normalized === "critical") {

        indicator.classList.add("critical");

        conditionElement.classList.add(
            "critical-text"
        );
    }
}


function formatTimestamp(timestamp) {
    return new Date(timestamp).toLocaleString(
        undefined,
        {
            dateStyle: "medium",
            timeStyle: "medium"
        }
    );
}


function prepareHistory(history) {

    return {

        labels: history.map(
            item => formatChartTimestamp(
                item.timestamp
            )
        ),

        rms: history.map(
            item => item.rms
        ),

        kurtosis: history.map(
            item => item.kurtosis
        ),

        peak: history.map(
            item => item.peak_to_peak
        ),

        crest: history.map(
            item => item.crest_factor
        ),

        health: history.map(
            item => item.health_score
        )
    };
}


function formatChartTimestamp(timestamp) {

    return new Date(timestamp).toLocaleDateString(
        undefined,
        {
            month: "short",
            day: "numeric"
        }
    );
}


function chartOptions() {

    return {
        responsive: true,
        maintainAspectRatio: false,

        interaction: {
            mode: "index",
            intersect: false
        },

        plugins: {
            legend: {
                display: false
            },

            tooltip: {
                callbacks: {
                    title: items => {
                        return items[0].label;
                    }
                }
            }
        },

        scales: {
            x: {
                grid: {
                    display: false
                },

                ticks: {
                    maxTicksLimit: 8
                }
            },

            y: {
                beginAtZero: false,

                grid: {
                    color: "rgba(255,255,255,0.06)"
                }
            }
        }
    };
}


function createChart(canvasId, values, label) {

    return new Chart(
        document.getElementById(canvasId),
        {
            type: "line",

            data: {
                labels: [],
                datasets: [
                    {
                        label,
                        data: values,

                        borderColor: "#1976a8",
                        backgroundColor: "rgba(25, 118, 168, 0.08)",
                        borderWidth: 2,
                        pointRadius: 0,
                        tension: 0.28,
                        fill: true
                    }
                ]
            },

            options: chartOptions()
        }
    );
}


function initializeCharts() {

    charts.rms = createChart(
        "rmsChart",
        [],
        "RMS"
    );

    charts.kurtosis = createChart(
        "kurtosisChart",
        [],
        "Kurtosis"
    );

    charts.peak = createChart(
        "peakChart",
        [],
        "Peak-to-Peak"
    );

    charts.crest = createChart(
        "crestChart",
        [],
        "Crest Factor"
    );

    charts.health = createChart(
        "healthChart",
        [],
        "Health Score"
    );
}


function updateChart(chart, labels, values) {

    chart.data.labels = labels;
    chart.data.datasets[0].data = values;

    chart.update();
}


async function loadBearing(bearingId) {

    try {

        connectionStatus.textContent = "Loading...";

        const [latest, historyResponse] =
            await Promise.all([
                getLatest(bearingId),
                getHistory(bearingId)
            ]);

        updateMetrics(latest);

        const history = prepareHistory(
            historyResponse.data
        );

        updateChart(
            charts.rms,
            history.labels,
            history.rms
        );

        updateChart(
            charts.kurtosis,
            history.labels,
            history.kurtosis
        );

        updateChart(
            charts.peak,
            history.labels,
            history.peak
        );

        updateChart(
            charts.crest,
            history.labels,
            history.crest
        );

        updateChart(
            charts.health,
            history.labels,
            history.health
        );

        document.getElementById("assetName").textContent =
            `Bearing ${bearingId}`;

        setConnectionState(true);

    } catch (error) {

        console.error(error);

        setConnectionState(false);

    }
}


selector.addEventListener(
    "change",
    event => {
        loadBearing(
            Number(event.target.value)
        );
    }
);


initializeCharts();
loadBearing(1);
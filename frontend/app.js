const API_BASE = "http://127.0.0.1:8000";

const selector =
    document.getElementById("bearingSelector");

const connectionStatus =
    document.getElementById("connectionStatus");

const assetName =
    document.getElementById("assetName");

const timelineSlider =
    document.getElementById("timelineSlider");

const selectedObservation =
    document.getElementById(
        "selectedObservation"
    );

const selectedTimestamp =
    document.getElementById(
        "selectedTimestamp"
    );

const agentSnapshot =
    document.getElementById(
        "agentSnapshot"
    );

const analyzeSelected =
    document.getElementById(
        "analyzeSelected"
    );

const compareBearings =
    document.getElementById(
        "compareBearings"
    );

const agentStatus =
    document.getElementById(
        "agentStatus"
    );

const agentTools =
    document.getElementById(
        "agentTools"
    );

const agentResponse =
    document.getElementById(
        "agentResponse"
    );

let charts = {
    rms: null,
    kurtosis: null,
    peak: null,
    crest: null,
    health: null
};

let historicalData = [];
let selectedIndex = 983;


async function getLatest(
    bearingId
) {

    const response = await fetch(
        `${API_BASE}/api/bearings/${bearingId}/latest`
    );

    if (!response.ok) {
        throw new Error(
            "Could not load latest observation."
        );
    }

    return response.json();
}


async function getHistory(
    bearingId
) {

    const response = await fetch(
        `${API_BASE}/api/bearings/${bearingId}/history?limit=984`
    );

    if (!response.ok) {
        throw new Error(
            "Could not load observation history."
        );
    }

    return response.json();
}


async function getSnapshot(
    bearingId,
    index
) {

    const response = await fetch(
        `${API_BASE}/api/bearings/${bearingId}/snapshot?index=${index}`
    );

    if (!response.ok) {
        throw new Error(
            "Could not load telemetry snapshot."
        );
    }

    return response.json();
}


function renderAgentMarkdown(markdown) {
    if (!markdown) {
        return "";
    }

    // Llama may return escaped Markdown such as \*\*text\*\*.
    const normalized = markdown.replace(
        /\\(\*{1,3}|_{1,3}|`|~~)/g,
        "$1"
    );

    return DOMPurify.sanitize(
        marked.parse(normalized, {
            breaks: true
        })
    );
}


function setConnectionState(
    connected
) {

    const dot =
        document.querySelector(
            ".connection-dot"
        );

    if (connected) {

        connectionStatus.textContent =
            "Connected";

        dot.style.background =
            "#70d6a0";

    } else {

        connectionStatus.textContent =
            "Disconnected";

        dot.style.background =
            "#d66f70";
    }
}


function updateMetrics(
    data
) {

    document.getElementById(
        "rms"
    ).textContent =
        data.features.rms.toFixed(6);

    document.getElementById(
        "kurtosis"
    ).textContent =
        data.features.kurtosis.toFixed(6);

    document.getElementById(
        "peakToPeak"
    ).textContent =
        data.features.peak_to_peak.toFixed(6);

    document.getElementById(
        "crestFactor"
    ).textContent =
        data.features.crest_factor.toFixed(6);

    document.getElementById(
        "healthScore"
    ).textContent =
        data.health.score.toFixed(1);

    document.getElementById(
        "healthScoreMetric"
    ).textContent =
        data.health.score.toFixed(1);

    document.getElementById(
        "degradationIndex"
    ).textContent =
        data.health.degradation_index.toFixed(2);

    document.getElementById(
        "healthCondition"
    ).textContent =
        data.health.condition.toUpperCase();

    document.getElementById(
        "timestamp"
    ).textContent =
        formatTimestamp(
            data.timestamp
        );

    updateHealthVisuals(
        data.health.condition
    );
}


function updateHealthVisuals(
    condition
) {

    const indicator =
        document.getElementById(
            "stateIndicator"
        );

    const conditionElement =
        document.getElementById(
            "healthCondition"
        );

    const normalized =
        condition.toLowerCase();

    indicator.className =
        "state-indicator";

    conditionElement.className =
        "state-value";

    if (normalized === "healthy") {

        indicator.classList.add(
            "healthy"
        );

        conditionElement.classList.add(
            "healthy-text"
        );

    } else if (
        normalized === "degraded"
    ) {

        indicator.classList.add(
            "degraded"
        );

        conditionElement.classList.add(
            "degraded-text"
        );

    } else if (
        normalized === "severe"
    ) {

        indicator.classList.add(
            "severe"
        );

        conditionElement.classList.add(
            "severe-text"
        );

    } else if (
        normalized === "critical"
    ) {

        indicator.classList.add(
            "critical"
        );

        conditionElement.classList.add(
            "critical-text"
        );
    }
}


function formatTimestamp(
    timestamp
) {

    return new Date(
        timestamp
    ).toLocaleString(
        undefined,
        {
            dateStyle: "medium",
            timeStyle: "medium"
        }
    );
}


function formatChartTimestamp(
    timestamp
) {

    return new Date(
        timestamp
    ).toLocaleDateString(
        undefined,
        {
            month: "short",
            day: "numeric"
        }
    );
}


function prepareHistory(
    history
) {

    return {

        labels: history.map(
            item =>
                formatChartTimestamp(
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
                    color:
                        "rgba(45, 94, 120, 0.08)"
                }
            }
        }
    };
}


function createChart(
    canvasId,
    label
) {

    return new Chart(
        document.getElementById(
            canvasId
        ),
        {

            type: "line",

            data: {

                labels: [],

                datasets: [
                    {

                        label,

                        data: [],

                        borderColor:
                            "#1976a8",

                        backgroundColor:
                            "rgba(25, 118, 168, 0.08)",

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

    charts.rms =
        createChart(
            "rmsChart",
            "RMS"
        );

    charts.kurtosis =
        createChart(
            "kurtosisChart",
            "Kurtosis"
        );

    charts.peak =
        createChart(
            "peakChart",
            "Peak-to-Peak"
        );

    charts.crest =
        createChart(
            "crestChart",
            "Crest Factor"
        );

    charts.health =
        createChart(
            "healthChart",
            "Health Score"
        );
}


function updateChart(
    chart,
    labels,
    values
) {

    chart.data.labels =
        labels;

    chart.data.datasets[0].data =
        values;

    chart.update();
}


async function selectObservation(
    index
) {

    const bearingId =
        Number(
            selector.value
        );

    selectedIndex =
        Number(index);

    timelineSlider.value =
        selectedIndex;

    const local =
        historicalData[
            selectedIndex
        ];

    if (local) {

        selectedObservation.textContent =
            selectedIndex;

        selectedTimestamp.textContent =
            formatTimestamp(
                local.timestamp
            );

        agentSnapshot.textContent =
            `Bearing ${bearingId} • ${
                formatTimestamp(
                    local.timestamp
                )
            }`;
    }

    try {

        const snapshot =
            await getSnapshot(
                bearingId,
                selectedIndex
            );

        updateMetrics(
            snapshot
        );

    } catch (error) {

        console.error(error);
    }
}


async function loadBearing(
    bearingId
) {

    try {

        connectionStatus.textContent =
            "Loading...";

        const [
            latest,
            historyResponse
        ] = await Promise.all(
            [
                getLatest(
                    bearingId
                ),

                getHistory(
                    bearingId
                )
            ]
        );

        historicalData =
            historyResponse.data;

        timelineSlider.max =
            historicalData.length - 1;

        updateChart(
            charts.rms,
            prepareHistory(
                historicalData
            ).labels,
            prepareHistory(
                historicalData
            ).rms
        );

        const prepared =
            prepareHistory(
                historicalData
            );

        updateChart(
            charts.kurtosis,
            prepared.labels,
            prepared.kurtosis
        );

        updateChart(
            charts.peak,
            prepared.labels,
            prepared.peak
        );

        updateChart(
            charts.crest,
            prepared.labels,
            prepared.crest
        );

        updateChart(
            charts.health,
            prepared.labels,
            prepared.health
        );

        assetName.textContent =
            `Bearing ${bearingId}`;

        selectedIndex =
            historicalData.length - 1;

        await selectObservation(
            selectedIndex
        );

        setConnectionState(
            true
        );

    } catch (error) {

        console.error(error);

        setConnectionState(
            false
        );
    }
}


async function runAgentAnalysis(
    question
) {

    const bearingId =
        Number(
            selector.value
        );

    agentStatus.textContent =
        "Agent is analyzing the selected snapshot...";

    agentTools.textContent =
        "Consulting MCP diagnostic tools...";

    agentResponse.textContent =
        "Please wait...";

    analyzeSelected.disabled =
        true;

    compareBearings.disabled =
        true;

    try {

        const response =
            await fetch(
                `${API_BASE}/api/agent/ask`,
                {
                    method: "POST",

                    headers: {
                        "Content-Type":
                            "application/json"
                    },

                    body: JSON.stringify(
                        {
                            bearing_id:
                                bearingId,

                            observation_index:
                                selectedIndex,

                            question
                        }
                    )
                }
            );

        if (!response.ok) {

            const detail =
                await response.text();

            throw new Error(
                detail
            );
        }

        const result =
            await response.json();

        agentStatus.textContent =
            `Bearing ${result.bearing_id} • Snapshot ${result.observation_index}`;

        agentTools.textContent =
            result.tools_used.length
                ? `MCP tools used: ${
                    result.tools_used.join(
                        " → "
                    )
                }`
                : "No MCP tools used.";

        agentResponse.innerHTML = 
            renderAgentMarkdown(result.answer);

    } catch (error) {

        console.error(error);

        agentStatus.textContent =
            "Agent unavailable";

        agentResponse.textContent =
            "Could not obtain an agent response.";

    } finally {

        analyzeSelected.disabled =
            false;

        compareBearings.disabled =
            false;
    }
}


timelineSlider.addEventListener(
    "change",
    event => {

        selectObservation(
            Number(
                event.target.value
            )
        );
    }
);


selector.addEventListener(
    "change",
    event => {

        loadBearing(
            Number(
                event.target.value
            )
        );
    }
);


analyzeSelected.addEventListener(
    "click",
    () => {

        runAgentAnalysis(
            "Analyze the selected telemetry snapshot. "
            + "Assess the bearing condition, explain the "
            + "recent degradation trend, and recommend "
            + "the appropriate maintenance action."
        );
    }
);


compareBearings.addEventListener(
    "click",
    () => {

        runAgentAnalysis(
            "Compare all four bearings at the selected "
            + "telemetry point and identify which bearing "
            + "requires the most attention. Explain why."
        );
    }
);


initializeCharts();

loadBearing(1);
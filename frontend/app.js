let batchSignals = [];
let batchPredictions = [];
let ecgChart = null;

function showMessage(message, type = "") {
    const resultDiv = document.getElementById("result");
    resultDiv.className = "result";
    if (type) resultDiv.classList.add(type);
    resultDiv.innerHTML = message;
}

function parseSignalLine(line) {
    const cleanedLine = line.trim();
    if (!cleanedLine) return [];

    const rawValues = cleanedLine
        .split(/[\t,; ]+/)
        .map(v => v.trim())
        .filter(v => v !== "")
        .map(Number);

    if (rawValues.some(isNaN)) return [];

    if (rawValues.length === 97) {
        return rawValues.slice(1);
    }

    return rawValues;
}

function isValidSignal(signal) {
    return signal.length === 96 && !signal.some(isNaN);
}

function fillSignalTextarea(signal) {
    document.getElementById("signal").value = signal.join(", ");
}

function resetBatchResults() {
    batchSignals = [];
    batchPredictions = [];
    document.getElementById("batchResults").innerHTML = "";
    document.getElementById("batchInfo").innerHTML = "";
    document.getElementById("batchContainer").classList.add("hidden");
}

function getClinicalStatus(risk) {
    if (risk >= 70) {
        return {
            color: "#ef4444",
            type: "infarct",
            label: "Risque élevé",
            diagnosis: "Le signal présente une forte probabilité d’infarctus.",
            confidence: "Confiance du modèle : très élevée"
        };
    }

    if (risk >= 40) {
        return {
            color: "#facc15",
            type: "warning",
            label: "Risque intermédiaire",
            diagnosis: "Le signal nécessite une vérification médicale complémentaire.",
            confidence: "Confiance du modèle : modérée"
        };
    }

    return {
        color: "#22c55e",
        type: "normal",
        label: "Risque faible",
        diagnosis: "Le signal est classé comme normal par le modèle.",
        confidence: "Confiance du modèle : élevée"
    };
}

function renderMedicalDashboard(signal, prediction) {
    const dashboard = document.getElementById("medicalDashboard");
    const riskGauge = document.getElementById("riskGauge");
    const riskValue = document.getElementById("riskValue");
    const riskLabel = document.getElementById("riskLabel");
    const diagnosisText = document.getElementById("diagnosisText");
    const confidenceLabel = document.getElementById("confidenceLabel");
    const modelBadge = document.getElementById("modelBadge");
    const pointsBadge = document.getElementById("pointsBadge");

    const risk = prediction.probability * 100;
    const degrees = risk * 3.6;
    const status = getClinicalStatus(risk);

    riskGauge.style.background = `conic-gradient(${status.color} ${degrees}deg, #1e293b ${degrees}deg)`;
    riskValue.textContent = `${risk.toFixed(1)}%`;
    riskLabel.textContent = status.label;
    diagnosisText.textContent = status.diagnosis;
    confidenceLabel.textContent = status.confidence;

    modelBadge.textContent = prediction.modelUsed.toUpperCase();
    pointsBadge.textContent = `${signal.length} points ECG`;

    const ctx = document.getElementById("ecgChart");

    if (ecgChart !== null) {
        ecgChart.destroy();
    }

    ecgChart = new Chart(ctx, {
        type: "line",
        data: {
            labels: signal.map((_, i) => i + 1),
            datasets: [{
                label: "Signal ECG",
                data: signal,
                borderWidth: 2.5,
                tension: 0.25,
                pointRadius: 0,
                borderColor: "#38bdf8",
                backgroundColor: "rgba(56, 189, 248, 0.12)"
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: {
                    labels: { color: "#e2e8f0" }
                }
            },
            scales: {
                x: {
                    ticks: { color: "#94a3b8" },
                    grid: { color: "#1e293b" },
                    title: {
                        display: true,
                        text: "Temps",
                        color: "#cbd5e1"
                    }
                },
                y: {
                    ticks: { color: "#94a3b8" },
                    grid: { color: "#1e293b" },
                    title: {
                        display: true,
                        text: "Amplitude",
                        color: "#cbd5e1"
                    }
                }
            }
        }
    });

    dashboard.classList.remove("hidden");
}

function renderBatchTable() {
    const batchContainer = document.getElementById("batchContainer");
    const batchResults = document.getElementById("batchResults");
    const batchInfo = document.getElementById("batchInfo");

    if (batchSignals.length === 0) {
        batchContainer.classList.add("hidden");
        return;
    }

    batchInfo.textContent = `${batchSignals.length} signaux valides détectés dans le fichier.`;

    const rows = batchSignals.map((item, i) => {
        const pred = batchPredictions[i];

        let text = "En attente";
        let conf = "-";
        let statusClass = "status-pending";

        if (pred) {
            if (pred.error) {
                text = pred.error;
                statusClass = "status-ko";
            } else {
                text = pred.predictedClass === "normal" ? "Signal normal" : "Infarctus";
                conf = `${(pred.probability * 100).toFixed(1)}%`;
                statusClass = pred.predictedClass === "normal" ? "status-ok" : "status-ko";
            }
        }

        return `
            <tr onclick="fillSignalTextarea(batchSignals[${i}].values)">
                <td>${item.originalLineNumber}</td>
                <td class="${statusClass}">${text}</td>
                <td>${conf}</td>
            </tr>
        `;
    }).join("");

    batchResults.innerHTML = `
        <div class="batch-table-wrapper">
            <table class="batch-table">
                <thead>
                    <tr>
                        <th>Ligne</th>
                        <th>Prédiction</th>
                        <th>Confiance</th>
                    </tr>
                </thead>
                <tbody>${rows}</tbody>
            </table>
        </div>
    `;

    batchContainer.classList.remove("hidden");
}

async function classifySignal(model, signal) {
    const res = await fetch("/api/ecg/classify", {
        method: "POST",
        headers: {"Content-Type": "application/json"},
        body: JSON.stringify({model, signal})
    });

    const data = await res.json();
    if (!res.ok) throw new Error(data.error || "Erreur");

    return data;
}

document.getElementById("fileInput").addEventListener("change", function (e) {
    const file = e.target.files[0];
    if (!file) return;

    const reader = new FileReader();

    reader.onload = function (e) {
        const lines = e.target.result
            .split(/\r?\n/)
            .map(l => l.trim())
            .filter(l => l !== "");

        resetBatchResults();

        if (lines.length === 1) {
            const signal = parseSignalLine(lines[0]);
            if (!isValidSignal(signal)) {
                showMessage("Format invalide : le signal doit contenir 96 valeurs numériques.", "infarct");
                return;
            }

            fillSignalTextarea(signal);
            showMessage("Fichier chargé avec succès.", "normal");
            return;
        }

        const valid = [];

        lines.forEach((l, i) => {
            const s = parseSignalLine(l);
            if (isValidSignal(s)) {
                valid.push({originalLineNumber: i + 1, values: s});
            }
        });

        if (valid.length === 0) {
            showMessage("Aucun signal valide détecté dans le fichier.", "infarct");
            return;
        }

        batchSignals = valid;
        batchPredictions = new Array(valid.length).fill(null);

        renderBatchTable();
        showMessage("Fichier chargé avec succès.", "normal");
    };

    reader.readAsText(file);
});

async function predict() {
    const model = document.getElementById("model").value;
    const values = document.getElementById("signal").value
        .split(/[\t,; ]+/)
        .map(v => Number(v.trim()))
        .filter(v => !isNaN(v));

    if (values.length !== 96) {
        showMessage("Erreur : il faut exactement 96 valeurs ECG.", "infarct");
        return;
    }

    try {
        const data = await classifySignal(model, values);
        const risk = data.probability * 100;
        const label = data.predictedClass === "normal" ? "Signal normal" : "Infarctus probable";
        const type = data.predictedClass === "normal" ? "normal" : "infarct";

        showMessage(
            `
            <div class="result-line">
                <span>Classe : ${label}</span>
                <span>Probabilité : ${risk.toFixed(1)}%</span>
                <span class="small-badge">${data.modelUsed.toUpperCase()}</span>
            </div>
            `,
            type
        );

        renderMedicalDashboard(values, data);

    } catch (e) {
        showMessage(e.message, "infarct");
    }
}

async function predictBatch() {
    const model = document.getElementById("model").value;

    if (batchSignals.length === 0) {
        showMessage("Aucun fichier chargé.", "infarct");
        return;
    }

    for (let i = 0; i < batchSignals.length; i++) {
        try {
            batchPredictions[i] = await classifySignal(model, batchSignals[i].values);
        } catch (e) {
            batchPredictions[i] = {error: e.message};
        }

        renderBatchTable();
    }

    showMessage("Analyse du fichier terminée.", "normal");

}
async function compareModels() {
    const values = document.getElementById("signal").value
        .split(/[\t,; ]+/)
        .map(v => Number(v.trim()))
        .filter(v => !isNaN(v));

    if (values.length !== 96) {
        showMessage("Erreur : il faut exactement 96 valeurs ECG.", "infarct");
        return;
    }

    const models = ["mlp", "cnn", "lstm"];
    const comparisonContainer = document.getElementById("comparisonContainer");
    const comparisonResults = document.getElementById("comparisonResults");

    comparisonContainer.classList.remove("hidden");
    comparisonResults.innerHTML = "<p>Comparaison en cours...</p>";

    const results = [];

    for (const model of models) {
        try {
            const prediction = await classifySignal(model, values);
            results.push(prediction);
        } catch (e) {
            results.push({
                modelUsed: model,
                predictedClass: "Erreur",
                probability: 0,
                error: e.message
            });
        }
    }

    const best = results.reduce((max, current) => {
        return current.probability > max.probability ? current : max;
    }, results[0]);

    const rows = results.map(result => {
        const probability = (result.probability * 100).toFixed(1);
        const label = result.predictedClass === "normal" ? "Signal normal" : "Infarctus";
        const isBest = result.modelUsed === best.modelUsed;

        return `
            <tr class="${isBest ? "best-model" : ""}">
                <td>${isBest ? " " : ""}${result.modelUsed.toUpperCase()}</td>
                <td>${result.error ? result.error : label}</td>
                <td>${probability}%</td>
            </tr>
        `;
    }).join("");

    comparisonResults.innerHTML = `
        <table class="comparison-table">
            <thead>
                <tr>
                    <th>Modèle</th>
                    <th>Classe prédite</th>
                    <th>Probabilité</th>
                </tr>
            </thead>
            <tbody>
                ${rows}
            </tbody>
        </table>

        <p class="best-text">
            Meilleur score : ${best.modelUsed.toUpperCase()} avec ${(best.probability * 100).toFixed(1)}%
        </p>
    `;
}
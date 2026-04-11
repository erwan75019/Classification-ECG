let batchSignals = [];
let batchPredictions = [];

function showMessage(message, type = "") {
    const resultDiv = document.getElementById("result");
    resultDiv.className = "result";
    if (type) {
        resultDiv.classList.add(type);
    }
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

function renderBatchTable() {
    const batchContainer = document.getElementById("batchContainer");
    const batchResults = document.getElementById("batchResults");

    if (batchSignals.length === 0) {
        batchContainer.classList.add("hidden");
        return;
    }

    const rows = batchSignals.map((item, i) => {
        const pred = batchPredictions[i];

        let text = "En attente";
        let conf = "-";

        if (pred) {
            if (pred.error) {
                text = pred.error;
            } else {
                text = pred.predictedClass === "normal" ? "Signal normal" : "Infarctus";
                conf = `${(pred.probability * 100).toFixed(1)}%`;
            }
        }

        return `
            <tr>
                <td>${item.originalLineNumber}</td>
                <td>${text}</td>
                <td>${conf}</td>
            </tr>
        `;
    }).join("");

    batchResults.innerHTML = `
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
                showMessage("Format invalide.", "infarct");
                return;
            }

            fillSignalTextarea(signal);
            showMessage("Fichier chargé.", "normal");
            return;
        }

        const valid = [];
        const invalid = [];

        lines.forEach((l, i) => {
            const s = parseSignalLine(l);
            if (isValidSignal(s)) {
                valid.push({originalLineNumber: i + 1, values: s});
            } else {
                invalid.push(i + 1);
            }
        });

        if (valid.length === 0) {
            showMessage("Aucun signal valide.", "infarct");
            return;
        }

        batchSignals = valid;
        batchPredictions = new Array(valid.length).fill(null);

        renderBatchTable();
        showMessage("Fichier chargé.", "normal");
    };

    reader.readAsText(file);
});

async function predict() {
    const model = document.getElementById("model").value;
    const values = document.getElementById("signal").value
        .split(",").map(v => Number(v.trim())).filter(v => !isNaN(v));

    if (values.length !== 96) {
        showMessage("Il faut 96 valeurs.", "infarct");
        return;
    }

    try {
        const data = await classifySignal(model, values);

        showMessage(
            `Classe : ${data.predictedClass} | Confiance : ${(data.probability * 100).toFixed(1)}%`,
            data.predictedClass === "normal" ? "normal" : "infarct"
        );

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

    showMessage("Analyse terminée.", "normal");
}
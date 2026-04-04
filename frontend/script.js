/* ============================================================
   LogIQ — Dashboard Script

   Purpose:
   - Fetch real-time data from backend
   - Update charts (service, pie, timeline)
   - Manage pipeline lifecycle
   - Handle UI updates and user interactions


   ============================================================ */

// ── API ENDPOINT ─────────────────────────────────────────────
const API = "http://localhost:5000";


// ── GLOBAL STATE VARIABLES ───────────────────────────────────
let serviceChart, pieChart, timelineChart;
let refreshInterval = null;
let lastTotal = -1;
let userScrolling = false;
let scrollTimer   = null;


/* ============================================================
   Sticky Y-Axis Plugin
   Keeps Y-axis labels visible while horizontally scrolling
   ============================================================ */
const stickyYAxisPlugin = {
  id: "stickyYAxis",
  afterDraw(chart) {
    const { ctx, scales, chartArea, width, height } = chart;
    const scroll = document.getElementById("tl-scroll");
    if (!scroll) return;

    const scrollLeft = scroll.scrollLeft;
    if (scrollLeft === 0) return;

    const yLeft  = scales["yTotal"];  // Left axis (Total logs)
    const yRight = scales["yAnomaly"];   // Right axis (Anomalies)
    const leftW  = chartArea.left;
    const rightX = chartArea.right;

    /* ── Left Y axis (Total — cyan) ──────────────────────── */
    ctx.save();

    /* Background panel */
    ctx.fillStyle = "#0f1218";
    ctx.fillRect(scrollLeft, 0, leftW + 1, height);

    // Border line
    ctx.beginPath();
    ctx.strokeStyle = "#2d3748";
    ctx.lineWidth   = 1;
    ctx.moveTo(scrollLeft + leftW, chartArea.top);
    ctx.lineTo(scrollLeft + leftW, chartArea.bottom);
    ctx.stroke();

    // Tick labels
    ctx.textAlign    = "right";
    ctx.textBaseline = "middle";
    ctx.font         = "bold 13px 'JetBrains Mono', monospace";
    ctx.fillStyle    = "#00d4ff";

    yLeft.ticks.forEach(tick => {
      const y = yLeft.getPixelForValue(tick.value);
      if (y >= chartArea.top && y <= chartArea.bottom) {
        ctx.fillText(String(tick.value), scrollLeft + leftW - 8, y);
      }
    });

    ctx.restore();


    /* ── Right Y axis (Anomalies — red) ──────────────────── */
    ctx.save();

    const rightPanelX = scrollLeft + rightX;

    /* Background panel */
    ctx.fillStyle = "#0f1218";
    ctx.fillRect(rightPanelX - 1, 0, width - rightX + 4, height);

    /* Border */
    ctx.beginPath();
    ctx.strokeStyle = "#2d3748";
    ctx.lineWidth   = 1;
    ctx.moveTo(rightPanelX, chartArea.top);
    ctx.lineTo(rightPanelX, chartArea.bottom);
    ctx.stroke();

    // Tick labels
    ctx.textAlign    = "left";
    ctx.textBaseline = "middle";
    ctx.font         = "bold 13px 'JetBrains Mono', monospace";
    ctx.fillStyle    = "#ff4757";

    yRight.ticks.forEach(tick => {
      const y = yRight.getPixelForValue(tick.value);
      if (y >= chartArea.top && y <= chartArea.bottom) {
        ctx.fillText(String(tick.value), rightPanelX + 8, y);
      }
    });

    ctx.restore();
  }
};


/* ============================================================
   Initialize All Charts
   - Service Bar Chart
   - Pie Chart
   - Timeline Chart
   ============================================================ */
function initCharts() {
  Chart.defaults.color       = "#8892a4";
  Chart.defaults.font.family = "'JetBrains Mono', monospace";
  Chart.defaults.font.size   = 11;
  Chart.defaults.animation   = false;

  const grid = "#1a2235";

  /* ── SERVICE BAR CHART ─────────────────────────────────── */
  serviceChart = new Chart(document.getElementById("serviceChart"), {
    type: "bar",
    data: {
      labels: [],
      datasets: [
        {
          label: "Total",
          data: [],
          backgroundColor: "rgba(0,212,255,0.25)",
          borderColor: "#00d4ff",
          borderWidth: 1,
          borderRadius: 3
        },
        {
          label: "Anomalies",
          data: [],
          backgroundColor: "rgba(255,71,87,0.45)",
          borderColor: "#ff4757",
          borderWidth: 1,
          borderRadius: 3
        }
      ]
    },
    options: {
      responsive: true,
      animation: false,
      plugins: {
        legend: { position: "top", labels: { boxWidth: 10, padding: 14 } },
        tooltip: {
          backgroundColor: "#1c2333",
          borderColor: "#2d3748",
          borderWidth: 1,
          titleColor: "#00d4ff",
          bodyColor: "#e2e8f0",
          padding: 10
        }
      },
      scales: {
        x: { grid: { color: grid } },
        y: { grid: { color: grid }, beginAtZero: true }
      }
    }
  });


   /* ── PIE CHART (Normal vs Anomaly) ─────────────────────── */
  pieChart = new Chart(document.getElementById("pieChart"), {
    type: "doughnut",
    data: {
      labels: ["Normal", "Anomaly"],
      datasets: [{
        data: [1, 0],
        backgroundColor: ["rgba(0,230,118,0.75)", "rgba(255,71,87,0.75)"],
        borderColor: ["#00e676", "#ff4757"],
        borderWidth: 1
      }]
    },
    options: {
      responsive: true,
      animation: false,
      cutout: "65%",
      plugins: {
        legend: { position: "bottom", labels: { boxWidth: 10, padding: 14 } },
        tooltip: {
          backgroundColor: "#1c2333",
          borderColor: "#2d3748",
          borderWidth: 1,
          titleColor: "#00d4ff",
          bodyColor: "#e2e8f0",
          padding: 10
        }
      }
    }
  });


  /* ── TIMELINE CHART ────────────────────────────────────── */
  timelineChart = new Chart(document.getElementById("timelineChart"), {
    type: "line",
    plugins: [stickyYAxisPlugin],
    data: {
      labels: [],
      datasets: [
        {
          label: "Total",
          data: [],
          borderColor: "#00d4ff",
          backgroundColor: "rgba(0,212,255,0.05)",
          tension: 0.4,
          fill: true,
          pointRadius: 2,
          pointHoverRadius: 5,
          borderWidth: 1.5,
          yAxisID: "yTotal"
        },
        {
          label: "Anomalies",
          data: [],
          borderColor: "#ff4757",
          backgroundColor: "rgba(255,71,87,0.08)",
          tension: 0.4,
          fill: true,
          pointRadius: 3,
          pointHoverRadius: 6,
          pointBackgroundColor: "#ff4757",
          borderWidth: 2,
          yAxisID: "yAnomaly"
        }
      ]
    },
    options: {
      responsive: false,
      maintainAspectRatio: false,
      animation: false,
      layout: {
        padding: { top: 16, right: 80, bottom: 0, left: 0 }
      },
      plugins: {
        legend: { display: false },
        tooltip: {
          mode: "index",
          intersect: false,
          backgroundColor: "#1c2333",
          borderColor: "#2d3748",
          borderWidth: 1,
          titleColor: "#00d4ff",
          bodyColor: "#e2e8f0",
          padding: 12,
          titleFont: { size: 12 },
          bodyFont:  { size: 11 },
          callbacks: {
            title: items => `Time: ${items[0].label}`,
            label: item  => ` ${item.dataset.label}: ${item.raw}`
          }
        }
      },
      scales: {
        x: {
          grid: { color: grid },
          border: { color: "#232b3a" },
          ticks: {
            maxTicksLimit: 10,
            maxRotation: 0,
            font: { size: 11 },
            color: "#8892a4",
            padding: 8
          }
        },
        yTotal: {
          type: "linear",
          position: "left",
          grid: { color: grid },
          border: { color: "#232b3a" },
          ticks: {
            color: "#00d4ff",
            font: { size: 13, weight: "bold" },
            maxTicksLimit: 6,
            padding: 12
          },
          beginAtZero: false,
          grace: "20%"
        },
        yAnomaly: {
          type: "linear",
          position: "right",
          grid: { drawOnChartArea: false },
          border: { color: "#232b3a" },
          ticks: {
            color: "#ff4757",
            font: { size: 13, weight: "bold" },
            maxTicksLimit: 6,
            stepSize: 1,
            padding: 12
          },
          beginAtZero: true,
          min: 0,
          suggestedMax: 6
        }
      }
    }
  });


/* Handle scroll behavior for timeline */
  const scroll = document.getElementById("tl-scroll");


  if (scroll) {
    // Horizontal scroll using mouse wheel
    scroll.addEventListener("wheel", e => {
      e.preventDefault();
      scroll.scrollLeft += e.deltaY;
      timelineChart.draw();
    });

    // Detect manual scrolling
    scroll.addEventListener("scroll", () => {
    timelineChart.draw();
    /* Detect manual scroll — pause auto scroll for 3 seconds */
    userScrolling = true;
    clearTimeout(scrollTimer);

    // Resume auto-scroll after 10 seconds
    scrollTimer = setTimeout(() => {
        userScrolling = false;
    }, 10000);
});
  }
}

/* ============================================================
   Fetch data from backend and update dashboard
   ============================================================ */
async function refreshDashboard() {
  try {
    const [mR, sR, tR, lR, stR] = await Promise.all([
      fetch(`${API}/metrics`),
      fetch(`${API}/services`),
      fetch(`${API}/timeline`),
      fetch(`${API}/logs?limit=50`),
      fetch(`${API}/status`)
    ]);

    const metrics  = await mR.json();
    const services = await sR.json();
    const timeline = await tR.json();
    const logs     = await lR.json();
    const status   = await stR.json();

    
    lastTotal = metrics.total;

    // Update UI
    updateMetrics(metrics);
    updatePieChart(metrics);
    updateServiceChart(services);
    updateTimeline(timeline);
    updateFeed(logs);
    updateStatus(status.running);

  } catch (err) {
    console.warn("Backend not reachable:", err.message);
    showOffline();
  }
}

/* ============================================================
   UI Update Functions
   ============================================================ */

// Update metric cards
function updateMetrics(m) {
  setText("m-total",     m.total     ?? 0);
  setText("m-anomalies", m.anomalies ?? 0);
  setText("m-normal",    m.normal    ?? 0);
  setText("m-rate",      `${m.rate   ?? 0}%`);
}

// Update text safely
function setText(id, val) {
  const el = document.getElementById(id);
  if (el && el.textContent !== String(val)) el.textContent = val;
}


/* ============================================================
   AUTO REFRESH
   Continuously updates dashboard every 3 seconds
   ============================================================ */
function updateServiceChart(services) {
  if (!services || !services.length) return;
  serviceChart.data.labels           = services.map(s => s.service);
  serviceChart.data.datasets[0].data = services.map(s => s.total);
  serviceChart.data.datasets[1].data = services.map(s => s.anomalies);
  serviceChart.update("none");
}

function updatePieChart(m) {
  const n = m.normal ?? 0, a = m.anomalies ?? 0;
  if (n + a === 0) return;
  pieChart.data.datasets[0].data = [n, a];
  pieChart.update("none");
}

function updateTimeline(timeline) {
  if (!timeline || !timeline.length) return;

  const labels    = timeline.map(t => t.time.slice(11, 19));
  const totals    = timeline.map(t => t.total);
  const anomalies = timeline.map(t => t.anomalies);

  const maxTotal   = Math.max(...totals,    1);
  const minTotal   = Math.max(0, Math.min(...totals) - 2);
  const maxAnomaly = Math.max(...anomalies, 1) + 1;

  /* Grow canvas width — 30px per data point, min = screen width */
  const canvas   = document.getElementById("timelineChart");
  const scroll   = document.getElementById("tl-scroll");
  const screenW  = scroll ? scroll.clientWidth : 800;
  const newWidth = Math.max(screenW, labels.length * 30);

  if (canvas.width !== newWidth) {
    canvas.style.width = newWidth + "px";
    canvas.width       = newWidth;
    timelineChart.resize(newWidth, timelineChart.height);
  }

  timelineChart.data.labels           = labels;
  timelineChart.data.datasets[0].data = totals;
  timelineChart.data.datasets[1].data = anomalies;

  timelineChart.options.scales.yTotal.max   = maxTotal + 2;
  timelineChart.options.scales.yTotal.min   = minTotal;
  timelineChart.options.scales.yAnomaly.max = maxAnomaly;

  timelineChart.update("none");

  /* Auto scroll to right (latest) without jumping page */
  if (scroll && !userScrolling) {
    const prevY = window.scrollY;
    scroll.scrollLeft = scroll.scrollWidth;
    window.scrollTo(0, prevY);
}
}

function updateFeed(logs) {
  const tbody = document.getElementById("feed-body");
  if (!logs || !logs.length) {
    tbody.innerHTML = `<tr><td colspan="5" class="feed-empty">No logs yet — start the pipeline</td></tr>`;
    return;
  }
  tbody.innerHTML = logs.map(log => {
    const level = (log.level || "INFO").toLowerCase();
    const ts    = (log.timestamp || "").replace("T", " ").split(".")[0];
    return `<tr>
      <td>${ts}</td>
      <td><span class="badge badge-${level}">${log.level}</span></td>
      <td>${log.service || "—"}</td>
      <td>${log.message || "—"}</td>
      <td>${log.anomaly
        ? '<span class="badge badge-anomaly">Anomaly</span>'
        : '<span class="badge badge-normal">Normal</span>'
      }</td>
    </tr>`;
  }).join("");
}

function updateStatus(running) {
  const dot  = document.getElementById("status-dot");
  const text = document.getElementById("status-text");
  const pill = document.getElementById("live-pill");
  const algo = document.getElementById("status-algo");

  if (running) {
    dot.className    = "status-dot running";
    text.textContent = "Running";
    pill.className   = "live-pill active";
    pill.textContent = "● LIVE";
    algo.textContent = `${formatLabel(getSelected("model-select"))} · ${formatDataset(getSelected("dataset-select"))} · ${formatPipeline(getSelected("pipeline-select"))}`;
  } else {
    // ✅ WAIT 5 seconds before marking offline
    if (Date.now() - lastSeenRunning < 5000) {
      return;
    }
    
    dot.className    = "status-dot stopped";
    text.textContent = "Stopped";
    pill.className   = "live-pill";
    pill.textContent = "● LIVE";
    algo.textContent = "No pipeline running";
  }
}

function showOffline() {
  const pill = document.getElementById("live-pill");
  if (pill) { pill.className = "live-pill"; pill.textContent = "● OFFLINE"; }
}

/* ── Pipeline controls ─────────────────────────────────────── */
async function startPipeline() {
  const model    = getSelected("model-select");
  const dataset  = getSelected("dataset-select");
  const pipeline = getSelected("pipeline-select");

  document.getElementById("algo-label").textContent    = formatLabel(model);
  document.getElementById("dataset-label").textContent = dataset;
  updateModelCard(model);

  try { await fetch(`${API}/stop`, { method: "POST" }); } catch (e) {}

  try {
    await fetch(`${API}/start`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ model, dataset, pipeline })
    });
    startAutoRefresh();
  } catch (e) {
    alert("Cannot connect to backend.\nRun: python run.py --backend --storage sqlite");
  }
}

async function stopPipeline() {
  try { await fetch(`${API}/stop`, { method: "POST" }); } catch (e) {}
  updateStatus(false);
}

function updateModelCard(model) {
  const infos = {
    isolation_forest: {
      title: "Isolation Forest",
      items: ["Unsupervised ML", "Trains on first 50 logs", "No labelled data needed", "Industry standard baseline"]
    },
    lstm: {
      title: "LSTM",
      items: ["Sequence-based detection", "Learns log patterns over time", "Detects temporal anomalies", "Better for sequential data"]
    }
  };
  const info = infos[model] || infos.isolation_forest;
  document.getElementById("model-card").innerHTML = `
    <div class="model-card-title">${info.title}</div>
    <ul class="model-card-list">
      ${info.items.map(i => `<li>${i}</li>`).join("")}
    </ul>`;
}

document.getElementById("model-select").addEventListener("change", function () {
  const label = formatLabel(this.value);
  document.getElementById("algo-label").textContent = label;
  updateModelCard(this.value);
  showToast(`Model changed to ${label}\nRestarting pipeline...`, "success");
  autoStartPipeline();
});

document.getElementById("dataset-select").addEventListener("change", function () {
  document.getElementById("dataset-label").textContent = this.value;
  showToast(`Dataset changed to ${this.value}\nRestarting pipeline...`, "success");
  autoStartPipeline();
});

document.getElementById("pipeline-select").addEventListener("change", function () {
  const label = this.options[this.selectedIndex].text;
  showToast(`Pipeline changed to ${label}\nRestarting pipeline...`, "success");
  autoStartPipeline();
});

function getSelected(id) { return document.getElementById(id).value; }
function formatLabel(v)  { return v === "isolation_forest" ? "Isolation Forest" : "LSTM"; }

function formatDataset(v) {
  const map = { synthetic: "Log Simulator", nasa: "NASA HTTP" };
  return map[v] || v;
}

function formatPipeline(v) {
  const map = { file: "Simple Ingest", kafka: "Kafka · Production" };
  return map[v] || v;
}

function startAutoRefresh() {
  if (refreshInterval) clearInterval(refreshInterval);

  refreshInterval = setInterval(async () => {
    await refreshDashboard();
  }, 3000);

  // ✅ FORCE immediate refresh once
  refreshDashboard();
}

function showToast(message, type = "info", duration = 3000) {
  const toast = document.getElementById("toast");
  toast.textContent = message;
  toast.className   = `toast ${type} show`;
  clearTimeout(toast._timer);
  toast._timer = setTimeout(() => {
    toast.className = "toast";
  }, duration);
}

async function autoStartPipeline() {
  const model    = getSelected("model-select");
  const dataset  = getSelected("dataset-select");
  const pipeline = getSelected("pipeline-select");

  // RESET STATE
  lastTotal = -1;

  document.getElementById("algo-label").textContent    = formatLabel(model);
  document.getElementById("dataset-label").textContent = dataset;
  updateModelCard(model);

  try {
    await fetch(`${API}/stop`, { method: "POST" });

    const res  = await fetch(`${API}/start`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ model, dataset, pipeline })
    });

    const data = await res.json();

    if (res.ok) {
      showToast(
        `Pipeline started\nModel: ${formatLabel(model)}\nDataset: ${formatDataset(dataset)}`,
        "success"
      );

      // ✅ THIS IS THE FIX
      setTimeout(() => {
        startAutoRefresh();
      }, 1000);

    } else {
      showToast(
        `Failed to start: ${data.error || data.message}\nCheck backend logs`,
        "error"
      );
    }

  } catch (e) {
    showToast("Backend not reachable", "error");
  }
}


async function loadDropdowns() {
  try {
    const res = await fetch(`${API}/info`);
    const data = await res.json();

    updateSelect("model-select", data.models);
    updateSelect("dataset-select", data.datasets);
    updateSelect("pipeline-select", data.pipelines);

  } catch (e) {
    console.warn("Using default dropdowns (backend not reachable)");
  }
}

function updateSelect(id, options) {
  const select = document.getElementById(id);
  if (!select || !options) return;

  const current = select.value;
  select.innerHTML = "";

  const labelMaps = {
    "model-select": {
      isolation_forest: "Isolation Forest",
      lstm: "LSTM"
    },
    "dataset-select": {
      synthetic: "Log Simulator",
      nasa: "NASA HTTP Logs"
    },
    "pipeline-select": {
      file: "Simple Ingest Pipeline",
      kafka: "Kafka Streaming Pipeline"
    }
  };

  const map = labelMaps[id] || {};


  options.forEach(opt => {
    const option = document.createElement("option");
    option.value = opt;
    option.textContent = map[opt] || opt;
    select.appendChild(option);
  });

  if (options.includes(current)) {
    select.value = current;
  }
}


/* function to wake up render backed */
async function wakeBackend() {
  try {
    await fetch("https://logiq-anomaly-detection.onrender.com");
  } catch (e) {
    console.log("Waking backend...");
  }
}

/* ── Boot ──────────────────────────────────────────────────── */
(async function () {
  initCharts();

  wakeBackend();

  await loadDropdowns();   // ✅ dynamic dropdowns

  refreshDashboard();
  startAutoRefresh();
  autoStartPipeline();
})();


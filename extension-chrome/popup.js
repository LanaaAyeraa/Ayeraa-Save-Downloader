// Ayera Downloader Pro - Extension Popup Logic
const BRIDGE_URL = "http://127.0.0.1:18791";

document.addEventListener("DOMContentLoaded", async () => {
  const statusCard = document.getElementById("status-card");
  const statusText = document.getElementById("status-text");
  const btnRefresh = document.getElementById("btn-refresh");
  const toggleIntercept = document.getElementById("toggle-intercept");
  const toggleFloating = document.getElementById("toggle-floating");
  const inputQuickUrl = document.getElementById("input-quick-url");
  const btnSendUrl = document.getElementById("btn-send-url");
  const sendFeedback = document.getElementById("send-feedback");
  const tagContainer = document.getElementById("tag-container");

  // Load storage preferences
  chrome.storage.local.get(["auto_intercept", "floating_bar", "intercept_extensions"], (res) => {
    toggleIntercept.checked = res.auto_intercept !== false;
    toggleFloating.checked = res.floating_bar !== false;

    const exts = res.intercept_extensions || [
      "zip", "rar", "7z", "iso", "exe", "msi", "apk", "pdf", "mp4", "mkv", "mp3", "flac"
    ];
    tagContainer.innerHTML = exts.map((e) => `<span class="tag">.${e}</span>`).join("");
  });

  // Toggle events
  toggleIntercept.addEventListener("change", () => {
    chrome.storage.local.set({ auto_intercept: toggleIntercept.checked });
  });

  toggleFloating.addEventListener("change", () => {
    chrome.storage.local.set({ floating_bar: toggleFloating.checked });
  });

  // Check connection status
  async function checkBridgeStatus() {
    statusCard.className = "status-card status-checking";
    statusText.textContent = "Menghubungkan ke Ayera Desktop...";

    try {
      const controller = new AbortController();
      const timeoutId = setTimeout(() => controller.abort(), 1200);
      const resp = await fetch(`${BRIDGE_URL}/status`, { signal: controller.signal });
      clearTimeout(timeoutId);

      if (resp.ok) {
        const data = await resp.json();
        statusCard.className = "status-card status-connected";
        statusText.textContent = `🟢 Terhubung (32 Channel Aktif)`;
        return;
      }
    } catch (e) {}

    statusCard.className = "status-card status-disconnected";
    statusText.textContent = "🔴 Terputus (Jalankan Ayera App)";
  }

  btnRefresh.addEventListener("click", checkBridgeStatus);
  checkBridgeStatus();

  // Send Quick URL
  btnSendUrl.addEventListener("click", async () => {
    const url = inputQuickUrl.value.trim();
    if (!url) {
      sendFeedback.style.color = "#EF4444";
      sendFeedback.textContent = "Masukkan URL unduhan yang valid!";
      return;
    }

    sendFeedback.style.color = "#94A3B8";
    sendFeedback.textContent = "Mengirim ke Ayera Downloader...";

    chrome.runtime.sendMessage({ type: "TRIGGER_DOWNLOAD", url: url }, (res) => {
      if (res && res.success) {
        sendFeedback.style.color = "#10B981";
        sendFeedback.textContent = "✓ Berhasil masuk ke antrean 32-channel!";
        inputQuickUrl.value = "";
      } else {
        sendFeedback.style.color = "#EF4444";
        sendFeedback.textContent = "Gagal kirim! Pastikan Ayera Desktop aktif.";
      }
    });
  });
});

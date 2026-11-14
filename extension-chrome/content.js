// Ayera Downloader Pro - Floating Video Panel (IDM Style)
(function () {
  let floatingEnabled = true;

  // Query settings from extension
  chrome.runtime.sendMessage({ type: "GET_CONFIG" }, (config) => {
    if (config && config.floating_bar === false) {
      floatingEnabled = false;
    }
  });

  const observedElements = new WeakSet();

  function scanMediaElements() {
    if (!floatingEnabled) return;

    const mediaList = document.querySelectorAll("video, audio");
    mediaList.forEach((media) => {
      if (observedElements.has(media)) return;
      observedElements.add(media);
      attachAyeraVideoPanel(media);
    });
  }

  function attachAyeraVideoPanel(video) {
    const bar = document.createElement("div");
    bar.className = "ayera-video-panel";
    bar.innerHTML = `
      <div class="ayera-btn">
        <span class="ayera-icon">⚡</span>
        <span class="ayera-text">Download Video with Ayera (32 Lanes)</span>
      </div>
    `;

    document.body.appendChild(bar);

    function updatePosition() {
      if (!video || !video.isConnected) {
        bar.remove();
        return;
      }
      const rect = video.getBoundingClientRect();
      // Only display if video has non-zero size
      if (rect.width < 120 || rect.height < 90) {
        bar.style.display = "none";
        return;
      }
      bar.style.display = "block";
      bar.style.top = `${Math.max(10, rect.top + window.scrollY + 10)}px`;
      bar.style.left = `${Math.max(10, rect.right + window.scrollX - 250)}px`;
    }

    video.addEventListener("mouseenter", () => {
      updatePosition();
      bar.classList.add("ayera-visible");
    });

    video.addEventListener("mouseleave", (e) => {
      // Keep visible if hovering over the bar itself
      if (!bar.contains(e.relatedTarget)) {
        bar.classList.remove("ayera-visible");
      }
    });

    bar.addEventListener("mouseleave", () => {
      bar.classList.remove("ayera-visible");
    });

    bar.addEventListener("click", (e) => {
      e.preventDefault();
      e.stopPropagation();

      const src = video.currentSrc || video.src || window.location.href;
      if (!src) return;

      const pageTitle = document.title ? document.title.replace(/[\\/:*?"<>|]/g, "_") : "Video";
      const filename = `${pageTitle}.mp4`;

      const btnText = bar.querySelector(".ayera-text");
      btnText.textContent = "✓ Queued to Ayera (32 Lanes)...";
      bar.classList.add("ayera-success");

      chrome.runtime.sendMessage(
        {
          type: "TRIGGER_DOWNLOAD",
          url: src,
          filename: filename
        },
        (res) => {
          setTimeout(() => {
            btnText.textContent = "Download Video with Ayera (32 Lanes)";
            bar.classList.remove("ayera-success");
            bar.classList.remove("ayera-visible");
          }, 2500);
        }
      );
    });

    window.addEventListener("scroll", updatePosition, { passive: true });
    window.addEventListener("resize", updatePosition, { passive: true });
  }

  // Initial scan and continuous observer for dynamically inserted players (YouTube, etc.)
  scanMediaElements();
  const observer = new MutationObserver(() => scanMediaElements());
  observer.observe(document.body, { childList: true, subtree: true });
})();

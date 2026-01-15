function pad2(n) {
  return String(n).padStart(2, "0");
}

function setLastUpdatedNow() {
  const el = document.getElementById("lastUpdated");
  if (!el) return;

  const d = new Date();
  el.textContent = `${pad2(d.getHours())}:${pad2(d.getMinutes())}:${pad2(d.getSeconds())}`;
}

document.addEventListener("DOMContentLoaded", () => {
  // 初回表示
  setLastUpdatedNow();

  const debugBtn = document.getElementById("debugToggle");
  const refreshBtn = document.getElementById("refreshBtn");
  const panel = document.getElementById("debugPanel");

  // デバッグ表示の開閉
  if (debugBtn && panel) {
    debugBtn.addEventListener("click", () => {
      panel.hidden = !panel.hidden;
      setLastUpdatedNow();
    });
  }

  // 更新（ページ再読み込み）
  if (refreshBtn) {
    refreshBtn.addEventListener("click", () => {
      window.location.reload();
    });
  }
});

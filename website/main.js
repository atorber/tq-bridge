(() => {
  document.querySelectorAll("[data-copy]").forEach((btn) => {
    const targetId = btn.getAttribute("data-copy");
    const code = document.getElementById(targetId);
    if (!code) return;

    btn.addEventListener("click", async () => {
      const text = code.textContent || "";
      try {
        await navigator.clipboard.writeText(text);
        btn.textContent = "已复制";
      } catch {
        btn.textContent = "复制失败";
      }
      window.setTimeout(() => {
        btn.textContent = "复制";
      }, 1400);
    });
  });
})();

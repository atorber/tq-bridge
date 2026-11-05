(() => {
  const copyBtn = document.querySelector("[data-copy]");
  const code = document.querySelector("#sample-code");
  if (!copyBtn || !code) return;

  copyBtn.addEventListener("click", async () => {
    const text = code.textContent || "";
    try {
      await navigator.clipboard.writeText(text);
      copyBtn.textContent = "已复制";
      window.setTimeout(() => {
        copyBtn.textContent = "复制";
      }, 1400);
    } catch {
      copyBtn.textContent = "复制失败";
      window.setTimeout(() => {
        copyBtn.textContent = "复制";
      }, 1400);
    }
  });
})();

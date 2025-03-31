document.querySelectorAll(".copy").forEach(copyButton => {
    copyButton.addEventListener("click", () => {
        const targetElement = document.querySelector(copyButton.dataset.copy);
        const textToCopy = targetElement.textContent
            .replace(/\s+/g, " ")
            .trim();

        navigator.clipboard.writeText(textToCopy).then(() => {
            const label = copyButton.querySelector(".copy-label");
            const originalText = label.textContent;

            copyButton.disabled = true;
            label.textContent = "Copied!";

            setTimeout(() => {
                copyButton.disabled = false;
                label.textContent = originalText;
            }, 1000);
        });
    });
});
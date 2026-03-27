

chrome.tabs.onUpdated.addListener((tabId, changeInfo, tab) => {
    if (changeInfo.status === 'complete' && tab.url && tab.url.startsWith('http')) {
        let domain = new URL(tab.url).hostname;

        chrome.storage.local.get(['userChoices'], function(result) {
            let choices = result.userChoices || {};

            // If user previously BLOCKED it, show notification immediately
            if (choices[domain] === 'Blocked') {
                showNotify(tab.url, "Blocked (User Choice)", "100");
                return;
            }

            // If user previously ALLOWED it, do nothing (skip AI)
            if (choices[domain] === 'Allowed') return;

            // Otherwise, ask the AI
            fetch("http://127.0.0.1:8000/predict", {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({ url: tab.url })
            })
            .then(res => res.json())
            .then(data => {
                if (data.prediction === "Phishing" || data.prediction === "Suspicious") {
                    showNotify(tab.url, data.prediction, data.confidence);
                }
            });
        });
    }
});

function showNotify(url, type, conf) {
    chrome.notifications.create({
        type: "basic",
        iconUrl: "icon.png",
        title: `Security Alert: ${type}`,
        message: `Site: ${url}\nConfidence: ${conf}%`,
        priority: 2
    });
}
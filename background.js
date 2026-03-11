chrome.tabs.onUpdated.addListener((tabId, changeInfo, tab) => {
  if (changeInfo.status === "complete" && tab.url) {
    fetch("http://127.0.0.1:8000/predict", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ features: extractFeatures(tab.url) })
    })
    .then(res => res.json())
    .then(data => {
      if (data.prediction === "Phishing") {
        chrome.notifications.create({
          type: "basic",
          iconUrl: "icon.png",
          title: "⚠️ Phishing Alert",
          message: "This site may be a phishing attempt!"
        });
      }
    });
  }
});

function extractFeatures(url) {
  return [
    url.length,
    url.includes("https") ? 1 : -1,
    url.includes("@") ? -1 : 1,
    url.split(".").length
  ];
}

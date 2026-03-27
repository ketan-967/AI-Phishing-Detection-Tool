

document.addEventListener('DOMContentLoaded', function() {
    const loadingSection = document.getElementById('loading-section');
    const resultSection = document.getElementById('result-section');
    const statusBadge = document.getElementById('status-badge');
    const confidenceText = document.getElementById('confidence-text');
    const progressFill = document.getElementById('progress-fill');
    const domainText = document.getElementById('domain-text');

    chrome.tabs.query({active: true, currentWindow: true}, function(tabs) {
        let url = tabs[0].url;
        let domain = new URL(url).hostname;
        domainText.textContent = domain;

        chrome.storage.local.get(['userChoices'], function(result) {
            let choices = result.userChoices || {};
            
            if (choices[domain]) {
                showResult(choices[domain] === 'Allowed' ? 'Legitimate' : 'Phishing', 100, true);
            } else {
                fetchPrediction(url);
            }
        });
    });

    function fetchPrediction(url) {
        fetch("http://127.0.0.1:8000/predict", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ url: url })
        })
        .then(res => res.json())
        .then(data => {
            showResult(data.prediction, data.confidence, false);
        })
        .catch(err => {
            showResult("Error", 0, false);
            console.error(err);
        });
    }

    function showResult(prediction, confidence, isManual) {
        loadingSection.classList.add('hidden');
        resultSection.classList.remove('hidden');

        statusBadge.textContent = isManual ? `USER ${prediction}` : prediction;
        statusBadge.className = `status-badge ${prediction}`;
        
        // Animate confidence bar
        confidenceText.textContent = `${confidence}%`;
        progressFill.style.width = `${confidence}%`;
        
        // Color code the bar
        if (prediction === 'Phishing') progressFill.style.background = '#e74c3c';
        else if (prediction === 'Suspicious') progressFill.style.background = '#f1c40f';
        else progressFill.style.background = '#2ecc71';
    }

    // Button Logic
    document.getElementById('allow-btn').onclick = () => saveChoice('Allowed');
    document.getElementById('block-btn').onclick = () => saveChoice('Blocked');
    document.getElementById('reset-btn').onclick = () => {
        chrome.storage.local.clear(() => location.reload());
    };

    function saveChoice(type) {
        chrome.tabs.query({active: true, currentWindow: true}, function(tabs) {
            let domain = new URL(tabs[0].url).hostname;
            chrome.storage.local.get(['userChoices'], function(result) {
                let choices = result.userChoices || {};
                choices[domain] = type;
                chrome.storage.local.set({userChoices: choices}, () => location.reload());
            });
        });
    }
});
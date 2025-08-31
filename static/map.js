document.addEventListener('DOMContentLoaded', () => {
    // --- Chart.js Global Variable ---
    let projectionChart;

    // --- DOM Element References ---
    const dashboardInitialPrompt = document.getElementById('dashboard-initial-prompt');
    const dashboardLoading = document.getElementById('dashboard-loading');
    const dashboardResults = document.getElementById('dashboard-results');
    const locationCoordsEl = document.getElementById('location-coords');
    const techBadgeEl = document.getElementById('tech-recommendation-badge');
    const mapPrompt = document.getElementById('map-prompt');
    const searchInput = document.getElementById('location-search-input');

    // --- Leaflet Map Initialization ---
    const map = L.map('map').setView([22.3511148, 78.6677428], 5);
    L.tileLayer('https://{s}.basemaps.cartocdn.com/light_all/{z}/{x}/{y}{r}.png', {
        attribution: '&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors &copy; <a href="https://carto.com/attributions">CARTO</a>',
        subdomains: 'abcd',
        maxZoom: 20
    }).addTo(map);
    L.control.zoom({ position: 'bottomright' }).addTo(map);

    let marker;

    // --- Map Click Event to Set Marker and Run Analysis ---
    map.on('click', function(e) {
        const { lat, lng } = e.latlng;
        if (mapPrompt) mapPrompt.classList.add('hidden');
        if (marker) {
            marker.setLatLng(e.latlng);
        } else {
            marker = L.marker(e.latlng).addTo(map);
        }
        runAnalysis(lat, lng);
    });

    // --- New Event Handler for Analyze Button ---
    const analyzeButton = document.getElementById('analyze-button');
    const latitudeInput = document.getElementById('latitude');
    const longitudeInput = document.getElementById('longitude');

    if (analyzeButton) {
        analyzeButton.addEventListener('click', () => {
            const lat = parseFloat(latitudeInput.value);
            const lng = parseFloat(longitudeInput.value);

            if (isNaN(lat) || isNaN(lng)) {
                alert('Please enter valid latitude and longitude.');
                return;
            }
            
            runAnalysis(lat, lng);
        });
    }

    // --- Search Input Event Handler ---
    searchInput.addEventListener('keydown', (event) => {
        if (event.key === 'Enter') {
            const query = searchInput.value;
            if (query) {
                geocodeAndAnalyze(query);
            }
        }
    });

    // --- New Geocoding Function ---
    async function geocodeAndAnalyze(query) {
        const url = `https://nominatim.openstreetmap.org/search?format=json&q=${encodeURIComponent(query)}`;
        try {
            const response = await fetch(url);
            const data = await response.json();
            if (data && data.length > 0) {
                const lat = parseFloat(data[0].lat);
                const lon = parseFloat(data[0].lon);
                
                map.setView([lat, lon], 10);
                
                if (mapPrompt) mapPrompt.classList.add('hidden');

                if (marker) {
                    marker.setLatLng([lat, lon]);
                } else {
                    marker = L.marker([lat, lon]).addTo(map);
                }

                runAnalysis(lat, lon);

            } else {
                alert('Location not found. Please try a different name.');
            }
        } catch (error) {
            console.error('Geocoding failed:', error);
            alert('Failed to search for location.');
        }
    }

    // --- Main Analysis Function ---
    async function runAnalysis(lat, lng) {
        dashboardInitialPrompt.classList.add('hidden');
        dashboardResults.classList.add('hidden');
        dashboardLoading.classList.remove('hidden');
        
        try {
            const data = await fetchAnalysisData(lat, lng);
            updateDashboard(data);
            dashboardLoading.classList.add('hidden');
            dashboardResults.classList.remove('hidden');
        } catch (error) {
            console.error('Analysis failed:', error);
            dashboardLoading.classList.add('hidden');
            dashboardInitialPrompt.classList.remove('hidden');
            alert('Failed to analyze location. Please ensure the backend server is running and try again.');
        }
    }

    // --- UI Update Functions ---
    function updateDashboard(data) {
        // Get references to all dashboard elements
        const feasibilityScoreEl = document.getElementById('feasibility-score');
        const policyListEl = document.getElementById('policy-advantages-list');

        // 1. Update Location Coordinates
        locationCoordsEl.textContent = `Lat: ${data.location.lat.toFixed(4)}, Lon: ${data.location.lng.toFixed(4)}`;
        
        // 2. Update Feasibility Score
        if (feasibilityScoreEl) {
            feasibilityScoreEl.textContent = `${data.feasibilityScore}%`;
        }

        // 3. Update Recommended Technology Badge
        techBadgeEl.textContent = data.recommendation.name;
        techBadgeEl.style.backgroundColor = data.recommendation.bgColor;
        techBadgeEl.style.color = data.recommendation.textColor;

        // 4. Update Individual Suitability Scorecards
        updateScorecard('solar', data.scores.solar);
        updateScorecard('wind', data.scores.wind);
        updateScorecard('thermal', data.scores.thermal);

        // 5. Render Production Projection Chart
        renderProjectionChart(data.projection);

        // 6. Update Policy Advantages List
        if (policyListEl) {
            policyListEl.innerHTML = ''; // Clear previous list
            data.policyAdvantages.forEach(advantage => {
                const li = document.createElement('li');
                li.className = 'flex items-start';
                li.innerHTML = `
                    <svg class="w-4 h-4 mr-2 mt-0.5 text-renewal-green flex-shrink-0" fill="currentColor" viewBox="0 0 20 20">
                        <path fill-rule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z" clip-rule="evenodd"></path>
                    </svg>
                    <span>${advantage}</span>
                `;
                policyListEl.appendChild(li);
            });
        }
    }

    function updateScorecard(type, score) {
        const valueEl = document.getElementById(`${type}-score-value`);
        const barEl = document.getElementById(`${type}-score-bar`);
        if (valueEl) valueEl.textContent = `${score}/100`;
        if (barEl) {
            barEl.style.width = '0%';
            setTimeout(() => { barEl.style.width = `${score}%`; }, 100);
        }
    }

    function renderProjectionChart(projectionData) {
        const ctx = document.getElementById('projectionChart').getContext('2d');
        if (projectionChart) projectionChart.destroy();
        
        projectionChart = new Chart(ctx, {
            type: 'line',
            data: {
                labels: projectionData.years,
                datasets: [{
                    label: 'Projected H2 Production (kT)',
                    data: projectionData.values,
                    fill: false,
                    borderColor: 'rgb(75, 192, 192)',
                    tension: 0.1
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                scales: {
                    y: {
                        beginAtZero: true
                    }
                }
            }
        });
    }

    // --- REAL API FUNCTION ---
    // --- API FUNCTION with improved error handling ---
async function fetchAnalysisData(lat, lng) {
    const API_URL = '/map/analyze';
    
    try {
        const response = await fetch(API_URL, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ latitude: lat, longitude: lng }),
        });

        if (!response.ok) {
            // Get more details about the error
            const errorText = await response.text();
            throw new Error(`HTTP error! status: ${response.status}, details: ${errorText}`);
        }

        return await response.json();
    } catch (error) {
        console.error('API request failed:', error);
        if (error.message.includes('Failed to fetch')) {
            throw new Error('Cannot connect to the backend server. Please ensure it is running.');
        } else {
            throw new Error(`Analysis failed: ${error.message}`);
        }
    }
}

// --- Test backend connection on page load ---
async function testBackendConnection() {
    const HEALTH_URL = '/map/health';
    
    try {
        const response = await fetch(HEALTH_URL);
        if (response.ok) {
            console.log('Backend connection successful');
            return true;
        } else {
            console.error('Backend connection failed');
            return false;
        }
    } catch (error) {
        console.error('Cannot connect to backend:', error);
        return false;
    }
}
// Handle Generate Report button click
    document.getElementById('generate-report-btn').addEventListener('click', function() {
        generateDetailedReport();
    });
    
    // Handle download report button
    document.getElementById('download-report').addEventListener('click', function() {
        downloadReport();
    });
    
    // Handle report search input
    document.getElementById('report-search-input').addEventListener('keypress', function(e) {
        if (e.key === 'Enter') {
            askAdditionalQuestion(this.value);
            this.value = '';
        }
    });
});

function generateDetailedReport() {
    const btn = document.getElementById('generate-report-btn');
    const loadingIcon = document.getElementById('report-loading');
    const downloadBtn = document.getElementById('download-report');
    
    // Show loading state, disable download
    btn.disabled = true;
    downloadBtn.disabled = true;
    downloadBtn.classList.add('opacity-50', 'cursor-not-allowed');
    loadingIcon.classList.remove('hidden');
    
    // Get all the analysis data
    const location = document.getElementById('location-coords').textContent;
    const feasibility = document.getElementById('feasibility-score').textContent;
    const recommendedTech = document.getElementById('tech-recommendation-badge').textContent;
    
    // Get coordinates from location text
    const coordsMatch = location.match(/Lat: ([\d.-]+), Lon: ([\d.-]+)/);
    const latitude = coordsMatch ? parseFloat(coordsMatch[1]) : null;
    const longitude = coordsMatch ? parseFloat(coordsMatch[2]) : null;
    
    // Get suitability scores
    const solarScore = document.getElementById('solar-score-value').textContent;
    const windScore = document.getElementById('wind-score-value').textContent;
    const thermalScore = document.getElementById('thermal-score-value').textContent;
    
    // Get regional advantages
    const advantages = [];
    document.querySelectorAll('#policy-advantages-list li').forEach(li => {
        advantages.push(li.textContent);
    });
    
    // Show report section
    document.getElementById('report-section').classList.remove('hidden');
    document.getElementById('report-generating').classList.remove('hidden');
    document.getElementById('report-output').innerHTML = '';
    
    // Prepare the data for the LLM
    const reportData = {
        location: location,
        feasibility: feasibility,
        recommended_technology: recommendedTech,
        suitability_scores: {
            solar_electrolysis: solarScore,
            wind_electrolysis: windScore,
            thermal_with_ccs: thermalScore
        },
        regional_advantages: advantages,
        latitude: latitude,
        longitude: longitude,
        session_id: window.currentSessionId, // For updating existing sessions
        timestamp: new Date().toISOString()
    };
    
    // Store for later use in questions
    window.currentReportData = reportData;
    
    // Send request to generate report
    fetch('/LLM/generate-report', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify(reportData)
    })
    .then(response => {
        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }
        return response.json();
    })
    .then(data => {
        if (data.status === 'success') {
            // Hide generating indicator
            document.getElementById('report-generating').classList.add('hidden');
            
            // Store session ID for future questions
            window.currentSessionId = data.session_id;
            
            // Display the report with typing effect
            typeReport(data.report, function() {
                // Enable download button ONLY after report is fully displayed
                downloadBtn.disabled = false;
                downloadBtn.classList.remove('opacity-50', 'cursor-not-allowed');
                downloadBtn.classList.add('hover:bg-earth-blue-dark');
            });
        } else {
            document.getElementById('report-output').innerHTML = 
                `<p class="text-red-500">Error: ${data.error || 'Failed to generate report'}</p>`;
        }
    })
    .catch(error => {
        console.error('Fetch error:', error);
        document.getElementById('report-output').innerHTML = 
            `<p class="text-red-500">Network error: ${error.message}. Check if the backend is running.</p>`;
        document.getElementById('report-generating').classList.add('hidden');
    })
    .finally(() => {
        // Reset button state (but keep download disabled until report is complete)
        btn.disabled = false;
        loadingIcon.classList.add('hidden');
    });
}

function typeReport(reportText, onComplete) {
    const reportOutput = document.getElementById('report-output');
    reportOutput.innerHTML = '';
    
    let i = 0;
    const speed = 5; // Fast typing speed
    
    function typeWriter() {
        if (i < reportText.length) {
            const char = reportText[i];
            const currentText = reportText.substring(0, i + 1);
            
            // Render markdown as we type
            reportOutput.innerHTML = marked.parse(currentText) + 
                '<span class="ai-typing">|</span>';
            
            i++;
            setTimeout(typeWriter, speed);
        } else {
            // Final render
            reportOutput.innerHTML = marked.parse(reportText);
            
            // Highlight code blocks
            reportOutput.querySelectorAll('pre code').forEach((block) => {
                hljs.highlightElement(block);
            });
            
            // Typeset mathematical formulas
            if (typeof MathJax !== 'undefined') {
                MathJax.typesetPromise([reportOutput]);
            }
            
            // Call completion callback
            if (onComplete) onComplete();
        }
    }
    
    typeWriter();
}

function askAdditionalQuestion(question) {
    if (!question.trim()) return;
    
    const reportOutput = document.getElementById('report-output');
    const questionElement = document.createElement('div');
    questionElement.classList.add('mb-4', 'text-right');
    questionElement.innerHTML = `
        <div class="inline-block bg-indigo-100 rounded-lg px-4 py-2">
            <p class="text-indigo-800">${question}</p>
        </div>
    `;
    reportOutput.appendChild(questionElement);
    
    // Scroll to bottom
    reportOutput.scrollTop = reportOutput.scrollHeight;
    
    // Show typing indicator
    const typingIndicator = document.createElement('div');
    typingIndicator.classList.add('mb-4');
    typingIndicator.innerHTML = `
        <div class="inline-block bg-gray-100 rounded-lg px-4 py-2">
            <p class="text-gray-600">AI is thinking<span class="animate-pulse">...</span></p>
        </div>
    `;
    reportOutput.appendChild(typingIndicator);
    reportOutput.scrollTop = reportOutput.scrollHeight;
    
    // Send question to backend
    fetch('/LLM/ask-question', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({
            question: question,
            report_data: window.currentReportData,
            session_id: window.currentSessionId
        })
    })
    .then(response => {
        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }
        return response.json();
    })
    .then(data => {
        // Remove typing indicator
        reportOutput.removeChild(typingIndicator);
        
        if (data.status === 'success') {
            const answerElement = document.createElement('div');
            answerElement.classList.add('mb-4', 'prose', 'prose-sm', 'max-w-none');
            answerElement.innerHTML = marked.parse(data.answer);
            reportOutput.appendChild(answerElement);
            
            // Store updated session ID
            if (data.session_id) {
                window.currentSessionId = data.session_id;
            }
        } else {
            const errorElement = document.createElement('div');
            errorElement.classList.add('mb-4');
            errorElement.innerHTML = `
                <div class="inline-block bg-red-100 rounded-lg px-4 py-2">
                    <p class="text-red-800">Error: ${data.error || 'Failed to get answer'}</p>
                </div>
            `;
            reportOutput.appendChild(errorElement);
        }
        
        reportOutput.scrollTop = reportOutput.scrollHeight;
    })
    .catch(error => {
        reportOutput.removeChild(typingIndicator);
        
        const errorElement = document.createElement('div');
        errorElement.classList.add('mb-4');
        errorElement.innerHTML = `
            <div class="inline-block bg-red-100 rounded-lg px-4 py-2">
                <p class="text-red-800">Error: ${error.message}</p>
            </div>
        `;
        reportOutput.appendChild(errorElement);
        reportOutput.scrollTop = reportOutput.scrollHeight;
    });
}
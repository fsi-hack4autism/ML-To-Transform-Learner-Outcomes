const skillIds = {
    A: "Cooperation and Reinforcer Effectiveness",
    B: "Visual Performance",
    C: "Receptive Language"
};

const baseUrl = 'https://backend-student-status.azurewebsites.net';

function fetchData(studentId, skillLetter) {
    return $.get(`${baseUrl}/student/${studentId}/skill/${skillLetter}`);
}

function createGraphCard(skillLetter, skillName, scores) {
    const graphId = `graph-${skillLetter}`;
    const card = $(`<div class="card"><div id="${graphId}"></div></div>`);

    const cardsContainer = $('#cards-container');
    cardsContainer.append(card);

    const trace = {
        x: scores.map((_, i) => i + 1),
        y: scores,
        mode: 'lines',
        name: skillName
    };

    const layout = {
        title: skillName,
        xaxis: {title: 'Data Points'},
        yaxis: {title: 'Score'}
    };

    if (typeof Plotly !== 'undefined') {
        Plotly.newPlot(graphId, [trace], layout);
    } else {
        console.error("Plotly is not loaded.");
    }

    return card;
}

function updateWelcomeMessage(studentId) {
    const welcomeMessage = $(`#welcome-message`);
    welcomeMessage.text(`Welcome, Student ${studentId}`);
}

async function updateGraphs(studentId) {
    const cardsContainer = $('#cards-container');
    cardsContainer.empty();
    for (const [skillLetter, skillName] of Object.entries(skillIds)) {
        const scores = await fetchData(studentId, skillLetter);
        const card = createGraphCard(skillLetter, skillName, scores);
        cardsContainer.append(card);
    }
}

$(document).ready(function () {
    const studentIdInput = $('#student-id-input');
    const fetchDataButton = $('#fetch-data-button');
    let studentId = studentIdInput.val();
    updateWelcomeMessage(studentId);
    updateGraphs(studentId);

    fetchDataButton.on('click', function () {
        studentId = studentIdInput.val();
        updateWelcomeMessage(studentId);
        updateGraphs(studentId);
    });
});

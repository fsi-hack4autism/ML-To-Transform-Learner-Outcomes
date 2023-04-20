const skillIds = {
    A: "Cooperation and Reinforcer Effectiveness",
    B: "Visual Performance",
    C: "Receptive Language",
    D: "Motor Imitation",
    E: "Vocal Imitation (Echoics)",
    F: "Requests (Mands)",
    G: "Labeling (Tacts)",
    H: "Intraverbals",
    I: "Spontaneous Vocalizations",
    J: "Syntax and Grammar",
    K: "Play/Leisure Skills"
};

const baseUrl = 'https://backend-student-status.azurewebsites.net';

function createGraphCard(skillLetter, skillName) {
    const graphId = `graph-${skillLetter}`;
    const card = $(`<div class="card"><h4>${skillName}</h4><div id="${graphId}"></div></div>`);

    const layout = {
        xaxis: {title: 'Student Age'},
        yaxis: {title: 'Score'}
    };

    if (typeof Plotly !== 'undefined') {
        Plotly.newPlot(graphId, [], layout);
    } else {
        console.error("Plotly is not loaded.");
    }

    return {card, graphId};
}

async function fetchAndUpdateStudentData(studentId, skillLetter, graphId) {
    const studentData = await $.get(`${baseUrl}/student/${studentId}/skill/${skillLetter}`);
    updateGraph(graphId, studentData, 'Student');
}

async function fetchAndUpdateAverageData(skillLetter, graphId) {
    // const averageData = await $.get(`${baseUrl}/average_skill/${skillLetter}`);
    // updateGraph(graphId, averageData, 'Average');
}

function updateGraph(graphId, scores, traceName) {
    const trace = {
        x: scores.map(scoreObj => scoreObj.student_age),
        y: scores.map(scoreObj => scoreObj.skill_value),
        mode: 'lines',
        name: traceName
    };

    const layout = {
        xaxis: {title: 'Student Age'},
        yaxis: {title: 'Score'}
    };

    if (typeof Plotly !== 'undefined') {
        Plotly.addTraces(graphId, trace);
        Plotly.update(graphId, {}, layout);
    } else {
        console.error("Plotly is not loaded.");
    }
}

async function updateGraphs(studentId) {
    const cardsContainer = $('#cards-container');
    cardsContainer.empty();

    for (const [skillLetter, skillName] of Object.entries(skillIds)) {
        const {card, graphId} = createGraphCard(skillLetter, skillName);
        cardsContainer.append(card);
        fetchAndUpdateStudentData(studentId, skillLetter, graphId);
        fetchAndUpdateAverageData(skillLetter, graphId);
    }
}

function updateWelcomeMessage(studentId) {
    const welcomeMessage = $(`#welcome-message`);
    welcomeMessage.text(`Welcome, Student ${studentId}`);
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

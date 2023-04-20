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
async function fetchData(studentId, skillLetter) {
    const studentData = await $.get(`${baseUrl}/student/${studentId}/skill/${skillLetter}`);
    const averageData = await $.get(`${baseUrl}/average_skill/${skillLetter}`);
    return {studentData, averageData};
}
function createGraphCard(skillLetter, skillName) {
    const graphId = `graph-${skillLetter}`;
    const card = $(`<div class="card"><h4>${skillName}</h4><div id="${graphId}"></div></div>`);
    return {card, graphId};
}

async function fetchAndUpdateData(studentId, skillLetter, graphId) {
    const studentData = await $.get(`${baseUrl}/student/${studentId}/skill/${skillLetter}`);
    const averageData = await $.get(`${baseUrl}/average_skill/${skillLetter}`);
    updateGraph(graphId, studentData, averageData);
}

function updateGraph(graphId, studentScores, averageScores) {
    const studentTrace = {
        x: studentScores.map(scoreObj => scoreObj.student_age),
        y: studentScores.map(scoreObj => scoreObj.skill_value),
        mode: 'lines',
        name: 'Student'
    };

    const averageTrace = {
        x: averageScores.map(scoreObj => scoreObj.student_age),
        y: averageScores.map(scoreObj => scoreObj.skill_value),
        mode: 'lines',
        name: 'Average'
    };

    const layout = {
        xaxis: {title: 'Student Age'},
        yaxis: {title: 'Score'}
    };

    if (typeof Plotly !== 'undefined') {
        Plotly.newPlot(graphId, [studentTrace, averageTrace], layout);
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
        fetchAndUpdateData(studentId, skillLetter, graphId);
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

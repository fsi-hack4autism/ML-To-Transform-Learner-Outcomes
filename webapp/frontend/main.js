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

function createGraphCard(skillLetter, skillName, studentScores, averageScores) {
    const graphId = `graph-${skillLetter}`;
    const card = $(`<div class="card"><div id="${graphId}"></div></div>`);

    const cardsContainer = $('#cards-container');
    cardsContainer.append(card);

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
        title: skillName,
        xaxis: {title: 'Student Age'},
        yaxis: {title: 'Score'}
    };

    if (typeof Plotly !== 'undefined') {
        Plotly.newPlot(graphId, [studentTrace, averageTrace], layout);
    } else {
        console.error("Plotly is not loaded.");
    }

    return card;
}

async function updateGraphs(studentId) {
    const cardsContainer = $('#cards-container');
    cardsContainer.empty();

    const skillPromises = Object.entries(skillIds).map(async ([skillLetter, skillName]) => {
        const {studentData, averageData} = await fetchData(studentId, skillLetter);
        return createGraphCard(skillLetter, skillName, studentData, averageData);
    });

    const cards = await Promise.all(skillPromises);
    cards.forEach(card => cardsContainer.append(card));
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

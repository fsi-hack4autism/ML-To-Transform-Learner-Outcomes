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

function createGraphCard(skillLetter, skillName, cardsContainer) {
    const graphId = `graph-${skillLetter}`;
    const card = $(`<div class="card"><h4>${skillName}</h4><div id="${graphId}"></div></div>`);

    cardsContainer.append(card);

    const layout = {
        width: 500,
        xaxis: {title: 'Student Age'},
        yaxis: {title: 'Score'}
    };

    if (typeof Plotly !== 'undefined') {
        Plotly.newPlot(graphId, [], layout);
    } else {
        console.error("Plotly is not loaded.");
    }

    return graphId;
}

async function fetchAndUpdateStudentData(studentId, skillLetter, graphId) {
    const studentData = await $.get(`${baseUrl}/student/${studentId}/skill/${skillLetter}`);
    updateGraph(graphId, studentData, 'Student');
}

async function fetchAndUpdateAverageData(skillLetter, graphId) {
    const regressionData = await $.get(`${baseUrl}/average_skill/${skillLetter}`);
    const minAge = 0; // you can set this to the minimum age you expect in the data
    const maxAge = 20; // you can set this to the maximum age you expect in the data
    const averageData = generateAverageData(regressionData, minAge, maxAge);
    updateGraph(graphId, averageData, 'Average');
}

function generateAverageData(regressionData, minAge, maxAge) {
    const { intercept, slope } = regressionData;
    const ages = [minAge, maxAge];
    const skillValues = ages.map(age => intercept + slope * age);

    return ages.map((age, index) => ({
        student_age: age,
        skill_value: skillValues[index]
    }));
}

function updateGraph(graphId, scores, traceName) {
    const trace = {
        x: scores.map(scoreObj => scoreObj.student_age),
        y: scores.map(scoreObj => scoreObj.skill_value),
        mode: 'lines',
        name: traceName
    };

    const layout = {
        width: 500,
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
        const graphId = createGraphCard(skillLetter, skillName, cardsContainer);
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

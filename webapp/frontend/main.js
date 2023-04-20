const skillIds = {
    A: "Cooperation and Reinforcer Effectiveness",
    B: "Visual Performance",
    C: "Receptive Language"
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
        x: studentScores.map((_, i) => i + 1),
        y: studentScores,
        mode: 'lines',
        name: 'Student'
    };

    const averageTrace = {
        x: averageScores.map((_, i) => i + 1),
        y: averageScores,
        mode: 'lines',
        name: 'Average'
    };

    const layout = {
        title: skillName,
        xaxis: {title: 'Data Points'},
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
    for (const [skillLetter, skillName] of Object.entries(skillIds)) {
        const {studentData, averageData} = await fetchData(studentId, skillLetter);
        const card = createGraphCard(skillLetter, skillName, studentData, averageData);
        cardsContainer.append(card);
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

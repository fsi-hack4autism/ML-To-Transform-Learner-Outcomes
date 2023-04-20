import pandas as pd
from flask import Flask, jsonify
import zipfile
import logging
import re
import numpy as np
from datetime import datetime

app = Flask(__name__)


# Unzip and load the dataset
zip_filename = 'joinedData_assessmentStudentAssessor3_clean Anonymized.zip'
csv_filename = 'joinedData_assessmentStudentAssessor3_clean Anonymized.csv'

with zipfile.ZipFile(zip_filename, 'r') as zf:
    with zf.open(csv_filename) as f:
        data = pd.read_csv(f)

def aggregate_skills(student_data, skill_id):
    pattern = re.compile(f"^{skill_id}\d{{0,3}}$")
    skill_columns = [col for col in student_data.columns if pattern.match(col)]
    skill_values = student_data[skill_columns].sum(axis=1).tolist()

    # Get the row where FirstAssessment_byStudent is 1
    initial_assessment_row = student_data[student_data['FirstAssessment_byStudent'] == 1].iloc[0]
    student_initial_age = initial_assessment_row['StudentAgeAtAssesment']
    student_initial_assessment_date = datetime.strptime(initial_assessment_row['assessmentDate'], '%m/%d/%Y')

    # Calculate student_age for each row based on assessmentDate
    student_ages = []
    for assessment_date in student_data['assessmentDate']:
        date_obj = datetime.strptime(assessment_date, '%m/%d/%Y')
        days_difference = (date_obj - student_initial_assessment_date).days
        adjusted_age = student_initial_age + (days_difference / 365.25)
        student_ages.append(adjusted_age)

    logging.info("Loaded %s values and the first looks like: %s", len(skill_values), skill_values[0])

    # Combine skill_values and student_ages into a list of dictionaries
    combined_data = [{"skill_value": skill_value, "student_age": student_age} for skill_value, student_age in zip(skill_values, student_ages)]
    return combined_data

@app.route('/student/<string:student_id>/skill/<string:skill_id>')
def get_student_skill(student_id, skill_id):
    student_data = data[data['StudentId'] == student_id]
    if student_data.empty:
        return jsonify({"error": "Student not found"}), 404

    skill_values = aggregate_skills(student_data, skill_id)

    if not skill_values:
        return jsonify({"error": "Skill not found"}), 404

    return jsonify(skill_values)

# Initialize cache dictionary
skill_average_cache = {}

import numpy as np

@app.route('/average_skill/<string:skill_id>', methods=['GET'])
def get_average_skill(skill_id):
    # Check if the skill_id is already cached
    if skill_id in skill_average_cache:
        return jsonify(skill_average_cache[skill_id])

    unique_students = data['StudentId'].unique()
    all_student_ages = []
    all_skill_values = []

    for student_id in unique_students:
        student_data = data[data['StudentId'] == student_id]
        student_skill_data = aggregate_skills(student_data, skill_id)

        for skill_data in student_skill_data:
            all_student_ages.append(skill_data['student_age'])
            all_skill_values.append(skill_data['skill_value'])

    if not all_skill_values:
        return jsonify({"error": "Skill not found"}), 404

    # Calculate the best fit line's slope and intercept
    slope, intercept = np.polyfit(all_student_ages, all_skill_values, 1)

    # Store the calculated slope and intercept in cache
    skill_average_cache[skill_id] = {"slope": slope, "intercept": intercept}

    return jsonify(skill_average_cache[skill_id])




# Sanity checker and health check
@app.route("/hello")
def hello():
    return "Hello, World!"

if __name__ == '__main__':
    logging.info("### Welcome to student status backend ###")
    app.run(debug=True)

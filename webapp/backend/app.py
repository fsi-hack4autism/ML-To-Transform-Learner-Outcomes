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
    default_age_bump_between_tests = 0.1

    pattern = re.compile(f"^{skill_id}\d{{0,3}}$")
    skill_columns = [col for col in student_data.columns if pattern.match(col)]
    skill_values = student_data[skill_columns].sum(axis=1).tolist()

    initial_assessment_row = student_data[student_data['FirstAssessment_byStudent'] == 1].iloc[0]
    student_initial_age = initial_assessment_row['StudentAgeAtAssesment']

    try:
        student_initial_assessment_date = datetime.strptime(initial_assessment_row['assessmentDate'], '%m/%d/%Y')
    except (ValueError, TypeError):
        try:
            student_initial_assessment_date = datetime.strptime(initial_assessment_row['assessmentDate'], '%Y-%m-%d')
        except (ValueError, TypeError):
            return []

    student_ages = []
    filtered_skill_values = []
    for i, assessment_date in enumerate(student_data['assessmentDate']):
        try:
            date_obj = datetime.strptime(assessment_date, '%m/%d/%Y')
        except (ValueError, TypeError):
            try:
                date_obj = datetime.strptime(assessment_date, '%Y-%m-%d')
            except (ValueError, TypeError):
                if student_ages:
                    adjusted_age = student_ages[-1] + default_age_bump_between_tests
                else:
                    adjusted_age = student_initial_age
                if not pd.isna(adjusted_age):
                    student_ages.append(adjusted_age)
                    filtered_skill_values.append(skill_values[i])
                continue

        days_difference = (date_obj - student_initial_assessment_date).days
        adjusted_age = student_initial_age + (days_difference / 365.25)

        # Ensure ages are always ascending and never duplicated
        if student_ages and adjusted_age <= student_ages[-1]:
            adjusted_age = student_ages[-1] + default_age_bump_between_tests

        # Filter out NaN ages
        if not pd.isna(adjusted_age):
            student_ages.append(adjusted_age)
            filtered_skill_values.append(skill_values[i])

    combined_data = [{"skill_value": skill_value, "student_age": student_age} for skill_value, student_age in zip(filtered_skill_values, student_ages)]
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
from scipy.stats import linregress

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

    # Check for the number of unique values in the input arrays
    if len(set(all_student_ages)) <= 1 or len(set(all_skill_values)) <= 1:
        return jsonify({"error": "Not enough unique data points to calculate a trend line"}), 400

    # Calculate the best fit line's slope, intercept, and other values
    slope, intercept, r_value, p_value, std_err = linregress(all_student_ages, all_skill_values)

    # Store the calculated slope, intercept, and other values in cache
    skill_average_cache[skill_id] = {"slope": slope, "intercept": intercept, "r_value": r_value, "p_value": p_value, "std_err": std_err}

    return jsonify(skill_average_cache[skill_id])


@app.route('/all_skill_values/<string:skill_id>', methods=['GET'])
def get_all_skill_values(skill_id):
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

    return jsonify({"ages": all_student_ages, "skill_values": all_skill_values})


# Sanity checker and health check
@app.route("/hello")
def hello():
    return "Hello, World!"

if __name__ == '__main__':
    logging.info("### Welcome to student status backend ###")
    app.run(debug=True)

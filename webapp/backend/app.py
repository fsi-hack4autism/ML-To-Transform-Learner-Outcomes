import pandas as pd
from flask import Flask, jsonify
import zipfile
import logging
import re

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
    logging.info("Loaded %s values and the first looks like: %s", len(skill_values), skill_values[0])
    return skill_values

@app.route('/student/<string:student_id>/skill/<string:skill_id>')
def get_student_skill(student_id, skill_id):
    student_data = data[data['StudentId'] == student_id]
    if student_data.empty:
        return jsonify({"error": "Student not found"}), 404

    skill_values = aggregate_skills(student_data, skill_id)

    if not skill_values:
        return jsonify({"error": "Skill not found"}), 404

    return jsonify(skill_values)

@app.route('/average_skill/<string:skill_id>', methods=['GET'])
def get_average_skill(skill_id):
    unique_students = student_data['student_id'].unique()
    num_students = len(unique_students)
    average_skill_values = []

    for student_id in unique_students:
        student_skill_data = student_data[student_data['student_id'] == student_id]
        student_skill_values = aggregate_skills(student_skill_data, skill_id)
        average_student_skill_value = sum(student_skill_values) / num_students
        average_skill_values.append(average_student_skill_value)

    if not average_skill_values:
        return jsonify({"error": "Skill not found"}), 404

    return jsonify(average_skill_values)

# Sanity checker and health check
@app.route("/hello")
def hello():
    return "Hello, World!"

if __name__ == '__main__':
    logging.info("### Welcome to student status backend ###")
    app.run(debug=True)

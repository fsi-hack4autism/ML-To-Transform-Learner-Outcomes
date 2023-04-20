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

# Initialize cache dictionary
skill_average_cache = {}

@app.route('/average_skill/<string:skill_id>', methods=['GET'])
def get_average_skill(skill_id):
    # Check if the skill_id is already cached
    if skill_id in skill_average_cache:
        return jsonify(skill_average_cache[skill_id])

    unique_students = data['StudentId'].unique()
    skill_sums = {}
    skill_counts = {}

    for student_id in unique_students:
        student_data = data[data['StudentId'] == student_id]
        student_skill_values = aggregate_skills(student_data, skill_id)

        for i, skill_value in enumerate(student_skill_values):
            if i not in skill_sums:
                skill_sums[i] = 0
                skill_counts[i] = 0

            skill_sums[i] += skill_value
            skill_counts[i] += 1

    if not skill_sums:
        return jsonify({"error": "Skill not found"}), 404

    average_skill_values = [skill_sums[i] / skill_counts[i] for i in skill_sums]

    # Store the calculated average skill values in cache
    skill_average_cache[skill_id] = average_skill_values

    return jsonify(average_skill_values)



# Sanity checker and health check
@app.route("/hello")
def hello():
    return "Hello, World!"

if __name__ == '__main__':
    logging.info("### Welcome to student status backend ###")
    app.run(debug=True)

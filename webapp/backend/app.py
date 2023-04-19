import pandas as pd
from flask import Flask, jsonify

app = Flask(__name__)


# Unzip and load the dataset
zip_filename = 'joinedData_assessmentStudentAssessor3_clean Anonymized.zip'
csv_filename = 'joinedData_assessmentStudentAssessor3_clean Anonymized.csv'

with zipfile.ZipFile(zip_filename, 'r') as zf:
    with zf.open(csv_filename) as f:
        data = pd.read_csv(f)

def aggregate_skills(student_data, skill_id):
    skill_columns = [col for col in student_data.columns if col.startswith(skill_id)]
    skill_values = student_data[skill_columns].values.tolist()
    return skill_values

@app.route('/student/<student_id>/skill/<skill_id>')
def get_student_skill(student_id, skill_id):
    student_data = data[data['StudentId'] == student_id]
    if student_data.empty:
        return jsonify({"error": "Student not found"}), 404

    skill_values = aggregate_skills(student_data, skill_id)

    if not skill_values:
        return jsonify({"error": "Skill not found"}), 404

    return jsonify(skill_values)

# Sanity checker
@app.route("/")
def hello():
    return "Hello, World!"

if __name__ == '__main__':
    app.run(debug=True)

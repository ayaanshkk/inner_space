from flask import Flask, jsonify, request
from flask_cors import CORS
import uuid
from datetime import datetime

app = Flask(__name__)
CORS(app)

# Temporary in-memory storage - replace with database later
customers = []
jobs = []
assignments = []
staff_members = [
    {"id": 1, "name": "John Smith", "role": "Installer", "user_id": "staff-001"},
    {"id": 2, "name": "Mike Johnson", "role": "Installer", "user_id": None},
    {"id": 3, "name": "Sarah Wilson", "role": "Measuring", "user_id": None},
    {"id": 4, "name": "Tom Brown", "role": "Installer", "user_id": None},
    {"id": 5, "name": "Lisa Davis", "role": "Delivery", "user_id": None},
]

@app.route('/customers', methods=['GET', 'POST'])
def handle_customers():
    if request.method == 'GET':
        return jsonify(customers)
    
    data = request.json
    customer = {
        'id': str(uuid.uuid4()),
        'created_at': datetime.now().isoformat(),
        'updated_at': datetime.now().isoformat(),
        'stage': data.get('stage', 'Lead'),
        'contact_made': data.get('contact_made', 'Unknown'),
        'marketing_opt_in': data.get('marketing_opt_in', False),
        'status': data.get('status', 'active'),
        **data
    }
    customers.append(customer)
    return jsonify(customer), 201

@app.route('/customers/<customer_id>', methods=['GET', 'PUT', 'DELETE'])
def handle_customer(customer_id):
    global customers
    customer = next((c for c in customers if c['id'] == customer_id), None)
    
    if request.method == 'GET':
        return jsonify(customer) if customer else ('', 404)
    
    elif request.method == 'PUT':
        if customer:
            data = request.json
            customer.update(data)
            customer['updated_at'] = datetime.now().isoformat()
            return jsonify(customer)
        return ('', 404)
    
    elif request.method == 'DELETE':
        customers = [c for c in customers if c['id'] != customer_id]
        return '', 204

@app.route('/customers/active', methods=['GET'])
def get_active_customers():
    """Return active customers"""
    active = [c for c in customers if c.get('status') == 'active']
    return jsonify(active)

@app.route('/jobs', methods=['GET', 'POST'])
def handle_jobs():
    if request.method == 'GET':
        return jsonify(jobs)
    
    data = request.json
    job = {
        'id': str(uuid.uuid4()),
        'created_at': datetime.now().isoformat(),
        'updated_at': datetime.now().isoformat(),
        'stage': data.get('stage', 'Lead'),
        'job_type': data.get('job_type', 'Kitchen'),
        **data
    }
    jobs.append(job)
    return jsonify(job), 201

@app.route('/jobs/<job_id>', methods=['GET', 'PUT', 'DELETE'])
def handle_job(job_id):
    global jobs
    job = next((j for j in jobs if j['id'] == job_id), None)
    
    if request.method == 'GET':
        return jsonify(job) if job else ('', 404)
    
    elif request.method == 'PUT':
        if job:
            data = request.json
            job.update(data)
            job['updated_at'] = datetime.now().isoformat()
            return jsonify(job)
        return ('', 404)
    
    elif request.method == 'DELETE':
        jobs = [j for j in jobs if j['id'] != job_id]
        return '', 204

@app.route('/jobs/available', methods=['GET'])
def get_available_jobs():
    """Return jobs that are available for scheduling"""
    # Return jobs that are in certain stages ready for scheduling
    available = [j for j in jobs if j.get('stage') in ['Quoted', 'Accepted', 'Production', 'ready']]
    return jsonify(available)

@app.route('/assignments', methods=['GET', 'POST'])
def handle_assignments():
    if request.method == 'GET':
        return jsonify(assignments)
    
    data = request.json
    assignment = {
        'id': str(uuid.uuid4()),
        'created_at': datetime.now().isoformat(),
        'updated_at': datetime.now().isoformat(),
        'type': data.get('type', 'job'),
        'staff_id': data.get('staff_id'),
        'date': data.get('date'),
        'start_time': data.get('start_time'),
        'end_time': data.get('end_time'),
        'estimated_hours': data.get('estimated_hours', 0),
        'priority': data.get('priority', 'Medium'),
        'status': data.get('status', 'Scheduled'),
        'title': data.get('title', ''),
        'notes': data.get('notes', ''),
        'job_id': data.get('job_id'),
        'customer_id': data.get('customer_id'),
        **data
    }
    assignments.append(assignment)
    return jsonify({'assignment': assignment}), 201

# Add this route with your other routes
@app.route('/staff', methods=['GET'])
def get_staff():
    """Return all staff members"""
    return jsonify(staff_members)

@app.route('/assignments/<assignment_id>', methods=['GET', 'PUT', 'DELETE'])
def handle_assignment(assignment_id):
    global assignments
    assignment = next((a for a in assignments if a['id'] == assignment_id), None)
    
    if request.method == 'GET':
        return jsonify(assignment) if assignment else ('', 404)
    
    elif request.method == 'PUT':
        if assignment:
            data = request.json
            assignment.update(data)
            assignment['updated_at'] = datetime.now().isoformat()
            return jsonify({'assignment': assignment})
        return ('', 404)
    
    elif request.method == 'DELETE':
        assignments = [a for a in assignments if a['id'] != assignment_id]
        return '', 204

@app.route('/pipeline', methods=['GET'])
def get_pipeline():
    pipeline_items = []
    
    # Add customers without jobs
    for customer in customers:
        has_job = any(j.get('customer_id') == customer['id'] for j in jobs)
        if not has_job:
            pipeline_items.append({
                'id': f"customer-{customer['id']}",
                'type': 'customer',
                'customer': customer
            })
    
    # Add jobs with their customers
    for job in jobs:
        customer = next((c for c in customers if c['id'] == job.get('customer_id')), None)
        if customer:
            pipeline_items.append({
                'id': f"job-{job['id']}",
                'type': 'job',
                'customer': customer,
                'job': job
            })
    
    return jsonify(pipeline_items)

@app.route('/health', methods=['GET'])
def health_check():
    return jsonify({
        'status': 'healthy',
        'timestamp': datetime.now().isoformat(),
        'customers_count': len(customers),
        'jobs_count': len(jobs),
        'assignments_count': len(assignments)
    })

if __name__ == '__main__':
    app.run(debug=True, port=5000)
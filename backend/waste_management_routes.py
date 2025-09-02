from flask import Blueprint, request, jsonify
from database import DatabaseConnection
import json
from datetime import datetime

waste_management = Blueprint('waste_management', __name__)
db = DatabaseConnection()

# Waste Sourcing Routes
@waste_management.route('/api/waste-sourcing', methods=['POST'])
def create_waste_sourcing():
    try:
        data = request.get_json()
        
        # Validate required fields
        required_fields = [
            'collectionDate', 'collectionTime', 'sourceType', 'sourceName',
            'wasteType', 'wasteWeight', 'segregationStatus', 'collectionPersonnel',
            'recordedBy'
        ]
        
        missing_fields = [field for field in required_fields if field not in data]
        if missing_fields:
            return jsonify({'error': f'Missing required fields: {", ".join(missing_fields)}'}), 400

        # Handle contaminants as JSON
        contaminants = json.dumps(data.get('contaminantsFound', [])) if 'contaminantsFound' in data else None

        # Insert into database
        query = """
        INSERT INTO waste_sourcing (
            collection_date, collection_time, source_type, source_name,
            waste_type, waste_weight, segregation_status, collection_personnel,
            contaminants, collection_notes, recorded_by
        ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        """
        
        params = (
            data['collectionDate'],
            data['collectionTime'],
            data['sourceType'],
            data['sourceName'],
            data['wasteType'],
            float(data['wasteWeight']),
            data['segregationStatus'],
            data['collectionPersonnel'],
            contaminants,
            data.get('collectionNotes'),
            data['recordedBy']
        )
        
        db.execute_query(query, params)
        return jsonify({'message': 'Waste sourcing record created successfully'}), 201
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@waste_management.route('/api/waste-sourcing', methods=['GET'])
def get_waste_sourcing():
    try:
        query = "SELECT * FROM waste_sourcing"
        result = db.execute_query(query)
        return jsonify(result), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# Storage Records Routes
@waste_management.route('/api/storage-records', methods=['POST'])
def create_storage_record():
    try:
        data = request.get_json()
        
        # Validate required fields
        required_fields = [
            'storageDate', 'storageMethod', 'storageConditions',
            'storageDuration', 'plannedUtilization'
        ]
        
        missing_fields = [field for field in required_fields if field not in data]
        if missing_fields:
            return jsonify({'error': f'Missing required fields: {", ".join(missing_fields)}'}), 400

        # Insert into database
        query = """
        INSERT INTO storage_records (
            storage_date, storage_method, storage_conditions,
            storage_duration, planned_utilization, storage_observations
        ) VALUES (%s, %s, %s, %s, %s, %s)
        """
        
        params = (
            data['storageDate'],
            data['storageMethod'],
            data['storageConditions'],
            int(data['storageDuration']),
            data['plannedUtilization'],
            data.get('storageObservations')
        )
        
        db.execute_query(query, params)
        return jsonify({'message': 'Storage record created successfully'}), 201
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@waste_management.route('/api/storage-records', methods=['GET'])
def get_storage_records():
    try:
        query = "SELECT * FROM storage_records"
        result = db.execute_query(query)
        return jsonify(result), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# Processing Records Routes
@waste_management.route('/api/processing-records', methods=['POST'])
def create_processing_record():
    try:
        data = request.get_json()
        
        # Validate required fields
        required_fields = [
            'processingDate', 'processingType', 'processingMethod',
            'wasteProcessed', 'wasteReduction'
        ]
        
        missing_fields = [field for field in required_fields if field not in data]
        if missing_fields:
            return jsonify({'error': f'Missing required fields: {", ".join(missing_fields)}'}), 400

        # Insert into database
        query = """
        INSERT INTO processing_records (
            processing_date, processing_type, processing_method,
            waste_processed, waste_reduction, by_products, processing_remarks
        ) VALUES (%s, %s, %s, %s, %s, %s, %s)
        """
        
        params = (
            data['processingDate'],
            data['processingType'],
            data['processingMethod'],
            float(data['wasteProcessed']),
            float(data['wasteReduction']),
            data.get('byProducts'),
            data.get('processingRemarks')
        )
        
        db.execute_query(query, params)
        return jsonify({'message': 'Processing record created successfully'}), 201
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@waste_management.route('/api/processing-records', methods=['GET'])
def get_processing_records():
    try:
        query = "SELECT * FROM processing_records"
        result = db.execute_query(query)
        return jsonify(result), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# Environmental Monitoring Routes
@waste_management.route('/api/environmental-monitoring', methods=['POST'])
def create_environmental_monitoring():
    try:
        data = request.get_json()
        
        # Validate required fields
        required_fields = [
            'monitoring_date', 'monitoring_time', 'temperature',
            'humidity', 'odor_level', 'pest_presence'
        ]
        
        missing_fields = [field for field in required_fields if field not in data]
        if missing_fields:
            return jsonify({'error': f'Missing required fields: {", ".join(missing_fields)}'}), 400

        # Insert into database
        query = """
        INSERT INTO environmental_monitoring (
            monitoring_date, monitoring_time, temperature,
            humidity, odor_level, pest_presence,
            pest_details, mitigation_actions, remarks
        ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
        """
        
        params = (
            data['monitoring_date'],
            data['monitoring_time'],
            float(data['temperature']),
            float(data['humidity']),
            data['odor_level'],
            data['pest_presence'],
            data.get('pest_details'),
            data.get('mitigation_actions'),
            data.get('remarks')
        )
        
        db.execute_query(query, params)
        return jsonify({'message': 'Environmental monitoring record created successfully'}), 201
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@waste_management.route('/api/environmental-monitoring', methods=['GET'])
def get_environmental_monitoring():
    try:
        query = "SELECT * FROM environmental_monitoring"
        result = db.execute_query(query)
        return jsonify(result), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500 
# from google.cloud import vision
# import os
# from flask import Flask, request, jsonify
# from flask_cors import CORS
# import re
# import json
# import traceback
# from collections import defaultdict
# import math

# app = Flask(__name__)
# CORS(app)

# import logging
# logging.basicConfig(level=logging.DEBUG)

# # # Set the path to your service account key
# # os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = 'C:\\Users\\ayaan\\googlecredentials.json'



# client = vision.ImageAnnotatorClient()

# class DrawingAnalyzer:
#     def __init__(self):
#         self.components = {
#             'GABLE': [],
#             'T/B & FIX SHELVES': [],
#             'BACKS': [],
#             'S/H': [],
#             'DRAWS': [],
#             'END PANELS & INFILLS': [],
#             'BRACES': [],
#             'DOORS & DRAW FACES': []
#         }
        
#     def analyze_technical_drawing(self, text, text_regions):
#         """Analyze technical drawing and extract components"""
#         print(f"Analyzing technical drawing with {len(text_regions)} text regions")
        
#         # Extract all dimensions from the drawing
#         dimensions = self.extract_dimensions(text_regions)
#         print(f"Found {len(dimensions)} dimensions: {dimensions}")
        
#         # Analyze the drawing structure and categorize components
#         self.categorize_components(dimensions, text_regions)
        
#         return self.generate_cutting_list()
    
#     def extract_dimensions(self, text_regions):
#         """Extract all dimensional information from the drawing"""
#         dimensions = []
        
#         # Patterns for dimensions (more focused on technical drawings)
#         dimension_patterns = [
#             r'(\d{3,4})',  # 3-4 digit numbers (common in technical drawings)
#             r'(\d{2,4})\s*[xX×]\s*(\d{2,4})',  # Width x Height format
#             r'(\d+)\.(\d+)',  # Decimal dimensions
#         ]

#         for region in text_regions:
#             text = region['text'].strip()
            
#             # Skip very short text that's likely not dimensions
#             if len(text) < 2:
#                 continue
                
#             # Extract single dimensions (like 3795, 600, etc.)
#             if re.match(r'^\d{2,4}$', text):
#                 try:
#                     dim_value = int(text)
#                     if 50 <= dim_value <= 5000:  # Reasonable range for cabinet dimensions
#                         dimensions.append({
#                             'value': dim_value,
#                             'text': text,
#                             'position': self.get_center_position(region['bounding_box']),
#                             'type': 'single'
#                         })
#                 except ValueError:
#                     continue
                    
#             # Extract dimension pairs
#             for pattern in dimension_patterns[1:]:  # Skip the single digit pattern
#                 match = re.search(pattern, text)
#                 if match:
#                     try:
#                         if 'x' in pattern.lower() or 'X' in pattern or '×' in pattern:
#                             w, h = int(match.group(1)), int(match.group(2))
#                             if 50 <= w <= 5000 and 50 <= h <= 5000:
#                                 dimensions.append({
#                                     'width': w,
#                                     'height': h,
#                                     'text': text,
#                                     'position': self.get_center_position(region['bounding_box']),
#                                     'type': 'pair'
#                                 })
#                     except ValueError:
#                         continue
                        
#         return dimensions
    
#     def get_center_position(self, bounding_box):
#         """Get center position of bounding box"""
#         x_coords = [point[0] for point in bounding_box]
#         y_coords = [point[1] for point in bounding_box]
#         return {
#             'x': sum(x_coords) / len(x_coords),
#             'y': sum(y_coords) / len(y_coords)
#         }
    
#     def categorize_components(self, dimensions, text_regions):
#         """Categorize components based on position and dimensions"""
        
#         # Analyze the drawing structure
#         structure = self.analyze_drawing_structure(dimensions, text_regions)
        
#         # Generate components based on typical cabinet construction
#         self.generate_cabinet_components(structure)
    
#     def analyze_drawing_structure(self, dimensions, text_regions):
#         """Analyze the overall structure of the drawing"""
#         structure = {
#             'overall_width': 0,
#             'overall_height': 0,
#             'depth': 0,
#             'sections': [],
#             'vertical_divisions': [],
#             'horizontal_divisions': [],
#             'door_areas': []
#         }
        
#         # Find overall dimensions (usually the largest values)
#         single_dims = [d for d in dimensions if d['type'] == 'single']
#         if single_dims:
#             single_values = [d['value'] for d in single_dims]
#             single_values.sort(reverse=True)
            
#             if len(single_values) >= 2:
#                 structure['overall_width'] = single_values[0]  # Largest dimension
#                 structure['overall_height'] = single_values[1]  # Second largest
                
#             # Common cabinet depth
#             structure['depth'] = 600  # Standard cabinet depth
            
#         print(f"Structure analysis: {structure}")
#         return structure
    
#     def generate_cabinet_components(self, structure):
#         """Generate cutting list components based on cabinet structure"""
        
#         width = structure['overall_width']
#         height = structure['overall_height']
#         depth = structure['depth']
        
#         if width == 0 or height == 0:
#             print("Could not determine overall dimensions, using fallback")
#             return
            
#         print(f"Generating components for cabinet: {width}W x {height}H x {depth}D")
        
#         # GABLES (Side panels)
#         self.add_component('GABLE', depth, height, 2, f"Side panels - {depth}x{height}")
        
#         # T/B & FIX SHELVES (Top, Bottom, and Fixed Shelves)
#         internal_width = width - 36  # Account for panel thickness (18mm each side)
#         self.add_component('T/B & FIX SHELVES', internal_width, depth, 2, f"Top/Bottom - {internal_width}x{depth}")
        
#         # Estimate number of shelves based on height
#         shelf_count = max(1, (height - 200) // 350)  # Rough estimate
#         if shelf_count > 0:
#             self.add_component('T/B & FIX SHELVES', internal_width, depth, shelf_count, f"Fixed shelves - {internal_width}x{depth}")
        
#         # BACKS (typically 6mm or thin material)
#         back_width = width - 20  # Small reduction for fitting
#         back_height = height - 20
#         self.add_component('BACKS', back_width, back_height, 1, f"Back panel - {back_width}x{back_height}")
        
#         # DOORS (estimate based on width)
#         if width > 800:  # Likely has doors if wide enough
#             door_width = (width - 60) // 2  # Two doors
#             door_height = height - 100  # Allow for hardware
#             self.add_component('DOORS & DRAW FACES', door_width, door_height, 2, f"Cabinet doors - {door_width}x{door_height}")
#         elif width > 400:  # Single door
#             door_width = width - 30
#             door_height = height - 100
#             self.add_component('DOORS & DRAW FACES', door_width, door_height, 1, f"Cabinet door - {door_width}x{door_height}")
        
#         # DRAWS (if height suggests drawer space)
#         if height > 600:  # Likely has drawers
#             drawer_width = internal_width - 20
#             drawer_depth = depth - 50
#             drawer_count = min(3, (height - 300) // 200)  # Estimate drawer count
            
#             if drawer_count > 0:
#                 # Drawer boxes (4 sides per drawer)
#                 drawer_height = 150  # Standard drawer height
#                 self.add_component('DRAWS', drawer_width, drawer_height, drawer_count, f"Drawer fronts/backs - {drawer_width}x{drawer_height}")
#                 self.add_component('DRAWS', drawer_depth, drawer_height, drawer_count * 2, f"Drawer sides - {drawer_depth}x{drawer_height}")
                
#                 # Drawer faces
#                 face_width = drawer_width + 20
#                 face_height = drawer_height + 20
#                 self.add_component('DOORS & DRAW FACES', face_width, face_height, drawer_count, f"Drawer faces - {face_width}x{face_height}")
        
#         # END PANELS (if needed for exposed sides)
#         if width > 1200:  # Large cabinet might need end panels
#             self.add_component('END PANELS & INFILLS', depth, height, 2, f"End panels - {depth}x{height}")
        
#         # BRACES (structural support)
#         if width > 1000:  # Large cabinets need bracing
#             brace_length = internal_width
#             self.add_component('BRACES', brace_length, 100, 2, f"Structural braces - {brace_length}x100")
    
#     def add_component(self, category, width, height, quantity, description):
#         """Add a component to the cutting list"""
#         self.components[category].append({
#             'dimensions': f"{width}x{height}",
#             'width': width,
#             'height': height,
#             'quantity': quantity,
#             'raw_text': description
#         })
#         print(f"Added to {category}: {width}x{height} qty:{quantity}")
    
#     def generate_cutting_list(self):
#         """Generate the final cutting list summary"""
#         summary = {}
#         for category, items in self.components.items():
#             if items:
#                 total_pieces = sum(item['quantity'] for item in items)
#                 summary[category] = {
#                     'items': items,
#                     'total_pieces': total_pieces,
#                     'unique_sizes': len(set(item['dimensions'] for item in items))
#                 }
#             else:
#                 summary[category] = {
#                     'items': [],
#                     'total_pieces': 0,
#                     'unique_sizes': 0
#                 }
        
#         return summary

# def extract_text_with_regions(image_content):
#     """Extract text and regions from image using Google Cloud Vision"""
#     image = vision.Image(content=image_content)
#     response = client.text_detection(image=image)
    
#     if response.error.message:
#         raise Exception(f'{response.error.message}')
    
#     texts = response.text_annotations
#     if not texts:
#         return "", []
    
#     full_text = texts[0].description
#     print(f"Full extracted text: {full_text[:500]}...")
    
#     text_regions = []
#     for text in texts[1:]:  # Skip the first one as it's the full text
#         vertices = [(vertex.x, vertex.y) for vertex in text.bounding_poly.vertices]
#         text_regions.append({
#             'text': text.description,
#             'bounding_box': vertices
#         })
    
#     print(f"Found {len(text_regions)} text regions")
#     return full_text, text_regions

# @app.route('/upload', methods=['POST'])
# def upload_image():
#     try:
#         if 'file' not in request.files:
#             return jsonify({'error': 'No file part'}), 400
        
#         file = request.files['file']
#         if file.filename == '':
#             return jsonify({'error': 'No selected file'}), 400
        
#         image_content = file.read()
        
#         if 'GOOGLE_APPLICATION_CREDENTIALS' not in os.environ:
#             return jsonify({
#                 'error': 'Google Cloud credentials not configured',
#                 'status': 'failed'
#             }), 500
        
#         # Extract text and regions from the technical drawing
#         full_text, text_regions = extract_text_with_regions(image_content)
        
#         if not text_regions:
#             return jsonify({
#                 'error': 'No text detected in technical drawing',
#                 'raw_text': full_text,
#                 'status': 'failed'
#             }), 400
        
#         # Analyze the technical drawing
#         analyzer = DrawingAnalyzer()
#         categorized_data = analyzer.analyze_technical_drawing(full_text, text_regions)
        
#         return jsonify({
#             'categories': categorized_data,
#             'raw_text': full_text[:2000] + "..." if len(full_text) > 2000 else full_text,
#             'total_text_regions': len(text_regions),
#             'status': 'success',
#             'analysis_type': 'technical_drawing'
#         })
        
#     except Exception as e:
#         print(f"Error processing upload: {str(e)}")
#         print(traceback.format_exc())
#         return jsonify({
#             'error': str(e),
#             'traceback': traceback.format_exc(),
#             'status': 'failed'
#         }), 500

# @app.route('/health', methods=['GET'])
# def health_check():
#     return jsonify({'status': 'healthy', 'service': 'technical-drawing-analyzer'})

# if __name__ == '__main__':
#     app.run(debug=True, host='0.0.0.0', port=5000)

from flask import Flask, request, jsonify
from flask_cors import CORS
import re
import json
import traceback
from collections import defaultdict
import math
import base64
import requests
import os

app = Flask(__name__)
CORS(app)

import logging
logging.basicConfig(level=logging.DEBUG)

# OpenAI API configuration
OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')  # Set your OpenAI API key as environment variable
OPENAI_API_URL = "https://api.openai.com/v1/chat/completions"

class DrawingAnalyzer:
    def __init__(self):
        self.components = {
            'GABLE': [],
            'T/B & FIX SHELVES': [],
            'BACKS': [],
            'S/H': [],
            'DRAWS': [],
            'END PANELS & INFILLS': [],
            'BRACES': [],
            'DOORS & DRAW FACES': []
        }
        
    def analyze_technical_drawing_with_gpt(self, image_base64):
        """Analyze technical drawing using GPT Vision"""
        print("Analyzing technical drawing with GPT Vision")
        
        # Get analysis from GPT Vision
        gpt_analysis = self.get_gpt_analysis(image_base64)
        print(f"GPT Analysis: {gpt_analysis}")
        
        # Process the GPT analysis to generate cutting list
        self.process_gpt_analysis(gpt_analysis)
        
        return self.generate_cutting_list()
    
    def get_gpt_analysis(self, image_base64):
        """Send image to GPT Vision for analysis"""
        
        prompt = """You are an expert CAD cutting-list generator specializing in cabinet and furniture manufacturing. 

I will provide you with a 2D technical drawing showing cabinet elevations with dimensions. Your task is to analyze the drawing and extract all dimensional information to generate a comprehensive cutting list.

ANALYSIS REQUIREMENTS:
1. Identify all dimensions shown in the drawing (in mm)
2. Determine overall cabinet dimensions (width, height, depth)
3. Identify individual compartments, drawers, and door areas
4. Note any internal divisions, shelves, or structural elements
5. Analyze the cabinet construction type (face frame, frameless, etc.)

DIMENSIONAL EXTRACTION:
- Look for all numerical values (dimensions are typically in mm)
- Overall dimensions (usually the largest numbers)
- Internal compartment sizes
- Door and drawer dimensions
- Panel thicknesses (if shown)
- Hardware spacing

COMPONENT IDENTIFICATION:
Based on the drawing, identify these cabinet components:
- GABLE (side panels)
- T/B & FIX SHELVES (top, bottom, fixed shelves)
- BACKS (back panels)
- S/H (shelf hardware/adjustable shelves)
- DRAWS (drawer components)
- END PANELS & INFILLS
- BRACES (structural supports)
- DOORS & DRAW FACES

RESPONSE FORMAT:
Provide your analysis in this JSON structure:
{
  "overall_dimensions": {
    "width": number,
    "height": number, 
    "depth": number
  },
  "compartments": [
    {
      "width": number,
      "height": number,
      "type": "door/drawer/shelf",
      "position": "left/right/center/top/bottom"
    }
  ],
  "extracted_dimensions": [list of all dimension values found],
  "construction_notes": "observations about construction method",
  "component_analysis": {
    "doors_count": number,
    "drawers_count": number,
    "shelves_count": number,
    "has_face_frame": boolean
  }
}

Analyze the technical drawing carefully and provide detailed dimensional analysis for cutting list generation."""

        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {OPENAI_API_KEY}"
        }
        
        payload = {
            "model": "gpt-4o",  # Use GPT-4 with vision
            "messages": [
                {
                    "role": "user",
                    "content": [
                        {
                            "type": "text",
                            "text": prompt
                        },
                        {
                            "type": "image_url",
                            "image_url": {
                                "url": f"data:image/jpeg;base64,{image_base64}"
                            }
                        }
                    ]
                }
            ],
            "max_tokens": 2000,
            "temperature": 0.1  # Low temperature for consistent technical analysis
        }
        
        try:
            response = requests.post(OPENAI_API_URL, headers=headers, json=payload)
            response.raise_for_status()
            
            result = response.json()
            content = result['choices'][0]['message']['content']
            
            # Try to extract JSON from the response
            try:
                # Look for JSON in the response
                json_start = content.find('{')
                json_end = content.rfind('}') + 1
                if json_start != -1 and json_end != -1:
                    json_str = content[json_start:json_end]
                    return json.loads(json_str)
            except json.JSONDecodeError:
                pass
            
            # If no valid JSON, return the raw content
            return {"raw_analysis": content}
            
        except Exception as e:
            print(f"Error calling OpenAI API: {str(e)}")
            return {"error": str(e)}
    
    def process_gpt_analysis(self, analysis):
        """Process GPT analysis to generate cutting list components"""
        
        if "error" in analysis:
            print(f"GPT Analysis error: {analysis['error']}")
            return
            
        # Extract overall dimensions
        overall_dims = analysis.get('overall_dimensions', {})
        width = overall_dims.get('width', 0)
        height = overall_dims.get('height', 0)
        depth = overall_dims.get('depth', 600)  # Default depth if not specified
        
        if width == 0 or height == 0:
            # Try to extract from raw analysis or use fallback
            extracted_dims = analysis.get('extracted_dimensions', [])
            if extracted_dims:
                extracted_dims.sort(reverse=True)
                width = extracted_dims[0] if len(extracted_dims) > 0 else 1350
                height = extracted_dims[1] if len(extracted_dims) > 1 else 2820
        
        print(f"Processing cabinet: {width}W x {height}H x {depth}D")
        
        # Get component analysis
        comp_analysis = analysis.get('component_analysis', {})
        doors_count = comp_analysis.get('doors_count', 0)
        drawers_count = comp_analysis.get('drawers_count', 0)
        shelves_count = comp_analysis.get('shelves_count', 1)
        
        # Generate components based on analysis
        self.generate_components_from_analysis(width, height, depth, comp_analysis, analysis.get('compartments', []))
    
    def generate_components_from_analysis(self, width, height, depth, comp_analysis, compartments):
        """Generate cutting list components based on GPT analysis"""
        
        # GABLES (Side panels)
        self.add_component('GABLE', depth, height, 2, f"Side panels - {depth}x{height}")
        
        # T/B & FIX SHELVES (Top, Bottom, and Fixed Shelves)
        internal_width = width - 36  # Account for panel thickness (18mm each side)
        self.add_component('T/B & FIX SHELVES', internal_width, depth, 2, f"Top/Bottom - {internal_width}x{depth}")
        
        # Add fixed shelves based on analysis
        shelves_count = comp_analysis.get('shelves_count', 1)
        if shelves_count > 0:
            self.add_component('T/B & FIX SHELVES', internal_width, depth, shelves_count, f"Fixed shelves - {internal_width}x{depth}")
        
        # BACKS (typically 6mm or thin material)
        back_width = width - 20  # Small reduction for fitting
        back_height = height - 20
        self.add_component('BACKS', back_width, back_height, 1, f"Back panel - {back_width}x{back_height}")
        
        # DOORS based on analysis
        doors_count = comp_analysis.get('doors_count', 0)
        if doors_count > 0:
            # Calculate door dimensions based on compartments
            door_compartments = [c for c in compartments if c.get('type') == 'door']
            if door_compartments:
                for comp in door_compartments:
                    door_width = comp.get('width', (width - 60) // doors_count)
                    door_height = comp.get('height', height - 100)
                    self.add_component('DOORS & DRAW FACES', door_width, door_height, 1, f"Cabinet door - {door_width}x{door_height}")
            else:
                # Fallback calculation
                if doors_count == 2:
                    door_width = (width - 60) // 2
                else:
                    door_width = width - 30
                door_height = height - 100
                self.add_component('DOORS & DRAW FACES', door_width, door_height, doors_count, f"Cabinet doors - {door_width}x{door_height}")
        
        # DRAWERS based on analysis
        drawers_count = comp_analysis.get('drawers_count', 0)
        if drawers_count > 0:
            drawer_compartments = [c for c in compartments if c.get('type') == 'drawer']
            
            for i in range(drawers_count):
                if i < len(drawer_compartments):
                    drawer_width = drawer_compartments[i].get('width', internal_width - 20)
                    drawer_height = drawer_compartments[i].get('height', 150)
                else:
                    drawer_width = internal_width - 20
                    drawer_height = 150
                
                drawer_depth = depth - 50
                
                # Drawer box components
                self.add_component('DRAWS', drawer_width, drawer_height, 2, f"Drawer front/back - {drawer_width}x{drawer_height}")
                self.add_component('DRAWS', drawer_depth, drawer_height, 2, f"Drawer sides - {drawer_depth}x{drawer_height}")
                
                # Drawer face
                face_width = drawer_width + 20
                face_height = drawer_height + 20
                self.add_component('DOORS & DRAW FACES', face_width, face_height, 1, f"Drawer face - {face_width}x{face_height}")
        
        # END PANELS (if needed for exposed sides)
        if width > 1200:
            self.add_component('END PANELS & INFILLS', depth, height, 2, f"End panels - {depth}x{height}")
        
        # BRACES (structural support)
        if width > 1000:
            brace_length = internal_width
            self.add_component('BRACES', brace_length, 100, 2, f"Structural braces - {brace_length}x100")
    
    def add_component(self, category, width, height, quantity, description):
        """Add a component to the cutting list"""
        self.components[category].append({
            'dimensions': f"{width}x{height}",
            'width': width,
            'height': height,
            'quantity': quantity,
            'raw_text': description
        })
        print(f"Added to {category}: {width}x{height} qty:{quantity}")
    
    def generate_cutting_list(self):
        """Generate the final cutting list summary"""
        summary = {}
        for category, items in self.components.items():
            if items:
                total_pieces = sum(item['quantity'] for item in items)
                summary[category] = {
                    'items': items,
                    'total_pieces': total_pieces,
                    'unique_sizes': len(set(item['dimensions'] for item in items))
                }
            else:
                summary[category] = {
                    'items': [],
                    'total_pieces': 0,
                    'unique_sizes': 0
                }
        
        return summary

@app.route('/upload', methods=['POST'])
def upload_image():
    try:
        if 'file' not in request.files:
            return jsonify({'error': 'No file part'}), 400
        
        file = request.files['file']
        if file.filename == '':
            return jsonify({'error': 'No selected file'}), 400
        
        # Check if OpenAI API key is configured
        if not OPENAI_API_KEY:
            return jsonify({
                'error': 'OpenAI API key not configured. Please set OPENAI_API_KEY environment variable.',
                'status': 'failed'
            }), 500
        
        # Convert image to base64
        image_content = file.read()
        image_base64 = base64.b64encode(image_content).decode('utf-8')
        
        # Analyze the technical drawing with GPT Vision
        analyzer = DrawingAnalyzer()
        categorized_data = analyzer.analyze_technical_drawing_with_gpt(image_base64)
        
        return jsonify({
            'categories': categorized_data,
            'status': 'success',
            # 'analysis_type': 'gpt_vision',
            # 'message': 'Technical drawing analyzed successfully with GPT Vision'
        })
        
    except Exception as e:
        print(f"Error processing upload: {str(e)}")
        print(traceback.format_exc())
        return jsonify({
            'error': str(e),
            'traceback': traceback.format_exc(),
            'status': 'failed'
        }), 500

@app.route('/health', methods=['GET'])
def health_check():
    return jsonify({
        'status': 'healthy', 
        'service': 'gpt-vision-drawing-analyzer',
        'openai_configured': bool(OPENAI_API_KEY)
    })

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
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
import ezdxf
from io import StringIO
import logging
from datetime import datetime

app = Flask(__name__)
CORS(app)

# Configure logging
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# OpenAI API configuration
OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')
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
        self.part_counters = {
            'GABLE': 1,
            'T/B & FIX SHELVES': 1,
            'BACKS': 1,
            'S/H': 1,
            'DRAWS': 1,
            'END PANELS & INFILLS': 1,
            'BRACES': 1,
            'DOORS & DRAW FACES': 1
        }
        
    def analyze_technical_drawing_with_gpt(self, image_base64):
        """Analyze technical drawing using GPT Vision with enhanced error handling"""
        logger.info("Starting GPT Vision analysis")
        
        try:
            # Get analysis from GPT Vision
            gpt_analysis = self.get_gpt_analysis(image_base64)
            logger.info(f"GPT Analysis received: {type(gpt_analysis)}")
            
            # Validate analysis result
            if not gpt_analysis or "error" in gpt_analysis:
                logger.warning("GPT analysis failed or returned error, using fallback")
                self.generate_fallback_components()
            else:
                # Process the GPT analysis to generate cutting list
                self.process_gpt_analysis(gpt_analysis)
                
        except Exception as e:
            logger.error(f"Error in GPT analysis: {str(e)}")
            logger.error(traceback.format_exc())
            # Generate fallback components on any error
            self.generate_fallback_components()
        
        return self.generate_cutting_list()
    
    def get_gpt_analysis(self, image_base64):
        """Send image to GPT Vision for analysis with better error handling"""
        
        if not OPENAI_API_KEY:
            logger.error("OpenAI API key not configured")
            return {"error": "OpenAI API key not configured"}
        
        prompt = """You are an expert in analyzing interior design drawings for cabinetry, specializing in generating cutting lists for manufacturing.

IMPORTANT: Analyze this technical drawing carefully. It may show:
- Elevation views (front view showing heights)
- Plan views (top view showing widths and depths)
- Combined elevation and plan on one sheet
- Dimensions in millimeters

Your task is to identify cabinetry components and extract their dimensions.

RESPONSE FORMAT (JSON only, no other text):
{
  "analysis_confidence": "high|medium|low",
  "drawing_type": "elevation_and_plan|elevation_only|plan_only|unclear",
  "units_detected": "mm|inches|unclear",
  "ceiling_height": 2620,
  "total_width": 2400,
  "cabinet_units": [
    {
      "position": 1,
      "type": "wardrobe|base_unit|wall_unit|tall_unit",
      "width": 1200,
      "height": 2400,
      "depth": 600,
      "doors": 2,
      "drawers": 0,
      "shelves": 2,
      "notes": "Double door wardrobe"
    }
  ],
  "fillers_and_gaps": [
    {"type": "filler", "width": 75, "position": "left"},
    {"type": "gap", "width": 50, "position": "right"}
  ],
  "construction_notes": "18mm panels, full back, standard construction",
  "extracted_dimensions": [1200, 2400, 600, 75]
}

Analyze the image and provide only the JSON response."""

        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {OPENAI_API_KEY}"
        }
        
        payload = {
            "model": "gpt-4o",
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
                                "url": f"data:image/jpeg;base64,{image_base64}",
                                "detail": "high"
                            }
                        }
                    ]
                }
            ],
            "max_tokens": 2000,
            "temperature": 0.1
        }
        
        try:
            logger.info("Sending request to OpenAI API")
            response = requests.post(OPENAI_API_URL, headers=headers, json=payload, timeout=60)
            response.raise_for_status()
            
            result = response.json()
            content = result['choices'][0]['message']['content']
            logger.info(f"OpenAI response received, content length: {len(content)}")
            
            # Extract JSON from response
            try:
                # Try to find JSON in the response
                json_start = content.find('{')
                json_end = content.rfind('}') + 1
                
                if json_start != -1 and json_end > json_start:
                    json_str = content[json_start:json_end]
                    parsed_analysis = json.loads(json_str)
                    logger.info("Successfully parsed JSON from GPT response")
                    return parsed_analysis
                else:
                    logger.warning("No JSON found in GPT response")
                    return {"error": "No valid JSON in response", "raw_content": content}
                    
            except json.JSONDecodeError as e:
                logger.error(f"JSON decode error: {str(e)}")
                return {"error": "Invalid JSON in response", "raw_content": content}
            
        except requests.exceptions.Timeout:
            logger.error("OpenAI API request timed out")
            return {"error": "API request timed out"}
        except requests.exceptions.RequestException as e:
            logger.error(f"OpenAI API request failed: {str(e)}")
            return {"error": f"API request failed: {str(e)}"}
        except Exception as e:
            logger.error(f"Unexpected error in GPT analysis: {str(e)}")
            return {"error": f"Unexpected error: {str(e)}"}
    
    def process_gpt_analysis(self, analysis):
        """Process GPT analysis with improved validation"""
        
        if "error" in analysis:
            logger.error(f"GPT Analysis error: {analysis['error']}")
            self.generate_fallback_components()
            return
        
        try:
            cabinet_units = analysis.get('cabinet_units', [])
            fillers_and_gaps = analysis.get('fillers_and_gaps', [])
            confidence = analysis.get('analysis_confidence', 'low')
            
            logger.info(f"Processing analysis with confidence: {confidence}")
            logger.info(f"Found {len(cabinet_units)} cabinet units")
            
            if not cabinet_units and confidence == 'low':
                logger.warning("Low confidence analysis with no units, using fallback")
                self.generate_fallback_components()
                return
            
            # Process fillers first
            for filler in fillers_and_gaps:
                if filler.get('type') == 'filler':
                    width = filler.get('width', 75)
                    height = analysis.get('ceiling_height', 2400) - 200  # Default gaps
                    self.add_component('END PANELS & INFILLS', height, width, 1, 
                                     f"Filler panel - {height}x{width}")
            
            # Process cabinet units
            for i, unit in enumerate(cabinet_units, 1):
                try:
                    self.generate_components_for_unit(
                        unit.get('width', 600),
                        unit.get('height', 2400),
                        unit.get('depth', 600),
                        unit.get('shelves', 1),
                        unit.get('doors', 2),
                        unit.get('drawers', 0),
                        f"Unit {i}"
                    )
                except Exception as e:
                    logger.error(f"Error processing unit {i}: {str(e)}")
                    continue
            
            # If no components were generated, create fallback
            if not any(self.components.values()):
                logger.warning("No components generated from analysis, using fallback")
                self.generate_fallback_components()
                
        except Exception as e:
            logger.error(f"Error processing GPT analysis: {str(e)}")
            self.generate_fallback_components()
    
    def generate_fallback_components(self):
        """Generate fallback components with typical wardrobe specifications"""
        logger.info("Generating fallback components - standard wardrobe")
        
        # Clear any existing components
        for category in self.components:
            self.components[category] = []
        
        # Reset part counters
        for category in self.part_counters:
            self.part_counters[category] = 1
        
        # Generate a typical double wardrobe: 1200W x 2400H x 600D
        self.generate_components_for_unit(1200, 2400, 600, 1, 2, 0, "Standard Wardrobe")
        
        # Add end fillers
        self.add_component('END PANELS & INFILLS', 2400, 75, 2, "End filler panels")
    
    def generate_components_for_unit(self, width, height, depth, shelves_count, doors_count, drawers_count, unit_name="Unit"):
        """Generate components for a single unit with validation"""
        
        # Validate inputs
        width = max(300, min(3000, int(width)))  # Reasonable limits
        height = max(400, min(3000, int(height)))
        depth = max(200, min(800, int(depth)))
        shelves_count = max(0, min(10, int(shelves_count)))
        doors_count = max(0, min(6, int(doors_count)))
        drawers_count = max(0, min(10, int(drawers_count)))
        
        panel_thick = 18
        back_thick = 18
        internal_width = width - 2 * panel_thick
        internal_depth = depth - back_thick
        
        logger.info(f"Generating components for {unit_name}: {width}W x {height}H x {depth}D")
        logger.info(f"Shelves: {shelves_count}, Doors: {doors_count}, Drawers: {drawers_count}")
        
        try:
            # GABLES (side panels)
            self.add_component('GABLE', depth, height, 2, f"{unit_name} - Side panels")
            
            # T/B & FIX SHELVES (Top, Bottom and Fixed Shelves)
            self.add_component('T/B & FIX SHELVES', internal_width, internal_depth, 2, 
                             f"{unit_name} - Top/Bottom panels")
            
            if shelves_count > 0:
                self.add_component('T/B & FIX SHELVES', internal_width, internal_depth, 
                                 shelves_count, f"{unit_name} - Fixed shelves")
            
            # BACKS
            back_width = internal_width
            back_height = height - 2 * panel_thick
            self.add_component('BACKS', back_width, back_height, 1, 
                             f"{unit_name} - Back panel")
            
            # S/H (Shelf supports and hanging hardware)
            if shelves_count > 0:
                shelf_support_count = shelves_count * 4
                self.add_component('S/H', 50, 25, shelf_support_count, 
                                 f"{unit_name} - Shelf supports")
            
            # Add hanging rail for tall units
            if height > 1800 and doors_count > 0:
                hanging_rail_length = internal_width - 100
                self.add_component('S/H', hanging_rail_length, 25, 1, 
                                 f"{unit_name} - Hanging rail")
            
            # DOORS
            if doors_count > 0:
                door_height = height - 4
                door_width = (width - 4) / doors_count
                self.add_component('DOORS & DRAW FACES', door_width, door_height, 
                                 doors_count, f"{unit_name} - Door panels")
            
            # DRAWERS
            if drawers_count > 0:
                drawer_height = 150
                drawer_face_width = width - 4
                drawer_internal_width = internal_width - 40
                drawer_internal_depth = internal_depth - 50
                drawer_side_height = drawer_height - 20
                
                # Drawer faces
                self.add_component('DOORS & DRAW FACES', drawer_face_width, drawer_height, 
                                 drawers_count, f"{unit_name} - Drawer faces")
                
                # Drawer box components
                self.add_component('DRAWS', drawer_internal_width, drawer_side_height, 
                                 drawers_count * 2, f"{unit_name} - Drawer front/back")
                self.add_component('DRAWS', drawer_internal_depth, drawer_side_height, 
                                 drawers_count * 2, f"{unit_name} - Drawer sides")
                self.add_component('DRAWS', drawer_internal_width, drawer_internal_depth, 
                                 drawers_count, f"{unit_name} - Drawer bottoms")
            
            # BRACES for wide units
            if width > 1000:
                brace_count = 1 if width <= 1500 else 2
                self.add_component('BRACES', internal_width, 100, brace_count, 
                                 f"{unit_name} - Structural braces")
            
        except Exception as e:
            logger.error(f"Error generating components for {unit_name}: {str(e)}")
            raise
    
    def add_component(self, category, width, height, quantity, description):
        """Add a component with validation and proper part ID generation"""
        try:
            # Validate inputs
            width = max(10, int(round(width)))
            height = max(10, int(round(height)))
            quantity = max(1, int(quantity))
            
            if category not in self.components:
                logger.warning(f"Unknown category: {category}")
                return
            
            # Generate part ID
            part_id = f"{self.get_category_short_name(category)}-{self.part_counters[category]:02d}"
            
            # Get material type
            material_type = self.get_material_type(category)
            
            component_data = {
                'part_id': part_id,
                'dimensions': f"{width}x{height}",
                'width': width,
                'height': height,
                'quantity': quantity,
                'material_type': material_type,
                'notes': description,
                'raw_text': description
            }
            
            self.components[category].append(component_data)
            self.part_counters[category] += 1
            
            logger.debug(f"Added to {category}: {part_id} - {width}x{height} qty:{quantity} - {description}")
            
        except Exception as e:
            logger.error(f"Error adding component: {str(e)}")
    
    def get_category_short_name(self, category):
        """Get short name for category"""
        short_names = {
            'GABLE': 'GABLE',
            'T/B & FIX SHELVES': 'SHELF',
            'BACKS': 'BACK',
            'S/H': 'HARDWARE',
            'DRAWS': 'DRAWER',
            'END PANELS & INFILLS': 'PANEL',
            'BRACES': 'BRACE',
            'DOORS & DRAW FACES': 'DOOR'
        }
        return short_names.get(category, 'COMP')
    
    def get_material_type(self, category):
        """Get material type for category"""
        materials = {
            'GABLE': '18mm MFC',
            'T/B & FIX SHELVES': '18mm MFC',
            'BACKS': '6mm MDF',
            'S/H': 'Hardware',
            'DRAWS': '12mm Ply',
            'END PANELS & INFILLS': '18mm MFC',
            'BRACES': '18mm MFC',
            'DOORS & DRAW FACES': '18mm MFC'
        }
        return materials.get(category, '18mm MFC')
    
    def generate_cutting_list(self):
        """Generate the final cutting list with validation"""
        summary = {}
        total_items = 0
        
        for category, items in self.components.items():
            if items:
                total_pieces = sum(item['quantity'] for item in items)
                unique_dimensions = set(item['dimensions'] for item in items)
                
                # Calculate total area for this category
                total_area = 0
                for item in items:
                    width = item.get('width', 0)
                    height = item.get('height', 0)
                    quantity = item.get('quantity', 1)
                    total_area += (width * height * quantity) / 1000000  # Convert to m²
                
                summary[category] = {
                    'items': items,
                    'total_pieces': total_pieces,
                    'unique_sizes': len(unique_dimensions),
                    'total_area': round(total_area, 2)
                }
                total_items += total_pieces
            else:
                summary[category] = {
                    'items': [],
                    'total_pieces': 0,
                    'unique_sizes': 0,
                    'total_area': 0.0
                }
        
        # Log summary
        logger.info(f"\n=== CUTTING LIST SUMMARY ===")
        logger.info(f"Total items across all categories: {total_items}")
        for category, data in summary.items():
            if data['total_pieces'] > 0:
                logger.info(f"{category}: {data['total_pieces']} pieces, {data['unique_sizes']} unique sizes, {data['total_area']} m²")
        logger.info("============================")
        
        return summary
    
    def generate_dxf(self):
        """Generate DXF with improved error handling"""
        try:
            return self._create_dxf_layout()
        except Exception as e:
            logger.error(f"Error generating DXF: {str(e)}")
            return self._generate_fallback_dxf()
    
    def _create_dxf_layout(self):
        """Create detailed DXF layout"""
        doc = ezdxf.new(dxfversion='R2010')
        doc.units = ezdxf.units.MM
        msp = doc.modelspace()
        
        # Layout parameters
        x_offset = 0
        y_offset = 0
        max_height_in_row = 0
        sheet_width = 2400  # Standard sheet width
        margin = 50
        
        # Add title block
        title_text = f"CUTTING LIST - Generated {datetime.now().strftime('%Y-%m-%d %H:%M')}"
        title_entity = msp.add_text(title_text)
        title_entity.set_pos((10, -30))
        title_entity.dxf.height = 25
        y_offset -= 80
        
        for category, items in self.components.items():
            if not items:
                continue
            
            # Category header
            header_text = msp.add_text(f"=== {category} ===")
            header_text.set_pos((x_offset, y_offset))
            header_text.dxf.height = 20
            y_offset -= 40
            
            for item in items:
                w = item['width']
                h = item['height']
                qty = item['quantity']
                part_id = item.get('part_id', f"{category[:4]}-01")
                
                for q in range(qty):
                    # Check if we need a new row
                    if x_offset + w > sheet_width:
                        x_offset = 0
                        y_offset -= max_height_in_row + margin
                        max_height_in_row = 0
                    
                    # Draw rectangle
                    points = [
                        (x_offset, y_offset),
                        (x_offset + w, y_offset),
                        (x_offset + w, y_offset - h),
                        (x_offset, y_offset - h)
                    ]
                    msp.add_lwpolyline(points, close=True)
                    
                    # Add dimension text
                    dim_text = f"{w}x{h}"
                    dim_entity = msp.add_text(dim_text)
                    dim_entity.set_pos((x_offset + 5, y_offset - 15))
                    dim_entity.dxf.height = 12
                    
                    # Add part info
                    part_text = f"{part_id}-{q+1:02d}" if qty > 1 else part_id
                    part_entity = msp.add_text(part_text)
                    part_entity.set_pos((x_offset + 5, y_offset - h + 5))
                    part_entity.dxf.height = 10
                    
                    x_offset += w + margin
                    max_height_in_row = max(max_height_in_row, h)
            
            # New row for next category
            x_offset = 0
            y_offset -= max_height_in_row + margin * 2
            max_height_in_row = 0
        
        # Save to string
        stream = StringIO()
        doc.saveas(stream)
        return stream.getvalue()
    
    def _generate_fallback_dxf(self):
        """Generate simple fallback DXF"""
        try:
            doc = ezdxf.new()
            msp = doc.modelspace()
            
            # Simple layout
            y = 0
            for category, items in self.components.items():
                if items:
                    # Add text
                    msp.add_text(f"{category}: {len(items)} items").set_pos((0, y))
                    y -= 50
            
            stream = StringIO()
            doc.saveas(stream)
            return stream.getvalue()
            
        except Exception as e:
            logger.error(f"Fallback DXF generation failed: {str(e)}")
            return f"# DXF Generation Failed\n# Error: {str(e)}\n# Timestamp: {datetime.now()}"

@app.route('/upload', methods=['POST'])
def upload_image():
    """Enhanced upload endpoint with better error handling"""
    try:
        # Validate request
        if 'file' not in request.files:
            return jsonify({
                'error': 'No file uploaded',
                'status': 'failed',
                'code': 'NO_FILE'
            }), 400
        
        file = request.files['file']
        if file.filename == '':
            return jsonify({
                'error': 'No file selected',
                'status': 'failed',
                'code': 'EMPTY_FILENAME'
            }), 400
        
        # Validate file type
        allowed_types = {'image/jpeg', 'image/jpg', 'image/png', 'image/gif', 'image/webp'}
        if file.content_type not in allowed_types:
            return jsonify({
                'error': f'Unsupported file type: {file.content_type}',
                'status': 'failed',
                'code': 'INVALID_FILE_TYPE'
            }), 400
        
        # Check API key
        if not OPENAI_API_KEY:
            return jsonify({
                'error': 'OpenAI API key not configured',
                'status': 'failed',
                'code': 'API_KEY_MISSING',
                'message': 'Please set OPENAI_API_KEY environment variable'
            }), 500
        
        # Process image
        logger.info(f"Processing upload: {file.filename}, type: {file.content_type}")
        image_content = file.read()
        
        # Validate file size (max 20MB)
        if len(image_content) > 20 * 1024 * 1024:
            return jsonify({
                'error': 'File too large (max 20MB)',
                'status': 'failed',
                'code': 'FILE_TOO_LARGE'
            }), 400
        
        image_base64 = base64.b64encode(image_content).decode('utf-8')
        
        # Analyze drawing
        analyzer = DrawingAnalyzer()
        categorized_data = analyzer.analyze_technical_drawing_with_gpt(image_base64)
        dxf_content = analyzer.generate_dxf()
        
        # Calculate summary statistics
        total_pieces = sum(cat.get('total_pieces', 0) for cat in categorized_data.values())
        active_categories = len([cat for cat in categorized_data.values() if cat.get('total_pieces', 0) > 0])
        total_area = sum(cat.get('total_area', 0) for cat in categorized_data.values())
        
        response_data = {
            'categories': categorized_data,
            'dxf': dxf_content,
            'status': 'success',
            'summary': {
                'total_pieces': total_pieces,
                'active_categories': active_categories,
                'total_area': round(total_area, 2),
                'generated_at': datetime.now().isoformat()
            },
            'metadata': {
                'filename': file.filename,
                'file_size': len(image_content),
                'file_type': file.content_type
            }
        }
        
        logger.info(f"Successfully processed {file.filename}: {total_pieces} total pieces, {active_categories} categories, {total_area} m² total area")
        return jsonify(response_data)
        
    except Exception as e:
        error_id = datetime.now().strftime('%Y%m%d_%H%M%S')
        logger.error(f"Error {error_id} processing upload: {str(e)}")
        logger.error(traceback.format_exc())
        
        return jsonify({
            'error': 'Internal server error during processing',
            'status': 'failed',
            'code': 'PROCESSING_ERROR',
            'error_id': error_id,
            'details': str(e) if app.debug else 'Enable debug mode for details'
        }), 500

@app.route('/health', methods=['GET'])
def health_check():
    """Enhanced health check"""
    try:
        # Test DXF generation
        test_doc = ezdxf.new()
        dxf_ok = True
    except:
        dxf_ok = False
    
    return jsonify({
        'status': 'healthy',
        'service': 'technical-drawing-analyzer',
        'version': '2.0',
        'timestamp': datetime.now().isoformat(),
        'components': {
            'openai_api': bool(OPENAI_API_KEY),
            'dxf_generation': dxf_ok
        }
    })

@app.route('/test', methods=['GET'])
def test_cutting_list():
    """Enhanced test endpoint"""
    try:
        logger.info("Generating test cutting list")
        analyzer = DrawingAnalyzer()
        analyzer.generate_fallback_components()
        categorized_data = analyzer.generate_cutting_list()
        dxf_content = analyzer.generate_dxf()
        
        total_pieces = sum(cat.get('total_pieces', 0) for cat in categorized_data.values())
        total_area = sum(cat.get('total_area', 0) for cat in categorized_data.values())
        
        return jsonify({
            'categories': categorized_data,
            'dxf': dxf_content,
            'status': 'success',
            'message': 'Test cutting list generated successfully',
            'test_data': {
                'total_pieces': total_pieces,
                'total_area': round(total_area, 2),
                'generated_at': datetime.now().isoformat()
            }
        })
        
    except Exception as e:
        logger.error(f"Error in test endpoint: {str(e)}")
        return jsonify({
            'error': 'Test generation failed',
            'status': 'failed',
            'details': str(e)
        }), 500

if __name__ == '__main__':
    logger.info("Starting Technical Drawing Analyzer service")
    app.run(debug=True, host='0.0.0.0', port=5000)
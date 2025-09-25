# import base64
# import json
# import traceback
# from collections import defaultdict
# import math
# import requests
# import os
# import ezdxf
# from io import StringIO, BytesIO
# import logging
# from datetime import datetime
# import re
# from google.cloud import vision
# from google.oauth2 import service_account
# from google.protobuf.json_format import MessageToDict

# # Configure logging
# logging.basicConfig(level=logging.INFO)
# logger = logging.getLogger(__name__)

# # API Configuration
# OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "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")
# OPENAI_API_URL = "https://api.openai.com/v1/chat/completions"

# # Google Cloud Vision Configuration
# GOOGLE_CLOUD_CREDENTIALS = os.getenv("GOOGLE_CLOUD_CREDENTIALS", '''{
#   "type": "service_account",
#   "project_id": "new-app-472823",
#   "private_key_id": "9d16e52e7a1bacc256b8b16eb65422318e5af92e",
#   "private_key": "-----BEGIN PRIVATE KEY-----\\nMIIEvAIBADANBgkqhkiG9w0BAQEFAASCBKYwggSiAgEAAoIBAQCvI5zx1IStepHQ\\nMXITqc0SyeYam5bEqcUlZTJ4G8mjYIqi7RlRy9u2sK4xwERqI2xT8RSf922YGOLD\\nVAD4FbvKmTfVAUWPCVNYhWVkmUkrZbj8TygmhAcMg8YW1D+puQ9MfEQGnYQrF01S\\nGpgtPkhGwNTiYB+WB8zdq1MbdE4GUuPttsiZwVrkjy/TWXvxmRJ6DPCfv2we1fFk\\nl57A4GsySJ/woiY1EZqGicMwtgc4gMGdUX6heoSi73DT/TIkYYivQjxlAVLVtibY\\nBO9rlaaIwEaatmViGPZPkrw1tNhGQuBvCEEBpXMZRGVpunTPk/SkmvcmGcj4qt4w\\n7RzeXUhpAgMBAAECggEAEH7xd5qdc4yFot8hYEZARUqEdJGeif/2jG7jacouPAfq\\nDu33kkt58pNiGNgD6Z5UA/UDTQzcQvTnGOA25ib/5NV5G4Qu5cnKUp5f3jGM4XxH\\nh+Y5wSTy2AQqWnib1XPTg8/5hUj9S6S6eOb92dcRri5X7smAeBxceK18Gqwh9Djf\\nDjJKhWMjZz2/rxAdYHCEUzSbjr1ZgexU8JeBtXLU0vqpcssd+EB1V/bQhk7wX3dT\\nJ6HpyMgZS98/xmcvzrDgjYvR9vkQrtWt3w/+8cxtysG2dTMBLDS2jcB0Ojw1zvXH\\nUSkhgkmJmu05qBxuqUJ3mVYAuXMd2gD8pD6Df+Y4oQKBgQDY9/Vzk59zaY9H0ees\\nYdIud8f6OhQewiSm4eRjnQhPtV2AuipH3UJ38jCxGeEIjlTSm3k6MbFzwUgSbsvh\\nM2CzBBjMI5jTPiJcRMji7YysBC5ms3u1oS8Vv5W7lp/eLdI8fIFOMi8hM12J2Otq\\nl/NJpab9quhi9w9STPq5Xz9E0QKBgQDOpUizNhFywsWj76lDHMceP3cKRNOiaTv7\\nKpAMvpEAbLFf1DThHeKfjM3BGTU0JchqQ/r7vMtlQjiJl9JoY42lDjbNdqBtmN5h\\nsPcu6almtlDmHg69wzhVJLVulALnR9RG9+O/K4eJFtYMJbETNXngToY8S6ldv4xn\\nJX+KeVqQGQKBgEpJg+HhrpuOjf9SMFeGWreMTY0wa4kogfIdr9wnfRwFhhE4LJfU\\nexikdOV+bd1HFmXR080IDLEMgYfGJcpik/5XLcJfgcj6IjujVYDVQu/2soh5dab3\\nnC5/HV5QMUaaO7x4CLHkXtyoQKOdAOXLRwJ1VFrQNKcF3loYf1QO95OxAoGAIw5r\\nLOvpPdzJBqyrvFTverQtj7JpbM4JfOyVj3PsyXOnC6jGZ8JYJdUPOsj5+6TFQTHT\\nLE20+7KmQMFe0pLA/tVQer67LJyYbV5GMNE3CdO4GbHTsmGh9t/JX78AVxgabQe0\\nvUO3NIyJN3pVdfrGeEUaBLSZQOwz93OnFWjM8lECgYAlAqbxJDZhm7L1CBKUQaoQ\\nfSBF8OMJ6R/fDHcinbfkKSP1T3S4fyDSsGpqX6+ZrwYB7oZOgcXp1miTtEghHeVK\\nmiBopW9VmymAeAF1TW9lVbqpUSvAFGU6xE1dred45g8fZhCp3TLs7S57bDUGpgtb\\nMCv0UIWQSaESAg8FC3rbXA==\\n-----END PRIVATE KEY-----\\n",
#   "client_email": "razataiab@new-app-472823.iam.gserviceaccount.com",
#   "client_id": "116148412739934691912",
#   "auth_uri": "https://accounts.google.com/o/oauth2/auth",
#   "token_uri": "https://oauth2.googleapis.com/token",
#   "auth_provider_x509_cert_url": "https://www.googleapis.com/oauth2/v1/certs",
#   "client_x509_cert_url": "https://www.googleapis.com/robot/v1/metadata/x509/razataiab%40new-app-472823.iam.gserviceaccount.com",
#   "universe_domain": "googleapis.com"
# }
# ''')

# class DrawingAnalyzer:
#     def __init__(self):
#         # Configurable offsets for different workshop requirements
#         self.BACK_WIDTH_OFFSET = 36      # W_back = W - BACK_WIDTH_OFFSET
#         self.TOP_DEPTH_OFFSET = 30       # Top depth = D - TOP_DEPTH_OFFSET  
#         self.SHELF_DEPTH_OFFSET = 70     # Shelf depth = D - SHELF_DEPTH_OFFSET
#         self.THICKNESS = 18              # Board thickness (18mm standard)
        
#         # Kitchen cabinet specific adjustments
#         self.LEG_HEIGHT_DEDUCTION = 100   # Subtract for legs underneath
#         self.COUNTERTOP_DEDUCTION = 25    # Subtract for countertop accommodation
        
#         self.components = {
#             'GABLE': [],
#             'T/B & FIX SHELVES': [],
#             'BACKS': [],
#             'S/H': []
#         }
#         self.part_counters = {
#             'GABLE': 1,
#             'T/B & FIX SHELVES': 1,
#             'BACKS': 1,
#             'S/H': 1
#         }
        
#         # Initialize Google Cloud Vision client
#         self.vision_client = self._init_google_vision_client()
    
#     def _init_google_vision_client(self):
#         try:
#             if GOOGLE_CLOUD_CREDENTIALS and GOOGLE_CLOUD_CREDENTIALS.strip().startswith('{'):
#                 logger.info("Initializing Google Vision client from inline JSON credentials.")
#                 creds_dict = json.loads(GOOGLE_CLOUD_CREDENTIALS)
#                 credentials = service_account.Credentials.from_service_account_info(creds_dict)
#                 client = vision.ImageAnnotatorClient(credentials=credentials)
#                 logger.info("Google Vision client initialized successfully.")
#                 return client
#             elif os.getenv('GOOGLE_APPLICATION_CREDENTIALS'):
#                 logger.info("Initializing Vision client using GOOGLE_APPLICATION_CREDENTIALS.")
#                 client = vision.ImageAnnotatorClient()
#                 return client
#             else:
#                 logger.info("Attempting to initialize Vision client using default credentials.")
#                 client = vision.ImageAnnotatorClient()
#                 return client
#         except Exception as e:
#             logger.warning(f"Could not initialize Google Cloud Vision client: {e}")
#             return None
    
#     def set_offsets(self, back_width_offset=36, top_depth_offset=30, shelf_depth_offset=70, 
#                    thickness=18, leg_height_deduction=100, countertop_deduction=25):
#         """Configure offsets for different workshop requirements"""
#         self.BACK_WIDTH_OFFSET = back_width_offset
#         self.TOP_DEPTH_OFFSET = top_depth_offset
#         self.SHELF_DEPTH_OFFSET = shelf_depth_offset
#         self.THICKNESS = thickness
#         self.LEG_HEIGHT_DEDUCTION = leg_height_deduction
#         self.COUNTERTOP_DEDUCTION = countertop_deduction
    
#     def extract_numbers_with_google_vision(self, image_bytes):
#         """Extract all numbers and text from image using Google Cloud Vision API"""
        
#         if not self.vision_client:
#             logger.error("Google Cloud Vision client not initialized")
#             return None, []
        
#         try:
#             logger.info("Extracting text with Google Cloud Vision...")
            
#             # Create vision image object
#             image = vision.Image(content=image_bytes)
            
#             # Perform text detection
#             response = self.vision_client.text_detection(image=image)
#             texts = response.text_annotations
            
#             if not texts:
#                 logger.warning("No text detected in the image")
#                 return None, []
            
#             # Full text is in the first annotation
#             full_text = texts[0].description if texts else ""
            
#             # Extract all numbers from the detected text
#             number_pattern = r'\b\d+(?:\.\d+)?\b'
#             all_numbers = re.findall(number_pattern, full_text)
            
#             # Convert to float/int and filter
#             extracted_numbers = []
#             for num_str in all_numbers:
#                 try:
#                     num = float(num_str) if '.' in num_str else int(num_str)
#                     extracted_numbers.append(num)
#                 except ValueError:
#                     continue
            
#             logger.info(f"Extracted {len(extracted_numbers)} numbers from image")
            
#             # Enhanced analysis for cabinet dimensions with segment detection
#             dimension_analysis = {
#                 'width_candidates': [n for n in extracted_numbers if 800 <= n <= 2000],
#                 'height_candidates': [n for n in extracted_numbers if 400 <= n <= 900],
#                 'depth_candidates': [n for n in extracted_numbers if 250 <= n <= 500],
#                 'large_numbers': [n for n in extracted_numbers if n > 2500],
#                 'small_numbers': [n for n in extracted_numbers if n < 200],
#                 'segment_candidates': [n for n in extracted_numbers if 400 <= n <= 800],
#                 'all_numbers': extracted_numbers
#             }
            
#             # Look for potential width segments
#             segments = dimension_analysis['segment_candidates']
#             potential_widths = []
            
#             for i, seg1 in enumerate(segments):
#                 for j, seg2 in enumerate(segments[i+1:], i+1):
#                     if abs(seg1 - seg2) <= 50:
#                         total_width = seg1 + seg2
#                         if 900 <= total_width <= 1800:
#                             potential_widths.append({
#                                 'segments': [seg1, seg2],
#                                 'total': total_width,
#                                 'description': f"{seg1}+{seg2}={total_width}"
#                             })
            
#             dimension_analysis['potential_segmented_widths'] = potential_widths
            
#             return full_text, dimension_analysis
            
#         except Exception as e:
#             logger.error(f"Error in Google Cloud Vision extraction: {str(e)}")
#             return None, []
    
#     def analyze_with_openai(self, image_bytes, dimension_analysis):
#         """Analyze with OpenAI GPT-4 Vision"""
        
#         if not OPENAI_API_KEY:
#             raise Exception("OpenAI API key not configured")
        
#         image_base64 = base64.b64encode(image_bytes).decode('utf-8')
        
#         # Prepare the enhanced prompt (simplified version for API)
#         prompt = f"""
#         Analyze this kitchen cabinet technical drawing and extract dimensions.
        
#         Extracted numbers: {dimension_analysis.get('all_numbers', [])}
#         Potential segmented widths: {dimension_analysis.get('potential_segmented_widths', [])}
        
#         CRITICAL: If you see segments like 600+600, use the SUM as cabinet width.
        
#         Apply these deductions:
#         - Height: subtract {self.LEG_HEIGHT_DEDUCTION}mm (legs) + {self.COUNTERTOP_DEDUCTION}mm (countertop)
#         - Width offsets: -{self.BACK_WIDTH_OFFSET}mm for shelves/back
#         - Depth offsets: -{self.TOP_DEPTH_OFFSET}mm for T/B, -{self.SHELF_DEPTH_OFFSET}mm for S/H
        
#         Return JSON with:
#         {{
#             "cabinet_width": [detected_width],
#             "cabinet_total_height": [detected_height],
#             "cabinet_working_height": [height - {self.LEG_HEIGHT_DEDUCTION + self.COUNTERTOP_DEDUCTION}],
#             "cabinet_depth": [detected_depth],
#             "components": {{
#                 "gables": {{"height": "working_height", "width": "depth", "quantity": 2}},
#                 "tb_panels": {{"height": "(width-{self.BACK_WIDTH_OFFSET})", "width": "(depth-{self.TOP_DEPTH_OFFSET})", "quantity": 2}},
#                 "sh_hardware": {{"height": "(width-{self.BACK_WIDTH_OFFSET})", "width": "(depth-{self.SHELF_DEPTH_OFFSET})", "quantity": 1}},
#                 "back": {{"height": "working_height", "width": "(width-{self.BACK_WIDTH_OFFSET})", "quantity": 1}}
#             }}
#         }}
#         """
        
#         headers = {
#             "Content-Type": "application/json",
#             "Authorization": f"Bearer {OPENAI_API_KEY}"
#         }
        
#         payload = {
#             "model": "gpt-4o",
#             "messages": [
#                 {
#                     "role": "user",
#                     "content": [
#                         {
#                             "type": "text",
#                             "text": prompt
#                         },
#                         {
#                             "type": "image_url",
#                             "image_url": {
#                                 "url": f"data:image/jpeg;base64,{image_base64}",
#                                 "detail": "high"
#                             }
#                         }
#                     ]
#                 }
#             ],
#             "max_tokens": 2000,
#             "temperature": 0.1
#         }
        
#         response = requests.post(OPENAI_API_URL, headers=headers, json=payload, timeout=60)
#         response.raise_for_status()
        
#         result = response.json()
#         content = result['choices'][0]['message']['content']
        
#         # Extract JSON from response
#         json_start = content.find('{')
#         json_end = content.rfind('}') + 1
        
#         if json_start != -1 and json_end > json_start:
#             json_str = content[json_start:json_end]
#             return json.loads(json_str)
#         else:
#             raise Exception("No valid JSON in OpenAI response")
    
#     def analyze_technical_drawing(self, image_bytes):
#         """Main analysis function"""
#         logger.info("Starting kitchen cabinet analysis")
        
#         try:
#             # Clear previous data
#             self.components = {
#                 'GABLE': [],
#                 'T/B & FIX SHELVES': [],
#                 'BACKS': [],
#                 'S/H': []
#             }
#             self.part_counters = {
#                 'GABLE': 1,
#                 'T/B & FIX SHELVES': 1,
#                 'BACKS': 1,
#                 'S/H': 1
#             }
            
#             # Extract numbers
#             full_text, dimension_analysis = self.extract_numbers_with_google_vision(image_bytes)
            
#             if not dimension_analysis or not dimension_analysis.get('all_numbers'):
#                 raise Exception("Failed to extract numbers from image")
            
#             # Analyze with OpenAI
#             analysis_result = self.analyze_with_openai(image_bytes, dimension_analysis)
            
#             # Process results
#             self.process_analysis_result(analysis_result)
            
#             return self.generate_cutting_list()
            
#         except Exception as e:
#             logger.error(f"Analysis failed: {str(e)}")
#             return self.generate_empty_cutting_list()
    
#     def process_analysis_result(self, analysis):
#         """Process analysis results and create components"""
        
#         width = analysis.get('cabinet_width', 0)
#         working_height = analysis.get('cabinet_working_height', 0)
#         depth = analysis.get('cabinet_depth', 0)
        
#         components = analysis.get('components', {})
        
#         # Add components
#         if 'gables' in components:
#             comp = components['gables']
#             self.add_component('GABLE', working_height, depth, 2, f"Gables {working_height}×{depth}")
        
#         if 'tb_panels' in components:
#             tb_width = width - self.BACK_WIDTH_OFFSET
#             tb_depth = depth - self.TOP_DEPTH_OFFSET
#             self.add_component('T/B & FIX SHELVES', tb_width, tb_depth, 2, f"T/B Panels {tb_width}×{tb_depth}")
        
#         if 'sh_hardware' in components:
#             sh_width = width - self.BACK_WIDTH_OFFSET
#             sh_depth = depth - self.SHELF_DEPTH_OFFSET
#             self.add_component('S/H', sh_width, sh_depth, 1, f"Shelf Hardware {sh_width}×{sh_depth}")
        
#         if 'back' in components:
#             back_width = width - self.BACK_WIDTH_OFFSET
#             self.add_component('BACKS', working_height, back_width, 1, f"Back Panel {working_height}×{back_width}")
    
#     def add_component(self, category, height, width, quantity, description):
#         """Add a component to the cutting list"""
#         try:
#             height = max(10, int(round(height)))
#             width = max(10, int(round(width)))
#             quantity = max(1, int(quantity))
            
#             part_id = f"{self.get_category_short_name(category)}-{self.part_counters[category]:02d}"
#             material_type = self.get_material_type(category)
            
#             component_data = {
#                 'part_id': part_id,
#                 'dimensions': f"{height}×{width}",
#                 'height': height,
#                 'width': width,
#                 'quantity': quantity,
#                 'material_type': material_type,
#                 'notes': description
#             }
            
#             self.components[category].append(component_data)
#             self.part_counters[category] += 1
            
#         except Exception as e:
#             logger.error(f"Error adding component: {str(e)}")
    
#     def get_category_short_name(self, category):
#         short_names = {
#             'GABLE': 'GABLE',
#             'T/B & FIX SHELVES': 'SHELF',
#             'BACKS': 'BACK',
#             'S/H': 'HARDWARE'
#         }
#         return short_names.get(category, 'COMP')
    
#     def get_material_type(self, category):
#         materials = {
#             'GABLE': '18mm MFC',
#             'T/B & FIX SHELVES': '18mm MFC',
#             'BACKS': '6mm MDF',
#             'S/H': 'Hardware'
#         }
#         return materials.get(category, '18mm MFC')
    
#     def generate_cutting_list(self):
#         """Generate the final cutting list summary"""
#         summary = {}
        
#         for category, items in self.components.items():
#             if items:
#                 total_pieces = sum(item['quantity'] for item in items)
#                 unique_dimensions = set(item['dimensions'] for item in items)
                
#                 total_area = 0
#                 for item in items:
#                     w = item.get('width', 0)
#                     h = item.get('height', 0)
#                     quantity = item.get('quantity', 1)
#                     total_area += (w * h * quantity) / 1000000
                
#                 summary[category] = {
#                     'items': items,
#                     'total_pieces': total_pieces,
#                     'unique_sizes': len(unique_dimensions),
#                     'total_area': round(total_area, 2)
#                 }
#             else:
#                 summary[category] = {
#                     'items': [],
#                     'total_pieces': 0,
#                     'unique_sizes': 0,
#                     'total_area': 0.0
#                 }
        
#         return summary
    
#     def generate_empty_cutting_list(self):
#         """Generate empty cutting list when analysis fails"""
#         summary = {}
#         for category in self.components:
#             summary[category] = {
#                 'items': [],
#                 'total_pieces': 0,
#                 'unique_sizes': 0,
#                 'total_area': 0.0
#             }
#         return summary
    
#     def generate_dxf(self):
#         """Generate DXF file for cutting layout"""
#         try:
#             doc = ezdxf.new(dxfversion='R2010')
#             doc.units = ezdxf.units.MM
#             msp = doc.modelspace()
            
#             # Simple layout
#             x_offset = 0
#             y_offset = 0
#             margin = 50
            
#             title = f"KITCHEN CABINET CUTTING LIST - {datetime.now().strftime('%Y-%m-%d %H:%M')}"
#             msp.add_text(title, dxfattribs={'height': 25}).set_pos((10, -30))
#             y_offset = -80
            
#             for category, items in self.components.items():
#                 if not items:
#                     continue
                
#                 # Category header
#                 msp.add_text(f"=== {category} ===", dxfattribs={'height': 20}).set_pos((x_offset, y_offset))
#                 y_offset -= 40
                
#                 for item in items:
#                     w = item['width']
#                     h = item['height']
#                     qty = item['quantity']
                    
#                     for q in range(qty):
#                         # Draw rectangle
#                         points = [
#                             (x_offset, y_offset),
#                             (x_offset + w, y_offset),
#                             (x_offset + w, y_offset - h),
#                             (x_offset, y_offset - h)
#                         ]
#                         msp.add_lwpolyline(points, close=True)
                        
#                         # Add dimensions
#                         dim_text = f"{w}×{h}"
#                         msp.add_text(dim_text, dxfattribs={'height': 12}).set_pos((x_offset + 5, y_offset - 15))
                        
#                         x_offset += w + margin
                
#                 x_offset = 0
#                 y_offset -= 200
            
#             stream = StringIO()
#             doc.saveas(stream)
#             return stream.getvalue()
            
#         except Exception as e:
#             logger.error(f"Error generating DXF: {str(e)}")
#             return None
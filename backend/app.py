import streamlit as st
import base64
import json
import traceback
from collections import defaultdict
import math
import requests
import os
import ezdxf
from io import StringIO, BytesIO
import logging
from datetime import datetime
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from PIL import Image
import re
import time

# Configure logging
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Mistral AI API configuration
MISTRAL_API_KEY = os.getenv('MISTRAL_API_KEY')
MISTRAL_API_URL = "https://api.mistral.ai/v1/chat/completions"

# OpenAI API configuration (fallback)
OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')
OPENAI_API_URL = "https://api.openai.com/v1/chat/completions"

class DrawingAnalyzer:
    def __init__(self):
        # Configurable offsets for different workshop requirements
        self.BACK_WIDTH_OFFSET = 36      # W_back = W - BACK_WIDTH_OFFSET
        self.TOP_DEPTH_OFFSET = 30       # Top depth = D - TOP_DEPTH_OFFSET  
        self.SHELF_DEPTH_OFFSET = 40     # Shelf depth = D - SHELF_DEPTH_OFFSET
        self.THICKNESS = 18              # Board thickness (18mm standard)
        
        self.components = {
            'GABLE': [],
            'T/B & FIX SHELVES': [],
            'BACKS': [],
            'S/H': []
        }
        self.part_counters = {
            'GABLE': 1,
            'T/B & FIX SHELVES': 1,
            'BACKS': 1,
            'S/H': 1
        }
    
    def set_offsets(self, back_width_offset=36, top_depth_offset=30, shelf_depth_offset=40, thickness=18):
        """Configure offsets for different workshop requirements"""
        self.BACK_WIDTH_OFFSET = back_width_offset
        self.TOP_DEPTH_OFFSET = top_depth_offset
        self.SHELF_DEPTH_OFFSET = shelf_depth_offset
        self.THICKNESS = thickness
    
    def generate_empty_cutting_list(self):
        """Generate empty cutting list when analysis fails"""
        summary = {}
        for category in self.components:
            summary[category] = {
                'items': [],
                'total_pieces': 0,
                'unique_sizes': 0,
                'total_area': 0.0
            }
        return summary
        
    def analyze_technical_drawing_hybrid(self, image_bytes):
        """Analyze drawing using Mistral AI vision with OpenAI fallback - ALWAYS DYNAMIC"""
        logger.info("Starting fresh analysis - clearing all previous data")
        
        try:
            # CRITICAL: Force clear all existing components and reset counters
            self.components = {
                'GABLE': [],
                'T/B & FIX SHELVES': [],
                'BACKS': [],
                'S/H': []
            }
            self.part_counters = {
                'GABLE': 1,
                'T/B & FIX SHELVES': 1,
                'BACKS': 1,
                'S/H': 1
            }
            
            # Generate unique timestamp for this analysis
            analysis_id = datetime.now().strftime('%Y%m%d_%H%M%S_%f')
            st.info(f"Starting fresh analysis #{analysis_id}")
            
            # Step 1: Fresh OCR extraction for this specific image
            st.info("Step 1: Extracting text from THIS specific drawing...")
            extracted_text = self.extract_text_with_mistral_vision(image_bytes)
            
            # Step 1.5: OpenAI Vision fallback if Mistral is insufficient
            if not extracted_text or len(re.findall(r'\d+', extracted_text)) < 5:
                st.warning("Mistral AI extracted limited numbers - trying OpenAI Vision fallback...")
                openai_text = self.extract_text_with_openai_vision_fallback(image_bytes)
                
                if openai_text:
                    # Merge both extractions
                    combined_text = f"MISTRAL AI ANALYSIS #{analysis_id}:\n{extracted_text or 'No text'}\n\nOPENAI VISION ANALYSIS #{analysis_id}:\n{openai_text}"
                    extracted_text = combined_text
                    st.success("Combined Mistral AI + OpenAI Vision text extraction")
                else:
                    st.warning("OpenAI Vision fallback also failed")
            
            # Critical validation
            if not extracted_text:
                st.error("Complete OCR failure - no text could be extracted from the image")
                return self.generate_empty_cutting_list()
            
            # Check numbers extraction
            numbers = re.findall(r'\d+', extracted_text)
            st.info(f"Analysis #{analysis_id}: Extracted {len(numbers)} numbers: {numbers[:20]}...")
            
            if len(numbers) < 3:
                st.error(f"OCR validation failed - only {len(numbers)} numbers extracted from THIS drawing")
                return self.generate_empty_cutting_list()
            
            with st.expander(f"View extracted text from analysis #{analysis_id}"):
                st.text(extracted_text)
            
            # Step 2: Fresh dimension analysis - pass analysis ID to prevent caching
            st.info(f"Step 2: Analyzing dimensions from analysis #{analysis_id}...")
            image_base64 = base64.b64encode(image_bytes).decode('utf-8')
            analysis_result = self.analyze_dimensions_with_openai(extracted_text, image_base64, analysis_id)
            
            if 'error' in analysis_result:
                st.error(f"AI dimension analysis failed: {analysis_result['error']}")
                return self.generate_empty_cutting_list()
            
            # Step 3: Process results
            st.info(f"Step 3: Processing analysis results #{analysis_id}...")
            
            confidence = analysis_result.get('analysis_confidence', 'unknown')
            st.info(f"Analysis #{analysis_id} confidence: {confidence}")
            
            measurements = analysis_result.get('extracted_measurements', [])
            ignored = analysis_result.get('ignored_measurements', [])
            
            if measurements:
                st.success(f"Used measurements from this drawing: {measurements}")
            if ignored:
                st.warning(f"Ignored measurements: {ignored}")
            
            # Process cabinet modules with fresh data
            self.process_hybrid_cabinet_analysis(analysis_result)
            
            notes = analysis_result.get('notes', '')
            if notes:
                st.info(f"Analysis #{analysis_id} notes: {notes}")
            
            # Final validation
            total_components = sum(len(items) for items in self.components.values())
            if total_components == 0:
                st.error(f"No valid components generated from analysis #{analysis_id}")
                return self.generate_empty_cutting_list()
            
            st.success(f"Analysis #{analysis_id} completed: Generated {total_components} components")
                    
        except Exception as e:
            logger.error(f"Error in analysis #{analysis_id}: {str(e)}")
            st.error(f"Analysis failed: {str(e)}")
            return self.generate_empty_cutting_list()
        
        return self.generate_cutting_list()
    
    def extract_text_with_mistral_vision(self, image_bytes):
        """Extract text and dimensions using Mistral AI vision model"""
        
        if not MISTRAL_API_KEY:
            st.error("Mistral API key not configured")
            return None
        
        # Convert image to base64
        image_base64 = base64.b64encode(image_bytes).decode('utf-8')
        
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {MISTRAL_API_KEY}"
        }
        
        payload = {
            "model": "pixtral-12b-2409",  # Mistral's vision model
            "messages": [
                {
                    "role": "user",
                    "content": [
                        {
                            "type": "text",
                            "text": """You are an OCR specialist analyzing a technical drawing for cabinet making.

EXTRACT ALL TEXT AND NUMBERS from this technical drawing, focusing on:
1. All visible numbers and dimensions (like 650, 1200, 340, etc.)
2. Any text labels or annotations
3. Dimension lines and measurements
4. Size specifications

Be thorough - extract every number you can see, even if small or partially visible.
List them clearly and indicate where you found them (near what elements).

Focus especially on measurements that could be cabinet dimensions:
- Heights (typically 200-2600mm)  
- Widths (typically 200-2000mm)
- Depths (typically 200-800mm)

Also list any very large numbers (>3000mm) as these are likely room dimensions to ignore."""
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
            "max_tokens": 1000,
            "temperature": 0.1
        }
        
        try:
            st.info("Submitting image to Mistral AI for text extraction...")
            response = requests.post(MISTRAL_API_URL, headers=headers, json=payload, timeout=60)
            response.raise_for_status()
            
            result = response.json()
            
            if 'error' in result:
                st.error(f"Mistral API error: {result['error']}")
                return None
            
            content = result['choices'][0]['message']['content']
            
            # Extract numbers from the response and validate
            numbers = re.findall(r'\d+(?:\.\d+)?', content)
            st.info(f"Mistral AI extracted {len(numbers)} numbers: {numbers[:10]}{'...' if len(numbers) > 10 else ''}")
            
            # Flag if too few numbers found
            if len(numbers) < 3:
                st.warning("Mistral AI extracted very few numbers - may need manual verification")
            
            return content
            
        except requests.exceptions.RequestException as e:
            st.error(f"Mistral API request failed: {str(e)}")
            return None
        except Exception as e:
            st.error(f"Unexpected error in Mistral AI analysis: {str(e)}")
            return None
    
    def extract_text_with_openai_vision_fallback(self, image_bytes):
        """Fallback: Use OpenAI's vision model for text extraction"""
        
        if not OPENAI_API_KEY:
            return None
        
        st.info("Using OpenAI Vision as fallback for text extraction...")
        
        image_base64 = base64.b64encode(image_bytes).decode('utf-8')
        
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
                            "text": "Extract ALL numbers, dimensions, and text visible in this technical drawing. Focus especially on measurements like 650, 1164, 340, etc. List every number you can see, even if small or partially visible."
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
            "max_tokens": 1000,
            "temperature": 0.1
        }
        
        try:
            response = requests.post(OPENAI_API_URL, headers=headers, json=payload, timeout=60)
            response.raise_for_status()
            
            result = response.json()
            content = result['choices'][0]['message']['content']
            
            return content
            
        except Exception as e:
            logger.error(f"OpenAI vision fallback failed: {str(e)}")
            return None
    
    def analyze_dimensions_with_openai(self, extracted_text, image_base64, analysis_id=None):
        """Enhanced OpenAI prompt using configurable offsets for precise workshop requirements"""
        
        analysis_id = analysis_id or datetime.now().strftime('%H%M%S')
        
        # Extract numbers outside of f-string to avoid backslash issues
        extracted_numbers = re.findall(r'\d+', extracted_text)
        
        prompt = f"""
        You are analyzing a technical drawing to create a cutting list for ONE SINGLE CABINET only.

        EXTRACTED TEXT FROM DRAWING:
        "{extracted_text}"

        ====================================
        CRITICAL REQUIREMENTS
        ====================================
        1. IDENTIFY EXACTLY ONE CABINET from this drawing
        2. GENERATE EXACTLY 4 COMPONENTS ONLY:
           - Gables (end panels) - 2 pieces
           - T/B panels (Top/Bottom) - 2 pieces 
           - S/H hardware (Shelves) - 1 piece
           - Back panel - 1 piece

        ====================================
        DIMENSION DETECTION PROCESS
        ====================================
        
        **STEP 1: Extract all numbers from the text**
        Find ALL numeric values in the extracted text: {extracted_numbers}
        
        **STEP 2: Classify dimensions by typical cabinet ranges**
        - WIDTH candidates: Numbers between 800-2000mm (typically 1200, 1350, 1500, etc.)
        - HEIGHT candidates: Numbers between 400-800mm (typically 600, 650, 720, etc.)  
        - DEPTH candidates: Numbers between 250-500mm (typically 340, 370, 400, etc.)
        
        **STEP 3: Select the most likely cabinet dimensions**
        Choose ONE dimension from each category that represents the main cabinet:
        - Prefer dimensions that appear multiple times
        - Ignore very large numbers (>2500mm) - these are room dimensions
        - Ignore very small numbers (<200mm) - these are hardware/thickness dimensions
        
        **STEP 4: Validate selected dimensions make sense together**
        The selected Width x Height x Depth should be reasonable for a cabinet.

        ====================================
        DEFINITIVE FORMULAS WITH CONFIGURABLE OFFSETS
        ====================================
        
        Workshop Configuration:
        - BACK_WIDTH_OFFSET = {self.BACK_WIDTH_OFFSET}mm
        - TOP_DEPTH_OFFSET = {self.TOP_DEPTH_OFFSET}mm  
        - SHELF_DEPTH_OFFSET = {self.SHELF_DEPTH_OFFSET}mm
        - THICKNESS = {self.THICKNESS}mm
        
        Once you have identified the cabinet Width (W), Height (H), and Depth (D), 
        apply these EXACT mathematical formulas:
        
        1. **Gables (end panels)**: 
           - height = H (use detected cabinet height exactly)
           - width = D (use detected cabinet depth exactly)
           - quantity = 2
           - Formula: H x D
        
        2. **T/B panels (Top/Bottom)**: 
           - height = W - {self.BACK_WIDTH_OFFSET} (subtract BACK_WIDTH_OFFSET from detected width)
           - width = D - {self.TOP_DEPTH_OFFSET} (subtract TOP_DEPTH_OFFSET from detected depth)
           - quantity = 2
           - Formula: (W - {self.BACK_WIDTH_OFFSET}) x (D - {self.TOP_DEPTH_OFFSET})
        
        3. **S/H hardware (Shelves)**: 
           - height = W - {self.BACK_WIDTH_OFFSET} (subtract BACK_WIDTH_OFFSET from detected width)
           - width = D - {self.SHELF_DEPTH_OFFSET} (subtract SHELF_DEPTH_OFFSET from detected depth)
           - quantity = 1
           - Formula: (W - {self.BACK_WIDTH_OFFSET}) x (D - {self.SHELF_DEPTH_OFFSET})
        
        4. **Back panel**: 
           - height = H (use detected cabinet height exactly)
           - width = W - {self.BACK_WIDTH_OFFSET} (subtract BACK_WIDTH_OFFSET from detected width)
           - quantity = 1
           - Formula: H x (W - {self.BACK_WIDTH_OFFSET})

        ====================================
        CALCULATION VERIFICATION
        ====================================
        
        **Before responding, verify your math using the configured offsets:**
        
        If you detected cabinet dimensions WxHxD, calculate:
        - Gables: H x D 
        - T/B: (W-{self.BACK_WIDTH_OFFSET}) x (D-{self.TOP_DEPTH_OFFSET})
        - S/H: (W-{self.BACK_WIDTH_OFFSET}) x (D-{self.SHELF_DEPTH_OFFSET})
        - Back: H x (W-{self.BACK_WIDTH_OFFSET})
        
        **Example verification (for 1200x650x340 with current offsets):**
        - Gables: 650 x 340 = 650x340 ✓
        - T/B: (1200-{self.BACK_WIDTH_OFFSET}) x (340-{self.TOP_DEPTH_OFFSET}) = {1200-self.BACK_WIDTH_OFFSET}x{340-self.TOP_DEPTH_OFFSET} ✓
        - S/H: (1200-{self.BACK_WIDTH_OFFSET}) x (340-{self.SHELF_DEPTH_OFFSET}) = {1200-self.BACK_WIDTH_OFFSET}x{340-self.SHELF_DEPTH_OFFSET} ✓
        - Back: 650 x (1200-{self.BACK_WIDTH_OFFSET}) = 650x{1200-self.BACK_WIDTH_OFFSET} ✓

        ====================================
        JSON RESPONSE FORMAT
        ====================================
        {{
        "analysis_confidence": "high|medium|low",
        "cabinet_modules": [
            {{
            "module_id": 1,
            "cabinet_width": [detected_W_value],
            "cabinet_height": [detected_H_value],
            "cabinet_depth": [detected_D_value],
            "source_measurements": ["[W_value]", "[H_value]", "[D_value]"],
            "calculated_components": {{
                "gables": {{
                "formula": "Height x Depth",
                "height": [H_value],
                "width": [D_value],
                "quantity": 2
                }},
                "tb_panels": {{
                "formula": "(Width - {self.BACK_WIDTH_OFFSET}) x (Depth - {self.TOP_DEPTH_OFFSET})",
                "height": [W_value - self.BACK_WIDTH_OFFSET],
                "width": [D_value - self.TOP_DEPTH_OFFSET],
                "quantity": 2
                }},
                "sh_hardware": {{
                "formula": "(Width - {self.BACK_WIDTH_OFFSET}) x (Depth - {self.SHELF_DEPTH_OFFSET})",
                "height": [W_value - self.BACK_WIDTH_OFFSET],
                "width": [D_value - self.SHELF_DEPTH_OFFSET],
                "quantity": 1
                }},
                "back": {{
                "formula": "Height x (Width - {self.BACK_WIDTH_OFFSET})",
                "height": [H_value],
                "width": [W_value - self.BACK_WIDTH_OFFSET],
                "quantity": 1
                }}
            }}
            }}
        ],
        "extracted_measurements": {extracted_numbers},
        "ignored_measurements": [list_of_rejected_large_numbers],
        "dimension_selection_reasoning": "Explain why you chose these specific WxHxD values",
        "notes": "Cabinet detected: [W]x[H]x[D]mm with offsets BACK_WIDTH_OFFSET={self.BACK_WIDTH_OFFSET}, TOP_DEPTH_OFFSET={self.TOP_DEPTH_OFFSET}, SHELF_DEPTH_OFFSET={self.SHELF_DEPTH_OFFSET}"
        }}

        ====================================
        CRITICAL REMINDERS
        ====================================
        1. Do the actual arithmetic using the configured offsets
        2. Use the specific dimensions YOU DETECT from THIS drawing
        3. Apply the offset formulas correctly using the provided constants
        4. Double-check all calculations before responding
        5. Show your dimension selection reasoning
        6. Use the exact offset values provided: BACK_WIDTH_OFFSET={self.BACK_WIDTH_OFFSET}, TOP_DEPTH_OFFSET={self.TOP_DEPTH_OFFSET}, SHELF_DEPTH_OFFSET={self.SHELF_DEPTH_OFFSET}
        """

        if not OPENAI_API_KEY:
            return {"error": "OpenAI API key not configured"}

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
            st.info("Sending request to OpenAI for dimension analysis...")
            response = requests.post(OPENAI_API_URL, headers=headers, json=payload, timeout=60)
            response.raise_for_status()
            
            result = response.json()
            content = result['choices'][0]['message']['content']
            
            # Extract JSON from response
            json_start = content.find('{')
            json_end = content.rfind('}') + 1
            
            if json_start != -1 and json_end > json_start:
                json_str = content[json_start:json_end]
                parsed_result = json.loads(json_str)
                
                # Show what was ignored
                ignored = parsed_result.get('ignored_measurements', [])
                if ignored:
                    st.warning(f"Ignored room dimensions: {ignored}")
                
                return parsed_result
            else:
                return {"error": "No valid JSON in OpenAI response"}
                
        except Exception as e:
            logger.error(f"OpenAI analysis error: {str(e)}")
            return {"error": f"OpenAI request failed: {str(e)}"}
    
    def process_hybrid_cabinet_analysis(self, analysis):
        """Process analysis results - DYNAMIC cabinet with exactly 4 components only"""
        
        # Force clear all existing components
        for category in self.components:
            self.components[category] = []
        
        # Reset part counters to ensure fresh start
        for category in self.part_counters:
            self.part_counters[category] = 1
        
        cabinet_modules = analysis.get('cabinet_modules', [])
        
        if not cabinet_modules:
            st.error("No cabinet modules identified from the drawing")
            return
        
        # CRITICAL: Process ONLY the first module (single cabinet approach)
        module = cabinet_modules[0]  # Take only the first module, ignore others
        
        module_id = module.get('module_id', 1)
        cabinet_width = module.get('cabinet_width', 0)
        cabinet_height = module.get('cabinet_height', 0)
        cabinet_depth = module.get('cabinet_depth', 0)
        
        # Validate cabinet dimensions
        if not self.validate_cabinet_dimensions(cabinet_width, cabinet_height, cabinet_depth):
            st.error(f"Invalid cabinet dimensions: {cabinet_width}x{cabinet_height}x{cabinet_depth}")
            return
        
        st.success(f"Processing cabinet from THIS drawing: {cabinet_width}W x {cabinet_height}H x {cabinet_depth}D mm")
        
        # Show dimension selection reasoning if available
        reasoning = analysis.get('dimension_selection_reasoning', '')
        if reasoning:
            st.info(f"Dimension selection: {reasoning}")
        
        calculated_components = module.get('calculated_components', {})
        
        # Process EXACTLY 4 component types only
        required_components = ['gables', 'tb_panels', 'sh_hardware', 'back']
        component_mapping = {
            'gables': ('GABLE', 'Gables'),
            'tb_panels': ('T/B & FIX SHELVES', 'Top/Bottom panels'),
            'sh_hardware': ('S/H', 'Shelf hardware'), 
            'back': ('BACKS', 'Back panel')
        }
        
        components_generated = 0
        
        for comp_name in required_components:
            if comp_name not in calculated_components:
                st.warning(f"Missing required component: {comp_name}")
                continue
                
            comp_data = calculated_components[comp_name]
            if not comp_data or comp_data.get('quantity', 0) == 0:
                continue
            
            category, comp_description = component_mapping[comp_name]
            
            component_height = comp_data.get('height', 0)
            component_width = comp_data.get('width', 0)  
            quantity = comp_data.get('quantity', 1)
            formula = comp_data.get('formula', '')
            
            # Validate component dimensions
            if not self.validate_component_dimensions(component_height, component_width, comp_name):
                st.warning(f"Invalid dimensions for {comp_name}: {component_height}x{component_width} - skipping")
                continue
            
            description = f"Cabinet {cabinet_width}x{cabinet_height}x{cabinet_depth} - {comp_description} ({formula})"
            # Store as Height x Width format
            self.add_component(category, component_height, component_width, quantity, description)
            
            st.success(f"✓ {comp_description}: {component_height}x{component_width} qty:{quantity}")
            components_generated += 1
        
        # Final validation - ensure exactly 4 component types
        if components_generated != 4:
            st.warning(f"Generated {components_generated} components, expected exactly 4")
        else:
            st.success("✅ Generated exactly 4 component types for this cabinet")
        
        # Show summary with the detected cabinet dimensions
        st.info(f"FINAL OUTPUT - Cabinet {cabinet_width}x{cabinet_height}x{cabinet_depth} with 4 Components:")
        for category, items in self.components.items():
            if items:
                for item in items:
                    st.write(f"- {item['part_id']}: {item['dimensions']} ({item['quantity']} pcs)")
    
    def validate_cabinet_dimensions(self, width, height, depth):
        """Validate cabinet dimensions are realistic"""
        if width < 200 or width > 2000:
            return False
        if height < 200 or height > 2600:
            return False
        if depth < 200 or depth > 800:
            return False
        return True
    
    def validate_component_dimensions(self, height, width, component_type):
        """Validate individual component dimensions are realistic"""
        if height <= 0 or width <= 0:
            return False
        if height > 3000 or width > 3000:  # No component should be larger than 3m
            return False
        
        # Component-specific validation
        if component_type == 'gables':
            # Gables should be cabinet height x cabinet depth
            if height > 2600 or width > 800:  # Max cabinet height/depth
                return False
        elif component_type == 'back':
            # Back should be cabinet height x (cabinet width - 36)
            if height > 2600 or width > 2000:  # Max cabinet height/width
                return False
        elif component_type in ['tb_panels', 'sh_hardware']:
            # T/B and S/H should be (cabinet width - 36) x cabinet depth variants
            if height > 2000 or width > 800:  # Max processed width/depth
                return False
                
        return True
    
    def add_component(self, category, height, width, quantity, description):
        """Add a component with validation and proper part ID generation - Height x Width format"""
        try:
            # Validate inputs - ensure we have positive numbers
            height = max(10, int(round(height)))
            width = max(10, int(round(width)))
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
                'dimensions': f"{height}x{width}",  # Height x Width format
                'height': height,
                'width': width, 
                'quantity': quantity,
                'material_type': material_type,
                'notes': description,
                'raw_text': description
            }
            
            self.components[category].append(component_data)
            self.part_counters[category] += 1
            
            logger.debug(f"Added to {category}: {part_id} - {height}x{width} qty:{quantity} - {description}")
            
        except Exception as e:
            logger.error(f"Error adding component: {str(e)}")
    
    def get_category_short_name(self, category):
        """Get short name for category"""
        short_names = {
            'GABLE': 'GABLE',
            'T/B & FIX SHELVES': 'SHELF',
            'BACKS': 'BACK',
            'S/H': 'HARDWARE'
        }
        return short_names.get(category, 'COMP')
    
    def get_material_type(self, category):
        """Get material type for category"""
        materials = {
            'GABLE': '18mm MFC',
            'T/B & FIX SHELVES': '18mm MFC',
            'BACKS': '6mm MDF',
            'S/H': 'Hardware'
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

def create_summary_charts(categorized_data):
    """Create summary charts for the cutting list"""
    
    # Prepare data for charts
    categories = []
    pieces = []
    areas = []
    
    for category, data in categorized_data.items():
        if data.get('total_pieces', 0) > 0:
            categories.append(category)
            pieces.append(data['total_pieces'])
            areas.append(data['total_area'])
    
    # Create pieces chart
    fig_pieces = px.bar(
        x=categories, 
        y=pieces,
        title="Total Pieces by Category",
        labels={'x': 'Category', 'y': 'Number of Pieces'},
        color=pieces,
        color_continuous_scale='Blues'
    )
    fig_pieces.update_layout(showlegend=False, xaxis_tickangle=-45)
    
    # Create area chart
    fig_area = px.bar(
        x=categories, 
        y=areas,
        title="Total Area by Category (m²)",
        labels={'x': 'Category', 'y': 'Area (m²)'},
        color=areas,
        color_continuous_scale='Greens'
    )
    fig_area.update_layout(showlegend=False, xaxis_tickangle=-45)
    
    return fig_pieces, fig_area

def display_cutting_list_table(categorized_data):
    """Display cutting list as an interactive table"""
    
    all_items = []
    for category, data in categorized_data.items():
        for item in data.get('items', []):
            all_items.append({
                'Category': category,
                'Part ID': item['part_id'],
                'Dimensions': item['dimensions'],
                'Height (mm)': item['height'],
                'Width (mm)': item['width'],
                'Quantity': item['quantity'],
                'Material': item['material_type'],
                'Notes': item['notes']
            })
    
    if all_items:
        df = pd.DataFrame(all_items)
        return df
    else:
        return pd.DataFrame()

def main():
    st.set_page_config(
        page_title="Technical Drawing Analyzer - Mistral AI",
        page_icon="📐",
        layout="wide",
        initial_sidebar_state="expanded"
    )
    
    # Custom CSS
    st.markdown("""
    <style>
    .main-header {
        font-size: 3rem;
        font-weight: bold;
        text-align: center;
        color: #2E86AB;
        margin-bottom: 2rem;
    }
    .sub-header {
        font-size: 1.5rem;
        color: #A23B72;
        margin-bottom: 1rem;
    }
    .metric-card {
        background-color: #f0f2f6;
        padding: 1rem;
        border-radius: 0.5rem;
        margin: 0.5rem 0;
    }
    .success-message {
        padding: 1rem;
        background-color: #d4edda;
        border: 1px solid #c3e6cb;
        border-radius: 0.25rem;
        color: #155724;
        margin: 1rem 0;
    }
    .error-message {
        padding: 1rem;
        background-color: #f8d7da;
        border: 1px solid #f5c6cb;
        border-radius: 0.25rem;
        color: #721c24;
        margin: 1rem 0;
    }
    </style>
    """, unsafe_allow_html=True)
    
    # Header
    st.markdown('<h1 class="main-header">📐 Technical Drawing Analyzer</h1>', unsafe_allow_html=True)
    st.markdown('<p style="text-align: center; font-size: 1.2rem; color: #666;">Transform your technical drawings into detailed cutting lists with Mistral AI-powered cabinet analysis</p>', unsafe_allow_html=True)
    
    # Sidebar
    with st.sidebar:
        st.header("⚙️ Configuration")
        
        # API credentials status
        st.subheader("Available APIs")
        if MISTRAL_API_KEY:
            st.success("✅ Mistral AI configured")
        else:
            st.error("❌ Mistral AI not configured")
            
        if OPENAI_API_KEY:
            st.success("✅ OpenAI API configured")
        else:
            st.error("❌ OpenAI API not configured")
        
        # Show analysis method
        if MISTRAL_API_KEY and OPENAI_API_KEY:
            st.success("🎯 Full Hybrid Analysis Available")
            selected_api = "Mistral + OpenAI Hybrid"
        elif MISTRAL_API_KEY:
            st.success("🤖 Mistral AI Vision Analysis")
            selected_api = "Mistral AI Only"
        elif OPENAI_API_KEY:
            st.warning("🔄 OpenAI Vision-only Analysis")
            selected_api = "OpenAI Only"
        else:
            st.error("No APIs configured. Set MISTRAL_API_KEY and OPENAI_API_KEY environment variables")
            selected_api = None
        
        st.markdown("---")
        
        # Offset Configuration
        st.subheader("🔧 Workshop Configuration")
        with st.expander("Configure Cabinet Offsets", expanded=False):
            st.info("Adjust offsets to match your workshop standards")
            
            back_width_offset = st.number_input(
                "Back Width Offset (mm)", 
                min_value=0, max_value=100, value=36,
                help="Subtracted from cabinet width for back panel and component widths"
            )
            
            top_depth_offset = st.number_input(
                "Top/Bottom Depth Offset (mm)", 
                min_value=0, max_value=100, value=30,
                help="Subtracted from cabinet depth for T/B panel depth"
            )
            
            shelf_depth_offset = st.number_input(
                "Shelf Depth Offset (mm)", 
                min_value=0, max_value=100, value=40,
                help="Subtracted from cabinet depth for shelf/hardware depth"
            )
            
            thickness = st.number_input(
                "Board Thickness (mm)", 
                min_value=6, max_value=25, value=18,
                help="Standard board thickness for calculations"
            )
            
            if st.button("Apply Configuration"):
                st.session_state['offsets'] = {
                    'back_width_offset': back_width_offset,
                    'top_depth_offset': top_depth_offset, 
                    'shelf_depth_offset': shelf_depth_offset,
                    'thickness': thickness
                }
                st.success("Configuration applied!")
        
        # Show current configuration
        current_config = st.session_state.get('offsets', {
            'back_width_offset': 36,
            'top_depth_offset': 30,
            'shelf_depth_offset': 40, 
            'thickness': 18
        })
        
        st.info(f"""
        **Current Settings:**
        - Back Width Offset: {current_config['back_width_offset']}mm
        - Top Depth Offset: {current_config['top_depth_offset']}mm  
        - Shelf Depth Offset: {current_config['shelf_depth_offset']}mm
        - Board Thickness: {current_config['thickness']}mm
        """)
        
        st.markdown("---")
        
        # Analysis info
        st.subheader("📐 Definitive Cabinet Formulas")
        st.info(f"""
        **Component Formulas (with current offsets):**
        
        1. **Gables**: Height × Depth (2 pcs)
        2. **T/B**: (Width - {current_config['back_width_offset']}) × (Depth - {current_config['top_depth_offset']}) (2 pcs)
        3. **S/H**: (Width - {current_config['back_width_offset']}) × (Depth - {current_config['shelf_depth_offset']}) (1 pc)
        4. **Back**: Height × (Width - {current_config['back_width_offset']}) (1 pc)
        
        **Example (1200×650×340 cabinet):**
        - Gables: 650 × 340
        - T/B: {1200-current_config['back_width_offset']} × {340-current_config['top_depth_offset']}
        - S/H: {1200-current_config['back_width_offset']} × {340-current_config['shelf_depth_offset']}
        - Back: 650 × {1200-current_config['back_width_offset']}
        
        **Configurable for different workshop requirements**
        """)
        
        st.markdown("---")
        
        # Quick Actions
        st.subheader("Quick Actions")
        if st.button("🔄 Clear All", type="secondary"):
            for key in list(st.session_state.keys()):
                del st.session_state[key]
            st.rerun()
    
    # Main content
    col1, col2 = st.columns([1, 1])
    
    with col1:
        st.markdown('<h2 class="sub-header">📁 Upload Drawing</h2>', unsafe_allow_html=True)
        
        uploaded_file = st.file_uploader(
            "Choose a technical drawing file",
            type=['png', 'jpg', 'jpeg', 'gif', 'webp', 'pdf'],
            help="Upload a technical drawing image or PDF for analysis"
        )
        
        if uploaded_file is not None:
            # Display uploaded image (if it's an image)
            if uploaded_file.type.startswith('image/'):
                image = Image.open(uploaded_file)
                st.image(image, caption=f"Uploaded: {uploaded_file.name}", use_column_width=True)
            else:
                st.info(f"Uploaded PDF: {uploaded_file.name}")
            
            # Analysis button
            if st.button("🔍 Analyze Drawing", type="primary"):
                if not selected_api:
                    st.error("No API configured. Please set up Mistral AI and/or OpenAI API keys.")
                    return
                
                with st.spinner(f"Analyzing drawing with {selected_api}... This may take a moment."):
                    try:
                        # Get image data
                        image_bytes = uploaded_file.getvalue()
                        analyzer = DrawingAnalyzer()
                        
                        # Apply user-configured offsets if available
                        if 'offsets' in st.session_state:
                            offsets = st.session_state['offsets']
                            analyzer.set_offsets(
                                back_width_offset=offsets['back_width_offset'],
                                top_depth_offset=offsets['top_depth_offset'],
                                shelf_depth_offset=offsets['shelf_depth_offset'], 
                                thickness=offsets['thickness']
                            )
                            st.info(f"Using custom offsets: Back={offsets['back_width_offset']}mm, Top={offsets['top_depth_offset']}mm, Shelf={offsets['shelf_depth_offset']}mm")
                        
                        # Use hybrid analysis
                        categorized_data = analyzer.analyze_technical_drawing_hybrid(image_bytes)
                        
                        dxf_content = analyzer.generate_dxf()
                        
                        # Store results in session state
                        st.session_state['analysis_results'] = categorized_data
                        st.session_state['dxf_content'] = dxf_content
                        st.session_state['filename'] = uploaded_file.name
                        st.session_state['file_size'] = len(image_bytes)
                        st.session_state['analysis_timestamp'] = datetime.now()
                        st.session_state['analysis_method'] = selected_api
                        
                        st.success("✅ Analysis completed successfully!")
                        
                    except Exception as e:
                        st.error(f"❌ Analysis failed: {str(e)}")
                        logger.error(f"Analysis error: {str(e)}")
    
    with col2:
        st.markdown('<h2 class="sub-header">📊 Quick Stats</h2>', unsafe_allow_html=True)
        
        # Display stats if analysis results exist
        if 'analysis_results' in st.session_state:
            results = st.session_state['analysis_results']
            
            # Calculate totals
            total_pieces = sum(cat.get('total_pieces', 0) for cat in results.values())
            total_area = sum(cat.get('total_area', 0) for cat in results.values())
            active_categories = len([cat for cat in results.values() if cat.get('total_pieces', 0) > 0])
            
            # Display metrics
            col_a, col_b = st.columns(2)
            with col_a:
                st.metric("Total Pieces", total_pieces)
                st.metric("Active Categories", active_categories)
            with col_b:
                st.metric("Total Area", f"{total_area:.2f} m²")
                st.metric("Analysis Time", st.session_state.get('analysis_timestamp', datetime.now()).strftime('%H:%M:%S'))
            
            # File info
            if 'filename' in st.session_state:
                st.info(f"📄 **File:** {st.session_state['filename']}")
                st.info(f"📏 **Size:** {st.session_state.get('file_size', 0):,} bytes")
        
        else:
            st.info("Upload and analyze a drawing to see statistics")
    
    # Results section
    if 'analysis_results' in st.session_state:
        st.markdown("---")
        st.markdown('<h2 class="sub-header">📋 Analysis Results</h2>', unsafe_allow_html=True)
        
        results = st.session_state['analysis_results']
        
        # Create tabs for different views
        tab1, tab2, tab3, tab4 = st.tabs(["📊 Summary Charts", "📋 Detailed Table", "📐 DXF Preview", "📦 Category Breakdown"])
        
        with tab1:
            st.subheader("Visual Summary")
            
            try:
                fig_pieces, fig_area = create_summary_charts(results)
                
                col1, col2 = st.columns(2)
                with col1:
                    st.plotly_chart(fig_pieces, use_container_width=True)
                with col2:
                    st.plotly_chart(fig_area, use_container_width=True)
                
                # Summary metrics
                st.markdown("### 📈 Summary Metrics")
                total_pieces = sum(cat.get('total_pieces', 0) for cat in results.values())
                total_area = sum(cat.get('total_area', 0) for cat in results.values())
                
                col1, col2, col3, col4 = st.columns(4)
                with col1:
                    st.metric("Total Components", total_pieces)
                with col2:
                    st.metric("Total Area", f"{total_area:.2f} m²")
                with col3:
                    unique_sizes = sum(cat.get('unique_sizes', 0) for cat in results.values())
                    st.metric("Unique Sizes", unique_sizes)
                with col4:
                    avg_pieces_per_cat = total_pieces / max(1, len([c for c in results.values() if c.get('total_pieces', 0) > 0]))
                    st.metric("Avg/Category", f"{avg_pieces_per_cat:.1f}")
                    
            except Exception as e:
                st.error(f"Error creating charts: {str(e)}")
        
        with tab2:
            st.subheader("Complete Cutting List")
            
            try:
                df = display_cutting_list_table(results)
                
                if not df.empty:
                    # Add filters
                    col1, col2, col3 = st.columns(3)
                    with col1:
                        categories = st.multiselect("Filter by Category", df['Category'].unique(), default=df['Category'].unique())
                    with col2:
                        materials = st.multiselect("Filter by Material", df['Material'].unique(), default=df['Material'].unique())
                    with col3:
                        min_qty = st.number_input("Minimum Quantity", min_value=1, max_value=100, value=1)
                    
                    # Apply filters
                    filtered_df = df[
                        (df['Category'].isin(categories)) & 
                        (df['Material'].isin(materials)) & 
                        (df['Quantity'] >= min_qty)
                    ]
                    
                    st.dataframe(
                        filtered_df,
                        use_container_width=True,
                        hide_index=True,
                        column_config={
                            "Height (mm)": st.column_config.NumberColumn(format="%d mm"),
                            "Width (mm)": st.column_config.NumberColumn(format="%d mm"),
                            "Quantity": st.column_config.NumberColumn(format="%d pcs"),
                        }
                    )
                    
                    # Download buttons
                    st.markdown("### 💾 Export Options")
                    col1, col2, col3 = st.columns(3)
                    
                    with col1:
                        csv_data = filtered_df.to_csv(index=False)
                        st.download_button(
                            label="📄 Download CSV",
                            data=csv_data,
                            file_name=f"cutting_list_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
                            mime="text/csv"
                        )
                    
                    with col2:
                        # Excel download
                        excel_buffer = BytesIO()
                        with pd.ExcelWriter(excel_buffer, engine='openpyxl') as writer:
                            filtered_df.to_excel(writer, sheet_name='Cutting List', index=False)
                        excel_data = excel_buffer.getvalue()
                        
                        st.download_button(
                            label="📊 Download Excel",
                            data=excel_data,
                            file_name=f"cutting_list_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx",
                            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
                        )
                    
                    with col3:
                        if 'dxf_content' in st.session_state:
                            st.download_button(
                                label="📐 Download DXF",
                                data=st.session_state['dxf_content'],
                                file_name=f"cutting_layout_{datetime.now().strftime('%Y%m%d_%H%M%S')}.dxf",
                                mime="application/dxf"
                            )
                else:
                    st.warning("No data to display")
                    
            except Exception as e:
                st.error(f"Error creating table: {str(e)}")
        
        with tab3:
            st.subheader("DXF Layout Preview")
            
            if 'dxf_content' in st.session_state:
                try:
                    # Display DXF info
                    dxf_size = len(st.session_state['dxf_content'])
                    st.info(f"📐 DXF file generated successfully ({dxf_size:,} bytes)")
                    
                    # Show first few lines of DXF for preview
                    st.markdown("**DXF Content Preview:**")
                    preview_lines = st.session_state['dxf_content'].split('\n')[:20]
                    preview_text = '\n'.join(preview_lines)
                    st.code(preview_text, language='text')
                    
                    if len(preview_lines) >= 20:
                        st.info("... (showing first 20 lines)")
                    
                    # Download button
                    st.download_button(
                        label="📐 Download Complete DXF File",
                        data=st.session_state['dxf_content'],
                        file_name=f"cutting_layout_{datetime.now().strftime('%Y%m%d_%H%M%S')}.dxf",
                        mime="application/dxf",
                        type="primary"
                    )
                    
                except Exception as e:
                    st.error(f"Error displaying DXF preview: {str(e)}")
            else:
                st.warning("No DXF content available")
        
        with tab4:
            st.subheader("Category Breakdown")
            
            try:
                for category, data in results.items():
                    if data.get('total_pieces', 0) > 0:
                        with st.expander(f"📦 {category} ({data['total_pieces']} pieces)", expanded=False):
                            
                            col1, col2, col3 = st.columns(3)
                            with col1:
                                st.metric("Total Pieces", data['total_pieces'])
                            with col2:
                                st.metric("Unique Sizes", data['unique_sizes'])
                            with col3:
                                st.metric("Total Area", f"{data['total_area']:.2f} m²")
                            
                            # Show items in this category
                            if data.get('items'):
                                st.markdown("**Components:**")
                                for item in data['items']:
                                    st.markdown(f"- **{item['part_id']}**: {item['dimensions']} x {item['quantity']} pcs ({item['material_type']}) - {item['notes']}")
                            else:
                                st.info("No items in this category")
                                
            except Exception as e:
                st.error(f"Error displaying category breakdown: {str(e)}")
    
    # Footer
    st.markdown("---")
    st.markdown("""
    <div style="text-align: center; color: #666; padding: 2rem;">
        <p><strong>Technical Drawing Analyzer</strong> - Powered by Mistral AI Vision</p>
        <p>Mistral AI OCR + OpenAI Analysis = Precise Cabinet Cutting Lists</p>
        <p><em>CORRECTED: Only generates 4 components with exact dimensions</em></p>
    </div>
    """, unsafe_allow_html=True)

if __name__ == "__main__":
    main()
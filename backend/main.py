# from fastapi import FastAPI, File, UploadFile, HTTPException
# from fastapi.middleware.cors import CORSMiddleware
# from fastapi.responses import JSONResponse
# import uvicorn
# from analyzer import DrawingAnalyzer
# import io
# import logging
# import traceback
# from datetime import datetime
# import base64

# # Configure logging
# logging.basicConfig(level=logging.INFO)
# logger = logging.getLogger(__name__)

# app = FastAPI(
#     title="Kitchen Cabinet Drawing Analyzer API",
#     description="Professional kitchen cabinet analysis with Google Cloud Vision + OpenAI",
#     version="2.0.0"
# )

# # Configure CORS
# app.add_middleware(
#     CORSMiddleware,
#     allow_origins=["http://localhost:3000"],  # Next.js default port
#     allow_credentials=True,
#     allow_methods=["*"],
#     allow_headers=["*"],
# )

# # Global analyzer instance
# analyzer = DrawingAnalyzer()

# @app.get("/")
# async def root():
#     return {"message": "Kitchen Cabinet Drawing Analyzer API", "version": "2.0.0"}

# @app.get("/health")
# async def health_check():
#     return {
#         "status": "healthy",
#         "timestamp": datetime.now().isoformat(),
#         "api_status": {
#             "google_vision": "configured" if analyzer.vision_client else "not_configured",
#             "openai": "configured"  # We'll assume it's configured
#         }
#     }

# @app.post("/analyze")
# async def analyze_drawing(
#     file: UploadFile = File(...),
#     back_width_offset: int = 36,
#     top_depth_offset: int = 30,
#     shelf_depth_offset: int = 70,
#     thickness: int = 18,
#     leg_height_deduction: int = 100,
#     countertop_deduction: int = 25
# ):
#     try:
#         # Validate file type
#         if not file.content_type.startswith('image/'):
#             raise HTTPException(status_code=400, detail="File must be an image")
        
#         # Read file content
#         contents = await file.read()
        
#         if len(contents) == 0:
#             raise HTTPException(status_code=400, detail="Empty file")
        
#         # Configure analyzer with custom offsets
#         analyzer.set_offsets(
#             back_width_offset=back_width_offset,
#             top_depth_offset=top_depth_offset,
#             shelf_depth_offset=shelf_depth_offset,
#             thickness=thickness,
#             leg_height_deduction=leg_height_deduction,
#             countertop_deduction=countertop_deduction
#         )
        
#         logger.info(f"Starting analysis for file: {file.filename}")
        
#         # Run analysis
#         results = analyzer.analyze_technical_drawing(contents)
        
#         # Generate DXF
#         dxf_content = analyzer.generate_dxf()
        
#         # Calculate summary statistics
#         total_pieces = sum(cat.get('total_pieces', 0) for cat in results.values())
#         total_area = sum(cat.get('total_area', 0) for cat in results.values())
#         categories_with_items = len([c for c in results.values() if c.get('total_pieces', 0) > 0])
        
#         # Encode DXF content for frontend
#         dxf_base64 = base64.b64encode(dxf_content.encode()).decode() if dxf_content else None
        
#         # Prepare response
#         response_data = {
#             "success": True,
#             "filename": file.filename,
#             "timestamp": datetime.now().isoformat(),
#             "summary": {
#                 "total_pieces": total_pieces,
#                 "total_area": round(total_area, 2),
#                 "categories": categories_with_items
#             },
#             "results": results,
#             "dxf_content": dxf_base64,
#             "configuration": {
#                 "back_width_offset": back_width_offset,
#                 "top_depth_offset": top_depth_offset,
#                 "shelf_depth_offset": shelf_depth_offset,
#                 "thickness": thickness,
#                 "leg_height_deduction": leg_height_deduction,
#                 "countertop_deduction": countertop_deduction
#             }
#         }
        
#         logger.info(f"Analysis completed successfully for {file.filename}")
#         return JSONResponse(content=response_data)
        
#     except Exception as e:
#         logger.error(f"Analysis failed: {str(e)}")
#         logger.error(traceback.format_exc())
        
#         return JSONResponse(
#             status_code=500,
#             content={
#                 "success": False,
#                 "error": str(e),
#                 "message": "Analysis failed. Please check your image and try again."
#             }
#         )

# @app.get("/config/defaults")
# async def get_default_config():
#     return {
#         "back_width_offset": 36,
#         "top_depth_offset": 30,
#         "shelf_depth_offset": 70,
#         "thickness": 18,
#         "leg_height_deduction": 100,
#         "countertop_deduction": 25
#     }

# if __name__ == "__main__":
#     uvicorn.run(
#         "main:app",
#         host="0.0.0.0",
#         port=8000,
#         reload=True,
#         log_level="info"
#     )
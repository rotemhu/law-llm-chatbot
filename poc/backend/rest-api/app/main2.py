# from fastapi import FastAPI, HTTPException, Depends, status
# from fastapi.middleware.cors import CORSMiddleware
# from fastapi.responses import JSONResponse
# from contextlib import asynccontextmanager
# import time
# import uuid
# import logging
# from typing import Dict, Any
# import traceback

# from models.chat_models import ChatRequest, ChatResponse, ErrorResponse, Citation
# from dependencies.config import settings
# from .llm_pipeline import LLMPipeline

# # Configure logging
# logging.basicConfig(level=logging.INFO)
# logger = logging.getLogger(__name__)

# class APIError(Exception):
#     """Base API exception"""
#     def __init__(self, message: str, error_code: str, status_code: int = 500):
#         self.message = message
#         self.error_code = error_code
#         self.status_code = status_code
#         super().__init__(self.message)

# class ValidationError(APIError):
#     """Validation error"""
#     def __init__(self, message: str):
#         super().__init__(message, "VALIDATION_ERROR", 400)

# class LLMServiceError(APIError):
#     """LLM service error"""
#     def __init__(self, message: str):
#         super().__init__(message, "LLM_SERVICE_ERROR", 503)

# class ConfigurationError(APIError):
#     """Configuration error"""
#     def __init__(self, message: str):
#         super().__init__(message, "CONFIGURATION_ERROR", 500)

# # Global LLM pipeline instance
# llm_pipeline: LLMPipeline = None

# @asynccontextmanager
# async def lifespan(app: FastAPI):
#     """Application lifespan manager"""
#     global llm_pipeline
    
#     try:
#         logger.info("Initializing LLM pipeline...")
#         llm_pipeline = LLMPipeline()
#         logger.info("LLM pipeline initialized successfully")
#         yield
#     except Exception as e:
#         logger.error(f"Failed to initialize LLM pipeline: {e}")
#         raise ConfigurationError(f"Failed to initialize application: {str(e)}")
#     finally:
#         logger.info("Shutting down application...")
#         llm_pipeline = None

# # Initialize FastAPI app
# app = FastAPI(
#     title=settings.app_name,
#     version=settings.app_version,
#     description="API for Israeli legal consultation using RAG and LLM",
#     lifespan=lifespan
# )

# # Add CORS middleware
# app.add_middleware(
#     CORSMiddleware,
#     allow_origins=["*"],  # Configure appropriately for production
#     allow_credentials=True,
#     allow_methods=["*"],
#     allow_headers=["*"],
# )

# def get_llm_pipeline() -> LLMPipeline:
#     """Dependency to get LLM pipeline instance"""
#     if llm_pipeline is None:
#         raise ConfigurationError("LLM pipeline not initialized")
#     return llm_pipeline

# def validate_request(request: ChatRequest) -> None:
#     """Validate chat request"""
#     if not request.user_prompt or not request.user_prompt.strip():
#         raise ValidationError("User prompt cannot be empty")
    
#     if len(request.user_prompt.strip()) > 2000:
#         raise ValidationError("User prompt cannot exceed 2000 characters")
    
#     if request.max_tokens and (request.max_tokens < 100 or request.max_tokens > 4000):
#         raise ValidationError("max_tokens must be between 100 and 4000")
    
#     if request.temperature and (request.temperature < 0.0 or request.temperature > 2.0):
#         raise ValidationError("temperature must be between 0.0 and 2.0")

# @app.exception_handler(APIError)
# async def api_error_handler(request, exc: APIError):
#     """Handle API errors"""
#     logger.error(f"API Error: {exc.message} (Code: {exc.error_code})")
#     return JSONResponse(
#         status_code=exc.status_code,
#         content=ErrorResponse(
#             error=exc.message,
#             error_code=exc.error_code
#         ).model_dump()
#     )

# @app.exception_handler(Exception)
# async def general_exception_handler(request, exc: Exception):
#     """Handle unexpected errors"""
#     logger.error(f"Unexpected error: {str(exc)}\n{traceback.format_exc()}")
#     return JSONResponse(
#         status_code=500,
#         content=ErrorResponse(
#             error="Internal server error occurred",
#             error_code="INTERNAL_ERROR"
#         ).model_dump()
#     )

# @app.get("/")
# async def root():
#     """Root endpoint"""
#     return {
#         "message": f"Welcome to {settings.app_name}",
#         "version": settings.app_version,
#         "status": "operational"
#     }

# @app.get("/health")
# async def health_check():
#     """Health check endpoint"""
#     try:
#         pipeline = get_llm_pipeline()
#         return {
#             "status": "healthy",
#             "timestamp": time.time(),
#             "pipeline_ready": pipeline is not None
#         }
#     except Exception as e:
#         logger.error(f"Health check failed: {e}")
#         raise HTTPException(
#             status_code=503,
#             detail="Service unavailable"
#         )

# @app.post("/api/v1/chat", response_model=ChatResponse)
# async def ask_legal_question(
#     request: ChatRequest,
#     pipeline: LLMPipeline = Depends(get_llm_pipeline)
# ) -> ChatResponse:
#     """
#     Submit a legal question and receive an AI-generated legal opinion.
    
#     Args:
#         request: Chat request containing the legal question and parameters
        
#     Returns:
#         ChatResponse: Legal opinion with citations and metadata
        
#     Raises:
#         ValidationError: If request validation fails
#         LLMServiceError: If LLM service fails
#         ConfigurationError: If configuration is invalid
#     """
#     start_time = time.time()
#     chat_id = request.chat_id or str(uuid.uuid4())
    
#     try:
#         # Validate request
#         validate_request(request)
        
#         logger.info(f"Processing legal question for chat_id: {chat_id}")
        
#         # Process the question through the LLM pipeline
#         try:
#             response = pipeline.process_question(
#                 question=request.user_prompt.strip(),
#                 max_tokens=request.max_tokens,
#                 temperature=request.temperature
#             )
#         except Exception as e:
#             logger.error(f"LLM pipeline error for chat_id {chat_id}: {str(e)}")
#             raise LLMServiceError(f"Failed to process question: {str(e)}")
        
#         # Extract citations from source documents
#         citations = []
#         if 'source_documents' in response:
#             for doc in response['source_documents']:
#                 try:
#                     metadata = doc.metadata if hasattr(doc, 'metadata') else {}
#                     citation = Citation(
#                         law_name=metadata.get('law_name', 'Unknown Law'),
#                         section=metadata.get('section'),
#                         chapter=metadata.get('chapter'),
#                         part=metadata.get('part'),
#                         sign=metadata.get('sign'),
#                         text_excerpt=doc.page_content[:200] if hasattr(doc, 'page_content') else "",
#                         relevance_score=getattr(doc, 'score', None)
#                     )
#                     citations.append(citation)
#                 except Exception as e:
#                     logger.warning(f"Failed to process citation: {e}")
#                     continue
        
#         processing_time = time.time() - start_time
        
#         result = ChatResponse(
#             answer=response.get('result', 'No response generated'),
#             citations=citations,
#             chat_id=chat_id,
#             processing_time_seconds=round(processing_time, 2)
#         )
        
#         logger.info(f"Successfully processed question for chat_id: {chat_id} in {processing_time:.2f}s")
#         return result
        
#     except APIError:
#         # Re-raise API errors
#         raise
#     except Exception as e:
#         logger.error(f"Unexpected error processing question for chat_id {chat_id}: {str(e)}\n{traceback.format_exc()}")
#         raise LLMServiceError(f"Unexpected error occurred: {str(e)}")

# @app.get("/api/v1/status")
# async def get_status():
#     """Get API status and configuration"""
#     try:
#         pipeline = get_llm_pipeline()
#         return {
#             "service": settings.app_name,
#             "version": settings.app_version,
#             "status": "operational",
#             "pipeline_initialized": pipeline is not None,
#             "configuration": {
#                 "embedding_provider": settings.embedding_provider,
#                 "embedding_model": settings.embedding_model,
#                 "gemini_model": settings.gemini_model,
#                 "max_relevant_documents": settings.max_relevant_documents,
#                 "default_temperature": settings.default_temperature
#             }
#         }
#     except Exception as e:
#         logger.error(f"Status check failed: {e}")
#         return {
#             "service": settings.app_name,
#             "version": settings.app_version,
#             "status": "error",
#             "error": str(e)
#         }

# if __name__ == "__main__":
#     import uvicorn
#     uvicorn.run(
#         "main:app",
#         host="0.0.0.0",
#         port=8000,
#         reload=settings.debug,
#         log_level="info"
#     )
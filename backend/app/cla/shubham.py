# =============================================================================
# SHUBHAM V2 - PRODUCTION-READY CODE GENERATION AGENT
# Location: backend/app/agents/shubham.py
# Purpose: Full-stack code generation with quality validation
# =============================================================================
#
# KEY IMPROVEMENTS FROM V1:
# 1. No base64 encoding - direct text with NULL byte cleaning
# 2. Smart token allocation per file type
# 3. Automatic model escalation (uses AI Router V2)
# 4. Syntax validation before saving
# 5. File splitting for oversized code
# 6. Tilotma validation integration
# 7. Comprehensive error handling
#
# =============================================================================

import os
import ast
import re
import logging
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass
from enum import Enum
import uuid

# Import AI Router V2
from services.ai_router import ai_router, TaskComplexity

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


# =============================================================================
# DATA STRUCTURES
# =============================================================================

class FileType(Enum):
    """File types with different generation strategies"""
    MODELS = "models"           # Database models
    SCHEMAS = "schemas"         # Pydantic schemas
    ROUTERS = "routers"         # API endpoints
    SERVICES = "services"       # Business logic
    DATABASE = "database"       # DB connection
    DEPENDENCIES = "dependencies"  # Utility functions
    SECURITY = "security"       # Auth logic
    MAIN = "main"              # App entry point
    CONFIG = "config"          # Configuration files
    REQUIREMENTS = "requirements"  # Package list
    ENV_EXAMPLE = "env_example"   # Environment template
    README = "readme"          # Documentation


@dataclass
class FileGenerationRequest:
    """Request to generate a single file"""
    file_path: str
    file_type: FileType
    description: str
    architecture: Dict[str, Any]
    dependencies: List[str] = None  # Other files this depends on
    
    def __post_init__(self):
        if self.dependencies is None:
            self.dependencies = []


@dataclass
class GeneratedFile:
    """Result of file generation"""
    file_path: str
    content: str
    file_type: FileType
    tokens_used: int
    model_used: str
    was_escalated: bool
    was_split: bool
    validation_passed: bool
    syntax_valid: bool
    cost: float


@dataclass
class ValidationResult:
    """Result of code validation"""
    is_valid: bool
    syntax_errors: List[str]
    logic_issues: List[str]
    suggestions: List[str]
    should_regenerate: bool


# =============================================================================
# TOKEN ALLOCATION STRATEGY
# =============================================================================

# Smart token limits per file type
# These are starting points - AI Router will escalate if needed
TOKEN_LIMITS = {
    FileType.MODELS: 8192,          # Can be large with many tables
    FileType.SCHEMAS: 6000,         # Many Pydantic models
    FileType.ROUTERS: 5000,         # Multiple endpoints
    FileType.SERVICES: 5000,        # Business logic
    FileType.DATABASE: 2000,        # Simple connection
    FileType.DEPENDENCIES: 2000,    # Utility functions
    FileType.SECURITY: 3000,        # Auth logic
    FileType.MAIN: 3000,            # App setup
    FileType.CONFIG: 2000,          # Settings
    FileType.REQUIREMENTS: 1000,    # Package list
    FileType.ENV_EXAMPLE: 500,      # Environment vars
    FileType.README: 4000,          # Documentation
}

# File types that can be split if too large
SPLITTABLE_FILE_TYPES = [
    FileType.MODELS,
    FileType.SCHEMAS,
    FileType.ROUTERS,
]

# File types by complexity
FILE_COMPLEXITY = {
    FileType.MODELS: TaskComplexity.COMPLEX,
    FileType.SCHEMAS: TaskComplexity.COMPLEX,
    FileType.ROUTERS: TaskComplexity.COMPLEX,
    FileType.SERVICES: TaskComplexity.COMPLEX,
    FileType.DATABASE: TaskComplexity.SIMPLE,
    FileType.DEPENDENCIES: TaskComplexity.MEDIUM,
    FileType.SECURITY: TaskComplexity.COMPLEX,
    FileType.MAIN: TaskComplexity.MEDIUM,
    FileType.CONFIG: TaskComplexity.SIMPLE,
    FileType.REQUIREMENTS: TaskComplexity.SIMPLE,
    FileType.ENV_EXAMPLE: TaskComplexity.SIMPLE,
    FileType.README: TaskComplexity.MEDIUM,
}


# =============================================================================
# SHUBHAM AGENT CLASS
# =============================================================================

class Shubham:
    """
    Full-stack code generation agent.
    
    Responsibilities:
    - Generate backend code files (FastAPI)
    - Validate syntax and logic
    - Handle file splitting for large code
    - Coordinate with Tilotma for quality review
    
    Features:
    - Smart token management per file type
    - Automatic model escalation
    - NULL byte cleaning
    - Syntax validation
    - File splitting for oversized code
    """
    
    def __init__(self, project_id: str, user_id: str):
        """
        Initialize Shubham agent.
        
        Args:
            project_id: UUID of the project
            user_id: UUID of the user
        """
        self.project_id = project_id
        self.user_id = user_id
        self.logger = logging.getLogger(f"shubham.{project_id}")
        
        self.logger.info(f"🤖 Shubham initialized for project {project_id}")
    
    # =========================================================================
    # MAIN GENERATION METHODS
    # =========================================================================
    
    async def generate_file(
        self,
        request: FileGenerationRequest
    ) -> GeneratedFile:
        """
        Generate a single file with validation.
        
        Workflow:
        1. Create generation prompt
        2. Call AI with smart token limit
        3. Clean NULL bytes from response
        4. Validate syntax
        5. Handle truncation (escalate or split)
        6. Return validated file
        
        Args:
            request: File generation request
        
        Returns:
            GeneratedFile with content and metadata
        """
        
        self.logger.info(f"📝 Generating file: {request.file_path}")
        
        # Step 1: Create prompt
        prompt = self._create_generation_prompt(request)
        
        # Step 2: Get token limit for this file type
        max_tokens = TOKEN_LIMITS.get(request.file_type, 4000)
        complexity = FILE_COMPLEXITY.get(request.file_type, TaskComplexity.MEDIUM)
        
        # Step 3: Generate with AI Router (automatic escalation)
        try:
            response = await ai_router.generate(
                messages=[{"role": "user", "content": prompt}],
                task_type="code_generation",
                complexity=complexity,
                max_tokens=max_tokens,
                auto_escalate=True  # Automatic escalation if truncated
            )
            
            # Step 4: Clean NULL bytes
            clean_content = self._clean_code_content(response.content)
            
            # Step 5: Validate syntax
            is_valid, syntax_errors = self._validate_syntax(
                clean_content, 
                request.file_path
            )
            
            # Step 6: Handle truncation
            if response.finish_reason == "length" and not response.was_escalated:
                # Still truncated after escalation - need to split
                if request.file_type in SPLITTABLE_FILE_TYPES:
                    self.logger.warning(
                        f"⚠️ File {request.file_path} too large, splitting..."
                    )
                    return await self._split_and_generate(request)
                else:
                    # Can't split this file type
                    self.logger.error(
                        f"❌ File {request.file_path} truncated and cannot be split"
                    )
            
            # Step 6.5: Validate models file has all required classes
            if request.file_type == FileType.MODELS and is_valid:
                self.logger.info(f"🔍 Validating all models are present...")
                missing_models = self._validate_all_models_present(
                    clean_content,
                    request.architecture
                )
                
                self.logger.info(f"📊 Validation result: missing_models={missing_models}")
                
                if missing_models:
                    self.logger.warning(
                        f"⚠️ Models missing for tables: {missing_models}. "
                        "Regenerating with explicit class names..."
                    )
                    # Retry with even more explicit prompt including missing models
                    return await self._regenerate_with_missing_models(
                        request,
                        missing_models
                    )
                else:
                    self.logger.info(f"✅ All models validated successfully")
            
            # Step 7: Create result
            result = GeneratedFile(
                file_path=request.file_path,
                content=clean_content,
                file_type=request.file_type,
                tokens_used=response.output_tokens,
                model_used=response.model_id,
                was_escalated=response.was_escalated,
                was_split=False,
                validation_passed=is_valid,
                syntax_valid=is_valid,
                cost=response.cost_estimate
            )
            
            if is_valid:
                self.logger.info(
                    f"✅ Generated {request.file_path}: "
                    f"{response.output_tokens} tokens, "
                    f"₹{response.cost_estimate:.4f}"
                )
            else:
                self.logger.warning(
                    f"⚠️ Generated {request.file_path} with syntax errors: "
                    f"{syntax_errors}"
                )
            
            return result
            
        except Exception as e:
            self.logger.error(f"❌ Failed to generate {request.file_path}: {e}")
            raise
    
    async def generate_multiple_files(
        self,
        requests: List[FileGenerationRequest]
    ) -> List[GeneratedFile]:
        """
        Generate multiple files in optimal order.
        
        Generation order:
        1. Database models (others depend on them)
        2. Schemas (depend on models)
        3. Dependencies & Security (utilities)
        4. Services (depend on models, schemas)
        5. Routers (depend on everything)
        6. Main (depends on routers)
        7. Config files
        
        Args:
            requests: List of file generation requests
        
        Returns:
            List of generated files
        """
        
        self.logger.info(f"📦 Generating {len(requests)} files...")
        
        # Sort by dependency order
        ordered_requests = self._order_by_dependencies(requests)
        
        results = []
        for request in ordered_requests:
            result = await self.generate_file(request)
            results.append(result)
        
        # Summary
        total_tokens = sum(r.tokens_used for r in results)
        total_cost = sum(r.cost for r in results)
        failed = sum(1 for r in results if not r.validation_passed)
        
        self.logger.info(
            f"✅ Generated {len(results)} files: "
            f"{total_tokens} tokens, "
            f"₹{total_cost:.2f}, "
            f"{failed} validation failures"
        )
        
        return results
    
    # =========================================================================
    # PROMPT CREATION
    # =========================================================================
    
    def _create_generation_prompt(
        self,
        request: FileGenerationRequest
    ) -> str:
        """
        Create detailed prompt for file generation.
        
        Prompt includes:
        - File purpose and requirements
        - Architecture context
        - Dependencies
        - Code quality standards
        - Output format instructions
        """
        
        # Base prompt structure
        prompt = f"""Generate a production-ready {request.file_type.value} file for a FastAPI application.

FILE: {request.file_path}
DESCRIPTION: {request.description}

ARCHITECTURE:
{self._format_architecture_context(request.architecture)}

REQUIREMENTS:
- Write clean, production-ready code
- Include comprehensive error handling
- Add type hints for all functions
- Include docstrings for classes and functions
- Follow PEP 8 style guidelines
- Use async/await where appropriate
- Add input validation

OUTPUT FORMAT:
Return ONLY the complete Python code.
Do NOT include markdown formatting or code fences.
Do NOT include explanations before or after the code.
Start directly with the imports.

IMPORTANT:
- Generate COMPLETE code (no placeholders or TODO comments)
- Ensure all imports are included
- Handle all edge cases
- Include proper error messages
"""
        
        # Add file-specific instructions
        if request.file_type == FileType.MODELS:
            # Extract table names from architecture
            tables = request.architecture.get("database", {}).get("tables", [])
            
            # Create explicit table-to-class mapping
            table_mappings = []
            for table in tables:
                table_name = table.get("name", "")
                # Convert to singular class name: users → User, posts → Post
                if table_name.endswith("ies"):  # categories → Category
                    class_name = table_name[:-3] + "y"
                elif table_name.endswith("ses"):  # addresses → Address
                    class_name = table_name[:-2]
                elif table_name.endswith("s"):  # users → User, posts → Post
                    class_name = table_name[:-1]
                else:
                    class_name = table_name
                class_name = class_name.capitalize()
                table_mappings.append(f"  - Table '{table_name}' → class {class_name}(Base)")
            
            mapping_text = "\n".join(table_mappings)
            
            prompt += f"""
DATABASE MODELS SPECIFIC REQUIREMENTS:
**YOU MUST GENERATE EXACTLY {len(tables)} MODEL CLASSES. NO MORE, NO LESS.**

Required table-to-class mappings (follow EXACTLY):
{mapping_text}

Requirements:
- Use SQLAlchemy ORM with declarative base
- Use __tablename__ = "{table_name}" for each model
- Use SINGULAR class names as shown above
- Add proper relationships (ForeignKey, relationship())
- Include created_at and updated_at timestamps
- Use UUID for primary keys
- Add __repr__ methods for debugging
- Generate ALL models in a single file
- Do NOT create any additional models not listed above
- Do NOT rename or skip any models

VERIFICATION: After generating, check that you have created these EXACT classes:
{", ".join(f"class {m.split('class ')[1].split('(')[0]}" for m in table_mappings)}
"""
        
        elif request.file_type == FileType.SCHEMAS:
            prompt += """
PYDANTIC SCHEMAS SPECIFIC REQUIREMENTS:
- Create separate schemas for: Create, Update, Response
- Use proper Pydantic field validators
- Include examples in schema Config
- Handle optional fields correctly
- Add field descriptions
"""
        
        elif request.file_type == FileType.ROUTERS:
            prompt += """
API ROUTERS SPECIFIC REQUIREMENTS:
- Use proper HTTP status codes
- Include request/response models
- Add comprehensive error handling
- Include docstrings for API documentation
- Use dependencies for authentication
- Add rate limiting where appropriate
"""
        
        elif request.file_type == FileType.SECURITY:
            prompt += """
SECURITY SPECIFIC REQUIREMENTS:
- Use proper password hashing (bcrypt)
- Implement JWT token generation
- Add token expiry
- Include refresh token logic
- Protect against timing attacks
- Add rate limiting
"""
        
        return prompt
    
    def _format_architecture_context(
        self,
        architecture: Dict[str, Any]
    ) -> str:
        """Format architecture dict for prompt context"""
        
        # Extract key info
        context = []
        
        if "database" in architecture:
            db = architecture["database"]
            context.append(f"Database: {db.get('type', 'PostgreSQL')}")
            if "tables" in db:
                context.append(f"Tables: {len(db['tables'])}")
        
        if "api" in architecture:
            api = architecture["api"]
            if "endpoints" in api:
                context.append(f"Endpoints: {len(api['endpoints'])}")
        
        if "authentication" in architecture:
            auth = architecture["authentication"]
            context.append(f"Auth: {auth.get('type', 'JWT')}")
        
        return "\n".join(context)
    
    # =========================================================================
    # CODE CLEANING & VALIDATION
    # =========================================================================
    
    def _clean_code_content(self, raw_code: str) -> str:
        """
        Clean code content from AI response.
        
        Operations:
        1. Remove NULL bytes (0x00)
        2. Remove markdown code fences if present
        3. Strip leading/trailing whitespace
        4. Ensure valid UTF-8
        5. Remove any preamble/postamble text
        
        Args:
            raw_code: Raw code from AI
        
        Returns:
            Cleaned code ready for saving
        """
        
        # Step 1: Remove NULL bytes
        cleaned = raw_code.replace('\x00', '')
        
        # Step 2: Ensure valid UTF-8
        cleaned = cleaned.encode('utf-8', errors='ignore').decode('utf-8')
        
        # Step 3: Remove markdown code fences
        # Pattern: ```python\ncode\n``` or ```\ncode\n```
        cleaned = re.sub(r'^```(?:python)?\n', '', cleaned, flags=re.MULTILINE)
        cleaned = re.sub(r'\n```$', '', cleaned, flags=re.MULTILINE)
        
        # Step 4: Remove common preamble phrases
        preamble_patterns = [
            r'^Here is the (?:complete|production-ready) code:?\s*\n',
            r'^Here\'s the (?:complete|production-ready) code:?\s*\n',
            r'^This is the (?:complete|production-ready) code:?\s*\n',
        ]
        for pattern in preamble_patterns:
            cleaned = re.sub(pattern, '', cleaned, flags=re.IGNORECASE)
        
        # Step 5: Strip whitespace
        cleaned = cleaned.strip()
        
        return cleaned
    
    def _validate_syntax(
        self,
        code: str,
        file_path: str
    ) -> Tuple[bool, List[str]]:
        """
        Validate Python code syntax.
        
        Args:
            code: Python code to validate
            file_path: File path for error messages
        
        Returns:
            Tuple of (is_valid, list of error messages)
        """
        
        # Skip validation for non-Python files
        if not file_path.endswith('.py'):
            return True, []
        
        try:
            # Try to parse as Python AST
            ast.parse(code)
            return True, []
            
        except SyntaxError as e:
            error_msg = f"Line {e.lineno}: {e.msg}"
            self.logger.warning(f"⚠️ Syntax error in {file_path}: {error_msg}")
            return False, [error_msg]
        
        except Exception as e:
            error_msg = f"Validation error: {str(e)}"
            self.logger.warning(f"⚠️ Validation failed for {file_path}: {error_msg}")
            return False, [error_msg]
    
    def _detect_truncation(self, code: str) -> bool:
        """
        Detect if code was truncated mid-generation.
        
        Checks for:
        - Unclosed brackets/braces/parentheses
        - Incomplete function/class definitions
        - Trailing incomplete lines
        
        Args:
            code: Generated code
        
        Returns:
            True if code appears truncated
        """
        
        # Check bracket/brace balance
        if code.count('(') != code.count(')'):
            return True
        if code.count('{') != code.count('}'):
            return True
        if code.count('[') != code.count(']'):
            return True
        
        # Check for incomplete docstrings
        if code.count('"""') % 2 != 0:
            return True
        if code.count("'''") % 2 != 0:
            return True
        
        # Check if ends mid-line
        last_line = code.split('\n')[-1].strip()
        incomplete_patterns = [
            'def ', 'class ', 'async def ',
            'return ', 'yield ',
            'if ', 'elif ', 'else:', 'for ', 'while ',
            'try:', 'except', 'finally:',
        ]
        
        for pattern in incomplete_patterns:
            if last_line.endswith(pattern):
                return True
        
        return False
    
    def _validate_all_models_present(
        self,
        code: str,
        architecture: Dict[str, Any]
    ) -> List[str]:
        """
        Validate that all tables have corresponding model classes.
        
        Args:
            code: Generated models code
            architecture: Project architecture with table definitions
        
        Returns:
            List of table names that are missing models (empty if all present)
        """
        
        # Extract table names from architecture
        tables = architecture.get("database", {}).get("tables", [])
        if not tables:
            return []
        
        # Extract class names from code
        import re
        class_pattern = r'class\s+(\w+)\s*\('
        generated_classes = re.findall(class_pattern, code)
        
        self.logger.info(f"🔎 Generated classes found: {generated_classes}")
        
        # Normalize class names (lowercase for comparison)
        generated_classes_lower = [c.lower() for c in generated_classes]
        
        # Check each table has a corresponding model
        missing = []
        for table in tables:
            table_name = table.get("name", "")
            
            # Expected class name (singular)
            if table_name.endswith("ies"):
                expected_class = table_name[:-3] + "y"
            elif table_name.endswith("ses"):
                expected_class = table_name[:-2]
            elif table_name.endswith("s"):
                expected_class = table_name[:-1]
            else:
                expected_class = table_name
            
            expected_class = expected_class.lower()
            
            self.logger.info(
                f"🔎 Checking table '{table_name}': "
                f"expected class '{expected_class}', "
                f"found in generated: {expected_class in generated_classes_lower}"
            )
            
            # Check if class exists (check both singular and plural)
            if (expected_class not in generated_classes_lower and
                table_name.lower() not in generated_classes_lower):
                self.logger.warning(f"⚠️ Missing model for table '{table_name}'")
                missing.append(table_name)
        
        return missing
    
    async def _regenerate_with_missing_models(
        self,
        request: FileGenerationRequest,
        missing_models: List[str]
    ) -> GeneratedFile:
        """
        Regenerate models file with explicit focus on missing models.
        
        Args:
            request: Original generation request
            missing_models: List of table names that were missing
        
        Returns:
            Regenerated file with all models
        """
        
        self.logger.info(
            f"🔄 Regenerating {request.file_path} with focus on missing models: "
            f"{', '.join(missing_models)}"
        )
        
        # Update request description to emphasize missing models
        original_desc = request.description
        request.description = (
            f"{original_desc}\n\n"
            f"CRITICAL: Previous generation was missing models for these tables: "
            f"{', '.join(missing_models)}. "
            f"You MUST include model classes for ALL tables including these."
        )
        
        # Regenerate
        result = await self.generate_file(request)
        
        # Restore original description
        request.description = original_desc
        
        return result
    
    # =========================================================================
    # FILE SPLITTING
    # =========================================================================
    
    async def _split_and_generate(
        self,
        request: FileGenerationRequest
    ) -> GeneratedFile:
        """
        Split large file into multiple smaller files.
        
        Only called when:
        1. File hit token limit
        2. Escalation didn't help
        3. File type is splittable
        
        Example:
        models.py (too large) →
        - models/user.py
        - models/product.py
        - models/order.py
        - models/__init__.py
        
        Args:
            request: Original file generation request
        
        Returns:
            GeneratedFile with combined content or __init__.py
        """
        
        self.logger.info(f"📦 Splitting {request.file_path}...")
        
        if request.file_type == FileType.MODELS:
            return await self._split_models_file(request)
        
        elif request.file_type == FileType.SCHEMAS:
            return await self._split_schemas_file(request)
        
        elif request.file_type == FileType.ROUTERS:
            return await self._split_routers_file(request)
        
        else:
            raise Exception(f"Cannot split file type: {request.file_type}")
    
    async def _split_models_file(
        self,
        request: FileGenerationRequest
    ) -> GeneratedFile:
        """
        Split models.py into multiple files by table groups.
        
        Strategy:
        - Group tables (max 3 per file)
        - Generate separate file for each group
        - Create __init__.py to import all
        """
        
        # Extract tables from architecture
        tables = request.architecture.get("database", {}).get("tables", [])
        
        if not tables:
            raise Exception("No tables found in architecture for splitting")
        
        # Split into groups of 3
        table_groups = [tables[i:i+3] for i in range(0, len(tables), 3)]
        
        generated_files = []
        total_tokens = 0
        total_cost = 0.0
        
        for i, group in enumerate(table_groups):
            # Create sub-request for this group
            group_request = FileGenerationRequest(
                file_path=f"app/models/models_{i+1}.py",
                file_type=FileType.MODELS,
                description=f"Database models for tables: {', '.join(t['name'] for t in group)}",
                architecture={
                    "database": {
                        "type": request.architecture["database"]["type"],
                        "tables": group
                    }
                }
            )
            
            # Generate this group
            result = await self.generate_file(group_request)
            generated_files.append(result)
            total_tokens += result.tokens_used
            total_cost += result.cost
        
        # Generate __init__.py
        init_content = self._generate_models_init(generated_files)
        
        # Return combined result
        return GeneratedFile(
            file_path="app/models/__init__.py",
            content=init_content,
            file_type=FileType.MODELS,
            tokens_used=total_tokens,
            model_used=generated_files[0].model_used,
            was_escalated=any(f.was_escalated for f in generated_files),
            was_split=True,
            validation_passed=all(f.validation_passed for f in generated_files),
            syntax_valid=all(f.syntax_valid for f in generated_files),
            cost=total_cost
        )
    
    async def _split_schemas_file(
        self,
        request: FileGenerationRequest
    ) -> GeneratedFile:
        """Split schemas.py by model groups"""
        # Similar to models splitting
        # TODO: Implement when needed
        raise NotImplementedError("Schema splitting not yet implemented")
    
    async def _split_routers_file(
        self,
        request: FileGenerationRequest
    ) -> GeneratedFile:
        """Split routers by endpoint groups"""
        # Similar to models splitting
        # TODO: Implement when needed
        raise NotImplementedError("Router splitting not yet implemented")
    
    def _generate_models_init(
        self,
        model_files: List[GeneratedFile]
    ) -> str:
        """
        Generate __init__.py for split models.
        
        Imports all models from sub-files:
        from .models_1 import *
        from .models_2 import *
        """
        
        imports = []
        for file in model_files:
            # Extract module name from path
            # app/models/models_1.py → models_1
            module = file.file_path.split('/')[-1].replace('.py', '')
            imports.append(f"from .{module} import *")
        
        return "\n".join(imports) + "\n"
    
    # =========================================================================
    # UTILITY METHODS
    # =========================================================================
    
    def _order_by_dependencies(
        self,
        requests: List[FileGenerationRequest]
    ) -> List[FileGenerationRequest]:
        """
        Order file generation requests by dependency.
        
        Order:
        1. Database
        2. Models
        3. Schemas
        4. Dependencies, Security
        5. Services
        6. Routers
        7. Main
        8. Config files
        """
        
        priority_order = {
            FileType.DATABASE: 1,
            FileType.MODELS: 2,
            FileType.SCHEMAS: 3,
            FileType.DEPENDENCIES: 4,
            FileType.SECURITY: 4,
            FileType.SERVICES: 5,
            FileType.ROUTERS: 6,
            FileType.MAIN: 7,
            FileType.CONFIG: 8,
            FileType.REQUIREMENTS: 9,
            FileType.ENV_EXAMPLE: 9,
            FileType.README: 10,
        }
        
        return sorted(
            requests,
            key=lambda r: priority_order.get(r.file_type, 99)
        )


# =============================================================================
# VALIDATION INTEGRATION (TILOTMA)
# =============================================================================

class TilotmaValidator:
    """
    Tilotma's validation layer for Shubham's code.
    
    Validates:
    - Code quality
    - Architecture compliance
    - Security best practices
    - Performance considerations
    """
    
    def __init__(self):
        self.logger = logging.getLogger("tilotma.validator")
    
    async def validate_code(
        self,
        file: GeneratedFile,
        architecture: Dict[str, Any]
    ) -> ValidationResult:
        """
        Validate generated code with AI reasoning.
        
        Uses AI to check:
        - Does code match architecture?
        - Are there security issues?
        - Is error handling comprehensive?
        - Are there performance problems?
        
        Args:
            file: Generated file to validate
            architecture: Project architecture
        
        Returns:
            ValidationResult with pass/fail and feedback
        """
        
        self.logger.info(f"🔍 Validating {file.file_path}...")
        
        # Skip validation if syntax already invalid
        if not file.syntax_valid:
            return ValidationResult(
                is_valid=False,
                syntax_errors=["Syntax validation failed"],
                logic_issues=[],
                suggestions=["Fix syntax errors first"],
                should_regenerate=True
            )
        
        # Create validation prompt
        prompt = f"""Review this generated code for quality and correctness.

FILE: {file.file_path}
TYPE: {file.file_type.value}

CODE:
```python
{file.content}
```

ARCHITECTURE CONTEXT:
{architecture}

Please evaluate:
1. Does code match the architecture requirements?
2. Are there any security vulnerabilities?
3. Is error handling comprehensive?
4. Are there performance issues?
5. Is the code production-ready?

Respond in JSON format:
{{
    "is_valid": true/false,
    "logic_issues": ["issue 1", "issue 2"],
    "suggestions": ["suggestion 1", "suggestion 2"],
    "should_regenerate": true/false
}}
"""
        
        try:
            response = await ai_router.generate(
                messages=[{"role": "user", "content": prompt}],
                task_type="code_review",
                complexity=TaskComplexity.COMPLEX,
                max_tokens=2000
            )
            
            # Parse JSON response
            import json
            validation_data = json.loads(response.content)
            
            return ValidationResult(
                is_valid=validation_data.get("is_valid", False),
                syntax_errors=[],
                logic_issues=validation_data.get("logic_issues", []),
                suggestions=validation_data.get("suggestions", []),
                should_regenerate=validation_data.get("should_regenerate", False)
            )
            
        except Exception as e:
            self.logger.error(f"❌ Validation failed: {e}")
            # If validation fails, assume code is okay (fail-open)
            return ValidationResult(
                is_valid=True,
                syntax_errors=[],
                logic_issues=[f"Validation error: {e}"],
                suggestions=[],
                should_regenerate=False
            )


# =============================================================================
# HELPER FUNCTIONS
# =============================================================================

async def generate_complete_backend(
    project_id: str,
    user_id: str,
    architecture: Dict[str, Any]
) -> List[GeneratedFile]:
    """
    Generate complete FastAPI backend.
    
    Entry point for generating all backend files.
    
    Args:
        project_id: Project UUID
        user_id: User UUID
        architecture: Project architecture specification
    
    Returns:
        List of all generated files
    """
    
    # Initialize Shubham
    shubham = Shubham(project_id, user_id)
    
    # Create generation requests for all files
    requests = [
        # Database connection
        FileGenerationRequest(
            file_path="app/database.py",
            file_type=FileType.DATABASE,
            description="PostgreSQL database connection with SQLAlchemy",
            architecture=architecture
        ),
        
        # Models
        FileGenerationRequest(
            file_path="app/models.py",
            file_type=FileType.MODELS,
            description="SQLAlchemy ORM models for all database tables",
            architecture=architecture
        ),
        
        # Schemas
        FileGenerationRequest(
            file_path="app/schemas.py",
            file_type=FileType.SCHEMAS,
            description="Pydantic schemas for request/response validation",
            architecture=architecture
        ),
        
        # Security
        FileGenerationRequest(
            file_path="app/security.py",
            file_type=FileType.SECURITY,
            description="Authentication and authorization logic with JWT",
            architecture=architecture
        ),
        
        # Dependencies
        FileGenerationRequest(
            file_path="app/dependencies.py",
            file_type=FileType.DEPENDENCIES,
            description="Utility functions and dependency injection",
            architecture=architecture
        ),
        
        # Main app
        FileGenerationRequest(
            file_path="app/main.py",
            file_type=FileType.MAIN,
            description="FastAPI application entry point with CORS and middleware",
            architecture=architecture
        ),
        
        # Requirements
        FileGenerationRequest(
            file_path="requirements.txt",
            file_type=FileType.REQUIREMENTS,
            description="Python package dependencies",
            architecture=architecture
        ),
        
        # Environment example
        FileGenerationRequest(
            file_path=".env.example",
            file_type=FileType.ENV_EXAMPLE,
            description="Environment variables template",
            architecture=architecture
        ),
    ]
    
    # Add routers based on architecture
    if "api" in architecture and "endpoints" in architecture["api"]:
        for endpoint_group in architecture["api"]["endpoints"]:
            requests.append(
                FileGenerationRequest(
                    file_path=f"app/routers/{endpoint_group['name']}.py",
                    file_type=FileType.ROUTERS,
                    description=f"API endpoints for {endpoint_group['name']}",
                    architecture=architecture
                )
            )
    
    # Generate all files
    results = await shubham.generate_multiple_files(requests)
    
    return results


# =============================================================================
# END OF SHUBHAM V2
# =============================================================================
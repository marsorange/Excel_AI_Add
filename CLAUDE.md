# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

Excel AI is an Office Add-in that provides intelligent Excel assistance through AI-powered natural language processing. It combines a React-based frontend with a FastAPI backend to deliver formula generation, explanation, optimization, and financial Excel operations.

## Development Commands

### Backend Development
```bash
cd backend
pip install -r requirements.txt
python main.py                    # Start FastAPI server (port 8000)
alembic upgrade head              # Initialize database
```

### Frontend Development
```bash
npm install                       # Install dependencies
npm run dev-server                # Start HTTPS dev server (port 3000)
npm run dev-server-http           # Start HTTP dev server for browser testing
npm run build                     # Production build
npm run lint                      # Lint code
npm run lint:fix                  # Fix linting issues
npm run start                     # Start Office Add-in debugging
npm run stop                      # Stop Office Add-in debugging
```

### Office Add-in Commands
```bash
npm run validate                  # Validate manifest.xml
npm run browser-test              # Browser testing mode
npm run signin                    # Sign in to Microsoft 365
npm run signout                   # Sign out from Microsoft 365
```

## Architecture

### Backend (FastAPI)
- **main.py**: Core API with authentication, LLM integration, and Excel operation generation
- **llm_config.py**: LLM provider configuration (supports Qwen/DashScope API)
- **models.py**: SQLAlchemy database models for users and authentication
- **schemas.py**: Pydantic schemas for request/response validation
- **excel_tools.py**: Excel-specific operations and data processing
- **database.py**: Database connection and session management
- **crud.py**: Database operations and user management

### Frontend (React + TypeScript)
- **src/taskpane/components/AgentChat.tsx**: Main AI chat interface with Excel operation execution
- **src/taskpane/components/App.tsx**: Main application component with authentication
- **src/config/api.ts**: API endpoint configuration
- **manifest.xml**: Office Add-in manifest defining permissions and UI

### Key Features
1. **AI Agent Chat**: Natural language interface that generates executable Excel operations
2. **Formula Management**: Generate, explain, optimize, and diagnose Excel formulas
3. **Financial Operations**: Specialized templates for voucher entry, reconciliation, data cleaning, and financial reports
4. **Excel Integration**: Direct Excel.js integration for real-time spreadsheet operations

## Environment Configuration

### Required Environment Variables
```bash
# Backend (.env file)
DATABASE_URL=sqlite:///./excel_ai.db
DASHSCOPE_API_KEY=your-qwen-api-key
DASHSCOPE_API_URL=https://dashscope.aliyuncs.com/compatible-mode/v1/chat/completions
QWEN_MODEL=qwen-turbo-latest
SECRET_KEY=your-secret-key
HOST=0.0.0.0
PORT=8000
DEBUG=true
```

### LLM Configuration Priority
1. **Qwen API** (DashScope): Primary LLM provider with `DASHSCOPE_API_KEY`
2. **DeepSeek API**: Fallback with `DEEPSEEK_API_KEY`  
3. **OpenAI API**: Final fallback with `OPENAI_API_KEY`

### HTTPS Development
The project requires HTTPS for Office Add-in development:
- Backend automatically detects and uses SSL certificates from `~/.office-addin-dev-certs/`
- Frontend uses `office-addin-dev-certs` for HTTPS development server
- Use `npm run dev-server-http` for HTTP browser testing

## Development Workflow

1. **Start Backend**: `cd backend && python main.py`
2. **Start Frontend**: `npm run dev-server`
3. **Debug Add-in**: `npm run start` (sideloads add-in in Excel)
4. **Test Changes**: Frontend hot-reloads, backend restarts with file changes

## Key Integration Points

### Agent Chat Flow
1. User inputs natural language request
2. Frontend captures current Excel data as markdown table
3. Backend processes request through LLM with Excel context
4. LLM generates response + executable Excel operations
5. Frontend displays response and allows operation execution

### Excel Operation Execution
- Operations are generated as JavaScript code using Excel.js API
- Frontend validates code security before execution
- Operations execute directly in user's Excel session
- Supports financial templates, data manipulation, and charting

### Authentication
- JWT-based authentication with 30-minute token expiration
- User registration with password validation (8+ chars, must contain letters)
- Secure password hashing with bcrypt

## Database Schema
- SQLite database with Alembic migrations
- Users table with email/password authentication
- Agent states and error logs for debugging

## Testing and Debugging
- Use `browser-test.html` for frontend testing without Office
- Backend includes detailed error logging and validation
- Frontend shows operation execution status and error messages
- Check `backend.log` for detailed API operation logs
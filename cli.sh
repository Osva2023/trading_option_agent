#!/usr/bin/env bash
# Makefile-style helper script for common trading agent tasks

# Colors for output
GREEN='\033[0;32m'
BLUE='\033[0;34m'
RED='\033[0;31m'
NC='\033[0m' # No Color

echo_header() {
    echo -e "${BLUE}========================================${NC}"
    echo -e "${BLUE}$1${NC}"
    echo -e "${BLUE}========================================${NC}"
}

echo_success() {
    echo -e "${GREEN}✓ $1${NC}"
}

echo_error() {
    echo -e "${RED}✗ $1${NC}"
}

# Change to project directory
cd "$(dirname "$0")"

case "${1:-help}" in
    help)
        echo_header "Trading Agent - CLI Commands"
        echo ""
        echo "Available commands:"
        echo ""
        echo "  ./cli.sh setup              Setup virtual environment and install dependencies"
                echo "  ./cli.sh test               Run full test suite (single command)"
                echo "  ./cli.sh test-manual        Run manual testing suite only"
        echo "  ./cli.sh run                Run agent (TEST_MODE must be set)"
        echo "  ./cli.sh run-prod           Run agent in production mode (respects market hours)"
        echo "  ./cli.sh logs               View agent logs"
        echo "  ./cli.sh docker-build       Build Docker image"
        echo "  ./cli.sh docker-run         Run agent in Docker"
        echo "  ./cli.sh docker-stop        Stop Docker container"
        echo "  ./cli.sh status             Show Docker container status"
        echo ""
        ;;
        
    setup)
        echo_header "Setting up environment"
        if [ ! -d "venv" ]; then
            python3 -m venv venv
            echo_success "Virtual environment created"
        fi
        
        source venv/bin/activate
        pip install -r requirements.txt > /dev/null 2>&1
        pip install python-dotenv > /dev/null 2>&1
        echo_success "Dependencies installed"
        echo "Virtual environment ready. Run 'source venv/bin/activate' to activate"
        ;;
        
    test)
        echo_header "Running Full Test Suite"
        source venv/bin/activate 2>/dev/null || {
            echo_error "Virtual environment not activated. Run './cli.sh setup' first"
            exit 1
        }
        ./venv/bin/python tests/test_basic.py && \
        ./venv/bin/python tests/test_imports.py && \
        ./venv/bin/python tests/test_agent_run.py && \
        ./venv/bin/python tests/test_manual.py
        ;;
        
    test-manual)
        echo_header "Running Manual Test Suite"
        source venv/bin/activate 2>/dev/null || {
            echo_error "Virtual environment not activated. Run './cli.sh setup' first"
            exit 1
        }
        ./venv/bin/python tests/test_manual.py
        ;;
        
    run)
        echo_header "Running Trading Agent (TEST_MODE)"
        source venv/bin/activate 2>/dev/null || exit 1
        echo_success "Starting agent with TEST_MODE enabled..."
        echo "(Press Ctrl+C to stop)"
        echo ""
        ./venv/bin/python run.py
        ;;
        
    run-prod)
        echo_header "Running Trading Agent (PRODUCTION)"
        source venv/bin/activate 2>/dev/null || exit 1
        
        # Check if TEST_MODE is False
        if grep -q "TEST_MODE=True" .env 2>/dev/null; then
            echo_error "TEST_MODE=True in .env. Production mode requires TEST_MODE=False"
            echo "Set TEST_MODE=False in .env to run production mode"
            exit 1
        fi
        
        echo_success "Starting agent in production mode..."
        echo "(Only runs during market hours: 9:30-10:30, 12:00-13:00, 15:00-16:00 ET)"
        echo "(Press Ctrl+C to stop)"
        echo ""
        ./venv/bin/python run.py
        ;;
        
    logs)
        echo_header "Agent Logs"
        if [ -f "data/logs/agent.log" ]; then
            tail -f data/logs/agent.log
        else
            echo_error "No logs found. Run the agent first."
        fi
        ;;
        
    docker-build)
        echo_header "Building Docker Image"
        docker build -f docker/Dockerfile -t trading-agent:latest .
        echo_success "Docker image built"
        ;;
        
    docker-run)
        echo_header "Running in Docker"
        
        # Check if image exists
        if ! docker image inspect trading-agent:latest > /dev/null 2>&1; then
            echo "Building Docker image first..."
            docker build -f docker/Dockerfile -t trading-agent:latest .
        fi
        
        # Check if container is already running
        if docker ps | grep -q trading-agent; then
            echo_error "Container already running. Stop it with './cli.sh docker-stop'"
            exit 1
        fi
        
        echo_success "Starting Docker container..."
        docker-compose -f docker/docker-compose.yml up -d
        echo "Container started. View logs with: docker logs -f trading-agent"
        echo "Dashboard available at: http://localhost:5001"
        ;;
        
    docker-stop)
        echo_header "Stopping Docker Container"
        docker-compose -f docker/docker-compose.yml down
        echo_success "Container stopped"
        ;;
        
    status)
        echo_header "Status"
        if docker ps | grep -q trading-agent; then
            echo_success "Docker container is running"
            docker ps --filter "name=trading-agent"
            echo ""
            echo "Recent logs:"
            docker logs --tail 5 trading-agent
        else
            echo_error "Docker container is not running"
        fi
        ;;
        
    *)
        echo_error "Unknown command: $1"
        echo "Run './cli.sh help' for available commands"
        exit 1
        ;;
esac

#!/bin/bash

# SecureAI - View Structured Logs
# This script provides a nice formatted view of structured JSON logs

LOG_FILE="logs/structured-backend.log"

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
MAGENTA='\033[0;35m'
CYAN='\033[0;36m'
WHITE='\033[1;37m'
NC='\033[0m' # No Color

# Check if log file exists
if [ ! -f "$LOG_FILE" ]; then
    echo "❌ Log file not found: $LOG_FILE"
    exit 1
fi

# Function to format and display logs
format_log() {
    echo ""
    echo -e "${CYAN}════════════════════════════════════════════════════════${NC}"
    echo -e "${WHITE}  SecureAI Structured Logs Viewer${NC}"
    echo -e "${CYAN}════════════════════════════════════════════════════════${NC}"
    echo ""
    
    # Parse and display each JSON log line
    while IFS= read -r line; do
        # Extract fields using jq if available, otherwise use basic parsing
        if command -v jq &> /dev/null; then
            timestamp=$(echo "$line" | jq -r '.timestamp // empty')
            level=$(echo "$line" | jq -r '.level // empty')
            step=$(echo "$line" | jq -r '.step // empty')
            session_id=$(echo "$line" | jq -r '.data.session_id // empty')
            user_role=$(echo "$line" | jq -r '.data.user_role // empty')
            
            # Color based on level
            case "$level" in
                "ERROR")
                    level_color=$RED
                    ;;
                "WARNING")
                    level_color=$YELLOW
                    ;;
                "INFO")
                    level_color=$GREEN
                    ;;
                *)
                    level_color=$WHITE
                    ;;
            esac
            
            # Display formatted log
            echo -e "${BLUE}[$timestamp]${NC} ${level_color}$level${NC} ${MAGENTA}$step${NC}"
            echo -e "  ${YELLOW}Session:${NC} $session_id | ${YELLOW}Role:${NC} $user_role"
            
            # Pretty print the entire JSON with colors
            echo "$line" | jq -C '.' 2>/dev/null || echo "$line"
            echo ""
        else
            # Fallback: just print the raw JSON
            echo "$line" | python3 -m json.tool 2>/dev/null || echo "$line"
            echo ""
        fi
    done < "$LOG_FILE"
}

# Function to tail logs in real-time
tail_logs() {
    echo ""
    echo -e "${CYAN}════════════════════════════════════════════════════════${NC}"
    echo -e "${WHITE}  Real-time Structured Logs (Press Ctrl+C to stop)${NC}"
    echo -e "${CYAN}════════════════════════════════════════════════════════${NC}"
    echo ""
    
    tail -f "$LOG_FILE" | while IFS= read -r line; do
        if command -v jq &> /dev/null; then
            timestamp=$(echo "$line" | jq -r '.timestamp // empty')
            level=$(echo "$line" | jq -r '.level // empty')
            step=$(echo "$line" | jq -r '.step // empty')
            
            # Color based on level
            case "$level" in
                "ERROR")
                    level_color=$RED
                    ;;
                "WARNING")
                    level_color=$YELLOW
                    ;;
                "INFO")
                    level_color=$GREEN
                    ;;
                *)
                    level_color=$WHITE
                    ;;
            esac
            
            echo -e "${BLUE}[$timestamp]${NC} ${level_color}$level${NC} ${MAGENTA}$step${NC}"
            echo "$line" | jq -C '.' 2>/dev/null || echo "$line"
            echo ""
        else
            echo "$line" | python3 -m json.tool 2>/dev/null || echo "$line"
            echo ""
        fi
    done
}

# Function to filter logs by session
filter_by_session() {
    local session_id=$1
    echo ""
    echo -e "${CYAN}════════════════════════════════════════════════════════${NC}"
    echo -e "${WHITE}  Logs for Session: $session_id${NC}"
    echo -e "${CYAN}════════════════════════════════════════════════════════${NC}"
    echo ""
    
    grep "\"session_id\": \"$session_id\"" "$LOG_FILE" | while IFS= read -r line; do
        if command -v jq &> /dev/null; then
            echo "$line" | jq -C '.'
        else
            echo "$line" | python3 -m json.tool
        fi
        echo ""
    done
}

# Function to show statistics
show_stats() {
    echo ""
    echo -e "${CYAN}════════════════════════════════════════════════════════${NC}"
    echo -e "${WHITE}  Log Statistics${NC}"
    echo -e "${CYAN}════════════════════════════════════════════════════════${NC}"
    echo ""
    
    if command -v jq &> /dev/null; then
        echo -e "${YELLOW}Total log entries:${NC}"
        wc -l < "$LOG_FILE"
        echo ""
        
        echo -e "${YELLOW}Entries by step:${NC}"
        jq -r '.step' "$LOG_FILE" | sort | uniq -c | sort -rn
        echo ""
        
        echo -e "${YELLOW}Entries by user role:${NC}"
        jq -r '.data.user_role' "$LOG_FILE" | sort | uniq -c | sort -rn
        echo ""
        
        echo -e "${YELLOW}Unique sessions:${NC}"
        jq -r '.data.session_id' "$LOG_FILE" | sort -u | wc -l
        echo ""
    else
        echo "Install 'jq' for detailed statistics"
        echo ""
        echo -e "${YELLOW}Total log entries:${NC}"
        wc -l < "$LOG_FILE"
        echo ""
    fi
}

# Main menu
case "${1:-view}" in
    "view"|"")
        format_log
        ;;
    "tail"|"follow"|"-f")
        tail_logs
        ;;
    "session"|"-s")
        if [ -z "$2" ]; then
            echo "Usage: $0 session <session_id>"
            exit 1
        fi
        filter_by_session "$2"
        ;;
    "stats"|"statistics")
        show_stats
        ;;
    "help"|"-h"|"--help")
        echo "Usage: $0 [command] [options]"
        echo ""
        echo "Commands:"
        echo "  view              View all structured logs (default)"
        echo "  tail, follow, -f  Follow logs in real-time"
        echo "  session, -s <id>  Filter logs by session ID"
        echo "  stats, statistics Show log statistics"
        echo "  help, -h, --help  Show this help message"
        echo ""
        echo "Examples:"
        echo "  $0                          # View all logs"
        echo "  $0 tail                     # Follow logs in real-time"
        echo "  $0 session default          # Show logs for session 'default'"
        echo "  $0 stats                    # Show statistics"
        echo ""
        ;;
    *)
        echo "Unknown command: $1"
        echo "Run '$0 help' for usage information"
        exit 1
        ;;
esac


#!/bin/bash

# Colors for output
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo -e "${YELLOW}Cache Timing Experiment Runner${NC}"
echo "==============================="

# Check if files exist
echo -e "\n${YELLOW}Checking for required files...${NC}"
if [ ! -f "cache_timing.c" ]; then
    echo -e "${RED}Error: cache_timing.c not found${NC}"
    exit 1
fi

# Check for Python and matplotlib
echo -e "\n${YELLOW}Checking for Python...${NC}"
if command -v python3 &>/dev/null; then
    PYTHON="python3"
elif command -v python &>/dev/null; then
    PYTHON="python"
else
    echo -e "${RED}Python not found. Will skip visualization step.${NC}"
    PYTHON=""
fi

# Compile the C program
echo -e "\n${YELLOW}Compiling cache_timing.c...${NC}"
gcc -o cache_timing cache_timing.c -march=native

if [ $? -ne 0 ]; then
    echo -e "${RED}Compilation failed${NC}"
    exit 1
else
    echo -e "${GREEN}Compilation successful${NC}"
fi

# Run the C program
echo -e "\n${YELLOW}Running cache timing experiment...${NC}"
./cache_timing

if [ $? -ne 0 ]; then
    echo -e "${RED}Experiment failed${NC}"
    exit 1
else
    echo -e "${GREEN}Experiment completed successfully${NC}"
fi

# Check if CSV was created
if [ ! -f "cache_timing_results.csv" ]; then
    echo -e "${RED}Error: No results file was generated${NC}"
    exit 1
fi

# Run the analysis
if [ ! -z "$PYTHON" ]; then
    echo -e "\n${YELLOW}Running analysis...${NC}"

    # Determine which script to use based on matplotlib availability
    # because in some environments, matplotlib may not be available
    # even if Python is installed.
    if $PYTHON -c "import matplotlib" 2>/dev/null; then
        echo "Matplotlib is available, using viz-plt.py"
        $PYTHON viz-plt.py
    else
        echo "Matplotlib is not available, using viz.py"
        $PYTHON viz.py
    fi

    if [ $? -ne 0 ]; then
        echo -e "${RED}Analysis failed${NC}"
    else
        echo -e "${GREEN}Analysis completed successfully${NC}"
    fi
else
    echo -e "\n${RED}Skipping analysis step (Python not available)${NC}"
fi

echo -e "\n${GREEN}Experiment complete!${NC}"
echo "Results are in:"
echo "- cache_timing_results.csv (raw data)"
echo "- cache_timing_analysis.txt (statistics)"

# Check if plots directory exists
if [ -d "plots" ]; then
    echo "- plots/ directory (visualizations)"
fi

echo -e "\n${YELLOW}To view the text analysis:${NC} cat cache_timing_analysis.txt"

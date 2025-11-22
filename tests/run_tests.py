#!/bin/bash
# CargoOpt Test Runner Script

echo "🧪 CargoOpt Test Suite"
echo "====================="

# Colors
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Parse arguments
RUN_SLOW=false
RUN_INTEGRATION=false
COVERAGE=false

while [[ $# -gt 0 ]]; do
    case $1 in
        --slow) RUN_SLOW=true; shift ;;
        --integration) RUN_INTEGRATION=true; shift ;;
        --coverage) COVERAGE=true; shift ;;
        *) echo "Unknown option: $1"; exit 1 ;;
    esac
done

# Build pytest command
PYTEST_CMD="pytest -v"

# Add markers
if [ "$RUN_SLOW" = true ]; then
    PYTEST_CMD="$PYTEST_CMD --run-slow"
else
    PYTEST_CMD="$PYTEST_CMD -m 'not slow'"
fi

if [ "$RUN_INTEGRATION" = true ]; then
    PYTEST_CMD="$PYTEST_CMD --run-integration"
fi

# Add coverage
if [ "$COVERAGE" = true ]; then
    PYTEST_CMD="$PYTEST_CMD --cov=backend --cov-report=html --cov-report=term"
fi

# Run tests
echo -e "${YELLOW}Running: $PYTEST_CMD${NC}"
echo ""

eval $PYTEST_CMD
TEST_RESULT=$?

# Report results
echo ""
if [ $TEST_RESULT -eq 0 ]; then
    echo -e "${GREEN}✅ All tests passed!${NC}"
else
    echo -e "${RED}❌ Some tests failed${NC}"
fi

if [ "$COVERAGE" = true ]; then
    echo ""
    echo -e "${YELLOW}📊 Coverage report generated: htmlcov/index.html${NC}"
fi

exit $TEST_RESULT
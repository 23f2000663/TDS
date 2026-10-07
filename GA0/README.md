$env:AIPIPE_TOKEN="eyJhbGciOiJIUzI1NiJ9.eyJlbWFpbCI6IjIzZjIwMDA2NjNAZHMuc3R1ZHkuaWl0bS5hYy5pbiIsImlhdCI6MTc5MTMwMzcxMSwiaXNzIjoiaHR0cHM6Ly9haXBpcGUub3JnIiwiYXVkIjoiYWlwaXBlLWFwaSIsImV4cCI6MTc5MTkwODUxMX0.D50ODIofRpuGR67NC5DpGWi37FGfBm0EbJVPPnZ1CfE"
python -m uvicorn Q5:app --reload --port 8000
python -m uvicorn Q6:app --reload --port 8001
python -m uvicorn Q7:app --reload --port 8002
python -m uvicorn api.index:app --reload --port 8003
# Internship project
__________________________________________________________________

## How to start
__________________________________________________________________
To start application you could either run main.py file or use command in terminal
```bash
uvicorn app.main:app --reload
```
## Tests
__________________________________________________________________

### Install dependencies
Make sure to install pytest
```bash
pip install pytest
```
To run tests use this command in the terminal
```bash
pytest
```
### Tests overview
test_health_check: checks endpoint's status code and json response body

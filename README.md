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

## Docker
__________________________________________________________________
### initialization
To start project within docker we need to build an image
```bash
docker build -t my_image .
```
Next we need to start container
```bash
docker run -d --name my_container -p 80:80 my_image
```
### Tests
To run tests within docker we need to execute container in bash
```bash
docker exec -it my_container bash
```
After that execute command
```bash
pytest
```
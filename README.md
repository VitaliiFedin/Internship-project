# Internship project
__________________________________________________________________

## How to start
__________________________________________________________________

To start application you need to create .env file with variables (examples in .env.sample).Then either run main.py file or use command in terminal
```bash
uvicorn app.main:app --reload --env-file .env
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
To start project within docker we need to build an image.
```bash
docker build -t my_image .
```
Next we need to start container. Also, we have to pass environment variables(watch .env.sample as a reference)
```bash
docker run --env APP_NAME='main:app' --env RELOAD=True --env HOST='0.0.0.0' --env PORT=80 --env ORIGINS=['1.0.0.0:8080'] --env ALLOW_CREDENTIALS=True --env ALLOW_METHODS=['*'] --env ALLOW
_HEADERS=['*'] -d --name mycontainer -p 80:80  myimage
```
- --env to pass environment variables
- -d detach mode, so you can still use terminal
- -p what port to use
- --name the container's name

### Tests
To run tests within docker we need to execute container in bash
```bash
docker exec -it my_container bash
```
After that execute command
```bash
pytest
```
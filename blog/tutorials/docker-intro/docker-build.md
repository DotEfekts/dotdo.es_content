# Two Weeks to Git Good - Intro to Docker

[Basic Commands](basic-commands)
[Docker Compose](docker-compose)
[**Docker Build**](docker-build)
[Putting it All Together](homelab-creation)
## Docker Build
### Basic Dockerfile
A Dockerfile is how we define instructions for creating a Docker image. To start, we'll create a simple image that will just print `Hello World!` when ran, using a Python script.

1. Create a new directory called `helloworld-build` and create a `hello-world.py` file with the following:

```python
# helloworld-build/hello-world.py
print("Hello World!")
```

2. Create a `Dockerfile` in the directory with the following contents:

```dockerfile
# helloworld-build/Dockerfile
FROM python:3.13-slim
WORKDIR /app
COPY hello-world.py .
ENTRYPOINT ["python", "hello-world.py"]
```

Let's step through this file again to see what each instruction is doing:
- `FROM` The base image to use for our new image. As we're building a Python app, we want to use a Python image.
- `WORKDIR` Change the working directory in the image to the specific location. `WORKDIR` will create the directory if it doesn't already exist.
- `COPY` Copy a file from the host working directory to the image working directory, in this case our `hello-world.py` script. Absolute paths can also be used.
- `ENTRYPOINT` The command to execute in the image when the container is created with `run`.

3. Run the `docker build .` command. This tells Docker to build the `Dockerfile` in the current directory.
4. Once the image is built, find the `Image ID` using `docker image ls`. It will show up as `<none> <none>` for the repository and tag.
5. Run the image with `docker run --rm <Image ID>`.

```
Hello World!
```

As you can see, we've not set a tag for this image, so we need to use the Image ID to run it. 
6. Use `docker image prune` to get rid of the untagged image.
7. Run `docker build . -t my-hello` to recreate the image with a name of `my-hello` and the default tag `latest`.
8. Run the new image with `docker run --rm my-hello`.

Now we've learnt how to use a Dockerfile to build an image, and how to give it a name!
### Building Services
It's all well and good running a little `Hello World!` program, but generally we're going to want to build an image for a longer running service. Let's make a small Python web server to print `Hello World!` in a browser instead.

1. Create a new directory called `helloflask-build` and create the file `app.py` with the following contents:

```python
# helloflask-build/app.py
import os
from flask import Flask

app = Flask(__name__)
hello_target = os.getenv('HELLO_TARGET', "Missing Target")
whoami = os.getuid()

@app.route("/")
def hello_world():
    return f"<p>Hello {hello_target}!</p><p>whoami: {whoami}</p>"
```

2. Add a `requirements.txt` file with our `flask` dependancy:

```python
# helloflask-build/requirements.txt
flask==3.1.1
```

3. Create a `Dockerfile` to build and package our app:

```dockerfile
FROM python:3.13-slim
WORKDIR /app
ENV HELLO_TARGET="World"
COPY requirements.txt .
RUN pip install -r requirements.txt
USER 1000:1000
COPY app.py .
EXPOSE 5000
ENTRYPOINT ["flask", "run", "--host=0.0.0.0"]
```

We looked at some of these instructions before but we can look at the changes made and the new keywords we've used:
- `ENV` Sets an environment variable. This variable will be available in the build file and after the container is created.
- `RUN` Here we execute a command in the image, in this case installing the dependancies specified in `requirements.txt`. We do this step first without copying the main application to allow Docker to cache the requirements layers for when the requirements don't change between builds. If we were to include the whole app, any change made to the application code would invalidate the cache for the requirements layers.
- `USER` Change the user and group ID to use in the image. By default the files and app will be owned and executed by the `root` user without this.
- `EXPOSE` This is more of an information instruction for Docker and people using the image. It tells Docker that this image will have something listening on that port, so if Docker is configured to automatically map ports for the container it knows which ports to use.

4. Build the new image with `docker build . -t flask-hello`.
5. Run the image with `docker run --rm -dp 5050:5000 --name flask-hello flask-hello` and navigate to `http://localhost:5050` to see our new `Hello World!`.
6. Stop the container with `docker stop flask-hello`.
### Building In Compose
Docker Compose also allows us to build an image as part of the services we want to launch. Let's take our Flask Hello World app and put it into a compose file to build and launch automatically.

1. In the `helloflask-build` directory, create a `docker-compose.yml` file with the following:

```yaml
# helloflask-build/docker-compose.yml
services:
  helloworld:
    build: .
    container_name: flask-hello
    environment:
      - HELLO_TARGET=Compose
    user: "1001:1001"
    ports:
      - 5050:5000
```

We've introduced a couple more new settings here.
- `build:` This is the directory for the `Dockerfile` the same as we specify in the `docker build .` command. As we're using the `docker compose` command in the same directory we don't need to specify another folder.
- `environment:` With this we can set or change environment variables in the container. Here we're overriding the `HELLO_TARGET` variable we set in the `Dockerfile` to change it to "Compose".
- `user:` Like `environment`, we're overriding the user specified in the `Dockerfile` to use UID 1001 rather than 1000.

2. Bring the service up with `docker compose up -d` and go to the `http://localhost:5050` page again. You should now see that the page says `Hello Compose!` and tells us the running UID is 1001.
3. Take the service down with `docker compose down`

Next: [Putting it All Together](homelab-creation)
## Basic Commands
### Getting Started

1. Install Docker on your system. [https://docs.docker.com/desktop/](https://docs.docker.com/desktop/)

> Docker desktop includes a GUI however we will not be covering its use. 
> If you are on Windows, please ensure you select the Linux containers option when installing (this should be default).

2. Verify you have a valid installation with `docker run hello-world`. If you are on Linux or Mac, you may need to use `sudo`.
3. Use `docker ps` to show all running containers. This should show an empty list at the moment.
4.  Use `docker ps -a` to show all containers, including stopped containers. The `hello-world` container should show here.
5. Remove the `hello-world` container using `docker rm <Container ID>` or `docker rm <Container Name>`.
### Command Line Containers
Some Docker containers run a command line program when they're created, letting us use various scripts and applications without needing to install them and their dependancies to the main system.

1. Run `docker run --rm -it wernight/funbox` and use some of the functions!

This command runs the `funbox` image, along with some flags to tell the container how to function. The `--rm` flag tells Docker to remove the container when the main program in the image exits, meaning we don't need to run the `docker rm` command. The `-i` flag lets us use the console to interact with the container, it would just exit after printing the menu without this. The `-t` flag provides more advanced features for the console and some of the functions don't quite work right without this.

2. If you find a container freezes and you can't shut it down you can use `docker kill <Container ID>` to force a container to stop. You can find the `Container ID` using `docker ps`
### Long Running Services
Most Docker containers are design to perform long running tasks like hosting a web app or gaming server. Here we'll launch a Super Mario clone that you play in a web browser.

1. Run `docker run -d -p 8600:8080 pengbai/docker-supermario`.

The `-d` flag tells Docker not to attach our console to the output of the container, instead launching it in the background. You can see the container running with the `docker ps` command. The `-p` flag maps a port from the container to the local system, with `8600` being the port that our system is listening on, and `8080` being the port that the application in the container is listening to. We'll talk about container networking later.

2. Try connecting to the game by going to `http://localhost:8600`. If you want to play, use the arrow keys to move and S to jump!

Docker assigns a default name to containers but we can change this to something more memorable. Let's rename the container so we can use the next set of commands more easily. 

3. Get the container ID with `docker ps` then run `docker rename <Container ID> mario`.
4. Stop the container with `docker stop mario`.
5. Refresh the game page. It should no longer connect as the container is not running.
6. Start the container again with `docker start mario` and refresh the game page to check the container successfully started (you may need to give it a second).
7. Stop the container again, then remove it with `docker rm mario`. You need to stop the container first as Docker will not let you remove a running container unless you use the `--force` flag.

You can also assign a name to a container when you use the run command with the `--name` flag. For our Mario container, this would look like `docker run -d -p 8600:8080 --name mario pengbai/docker-supermario` (If you try this out make sure to stop and delete the container before moving on).
### Images
We've now downloaded a few images as we've run these commands. We'll look at all the images we have downloaded and then perform some cleanup to remove ones we don't want to use anymore.

1. Run `docker image ls`. You should see three images: `hello-world`, `wernight/funbox`, and `pengbai/docker-supermario`.

We're finished with `hello-world` and `wernight/funbox` for now. You can remove them or keep them if you want.

3. Use `docker image rm <Full Image Name>` to delete an image from your system. You need to use the full `author-name/image-name` format (`hello-world` does not have an author so just use the name on its own). 

Sometimes you may want to download an image but not run it right away. 

 4. Use `docker image pull python:3.13-slim` to pull the image for Python 3.13.
 5. Run the image using `docker run --rm -it python:3.13-slim`, this should open an interpreter for Python 3.13. Exit the interpreter with `exit()`. Don't delete the Python image just yet.
### Tags
You may notice we specified a version number when downloading the Python image. This is called a "tag" and they're used by image authors to specify a certain branch or features of an image while being able to update the image for that specific tag. The default tag is "latest", which is what's downloaded when no tag is specified.

1. Use `docker image pull python:3.12-slim` to download the Python 3.12 image.
2. Run the image using `docker run --rm -it python:3.12-slim`. You can see the version number in the interpreter is different than before. Exit the 3.12 interpreter and run the 3.13 image again to see the different version numbers.
3. Use `docker image ls`. You should see the two separate Python images.
4. Try running `docker image rm python`. You should see an error message that there is no `python:latest` image, as we did not specify the tag and have not downloaded the Python image with the `latest` tag.
5. Use `docker image rm python:3.12-slim` to delete the 3.12 image.

If the image for a tag is updated, the previous image becomes "dangling". It can still be run by referencing it using its SHA hash, however in most cases we will want to delete old image version.

6. Run `docker pull python@sha256:db26f12821c8a1952702633eac1254280223da76b0082db6a64d8bceae73f149`
7.  Use `docker image ls`. We can see that the image we have just downloaded has \<none\> under the `tag` column. There also an image ID column we can use to make creating a container with the image easier.
8. We can run this image using `docker run --rm -it python@sha256:db26f12821c8a1952702633eac1254280223da76b0082db6a64d8bceae73f149` or `docker run --rm -it <Image ID>`. If you get a warning or are unable to run the image due to an architecture mismatch don't worry, we don't need to use this image as it's just an example. 
9. If we want to tag this image to more easily reference it we can use `docker tag python@sha256:db26f12821c8a1952702633eac1254280223da76b0082db6a64d8bceae73f149 python:my_version` to add a tag and then run the image using `docker run --rm -it python:my_version`
10. We can remove the tag by using the same command to remove an image. If an image has multiple tags you must remove all of them to delete the image entirely. Use `docker image rm python:my_version` to remove the custom tag. Docker will delete the image as this was the only tag referencing it.
11. If we have untagged images, usually a result of pulling the latest version of a tag rather than downloading them manually, Docker lets us delete all untagged images (as long as they're not in use by a container) with `docker image prune`. If you wish to try this, you can download the untagged `python` image again and then run the `prune` command.
## Docker Compose
### Basic Compose File
Let's take our Mario game container and run it in `compose` instead. 

1. Create a directory called `mario-compose` (or whatever else you like) and then create a file in that directory called `docker-compose.yml` (NOT whatever else you like) with the following contents:

```yml
# mario-compose/docker-compose.yml
services:
  mario:
    image: pengbai/docker-supermario
    container_name: mario
    ports:
      - 8600:8080
```

2. Run the compose file using the command `docker compose up` inside the `mario-compose` directory. This will start the container with the terminal attached so you can see all the logging. Stop the container using `Ctrl + C`. 
3. Run the compose file again, this time using the `-d` flag to run it in the background (`docker compose up -d`) then check the service is running at the `http://localhost:8600` address.
4. Bring the container down again using `docker compose down`. This will both stop and delete the container. You've just run your first compose file!
### Dependant Services
Sometimes a container will rely on another container being available, for example an application requiring a database. We can launch both containers using compose, and tell Docker that the application needs the database to function.

1. Create a new directory called `hedgedoc-compose` and then a `docker-compose.yml` file with the following contents:

```yml
# hedgedoc-compose/docker-compose.yml
services:
  doc-database:
    image: postgres:13.4-alpine
    environment:
      - POSTGRES_USER=hedgedoc
      - POSTGRES_PASSWORD=password
      - POSTGRES_DB=hedgedoc
    volumes:
      - database:/var/lib/postgresql/data
    restart: always
  doc-app:
    image: quay.io/hedgedoc/hedgedoc:1.10.3
    environment:
      - CMD_DB_URL=postgres://hedgedoc:password@doc-database:5432/hedgedoc
      - CMD_DOMAIN=localhost
      - CMD_URL_ADDPORT=true
    volumes:
      - uploads:/hedgedoc/public/uploads
    ports:
      - "3000:3000"
    restart: always
    depends_on:
      - doc-database
volumes:
  database:
  uploads:
```
(from https://docs.hedgedoc.org/setup/docker/)

2. Bring the services up with `docker compose up -d`.
3. Check the service is running at `http://localhost:3000`.
4. Inspect the created network using `docker network list`. You should see the `hedgedoc-compose_default` network (or whatever you called your directory).
5. We can see the connected containers using `docker network inspect hedgedoc-compose_default`.
6. Bring the services down again with `docker compose down`.
7. We can use `docker network list` to see the network has been deleted.
8. Run `docker volume list` to see the volumes for the services still remain. These won't be deleted unless you remove them manually using `docker volume rm <Volume Name>`.

Okay there's a lot going on here so lets go through it a bit at a time.
1. `services:` The section where we define the containers to run.
2. `doc-database:` The name of the service in the compose file. The name of the container will be generated from this (generally the directory name + the service name) unless you set the `container_name` property.
3. `image: postgres:13.4-alpine` The image for the container to use.
4. `environment:` The environment variables to set in the container. Postgres will read these to set up the database.
5. `volumes:` The Docker volumes and bind mounts to use for the container. In this case we are creating a volume called `database` and binding it to the `/var/lib/postgresql/data` directory in the container.
6. `restart: always` Always restart this container if it is stopped for any reason (e.g. Postgres crashes).
7. These same options are also configured for the `doc-app` service.
8. `ports:` The ports to bind on the host. 

You may notice Postgres does not have any ports specified. This is because we do not need to expose the database to the external network as we only want the `doc-app` service to have access to it.

10. `depends_on:` Telling Docker this service depends on the `doc-database` to run.
11. `volumes:` Declaring the `database` and `uploads` volumes we want to use for the containers. There are further options you can configure but we won't do this now.

If we look, we can see that the HedgeDoc service is using the `postgres://hedgedoc:password@doc-database:5432/hedgedoc` connection string. Compose will create a new `bridge` network when brought up and attach the created containers to that network rather than the default `bridge` network. This isolates that set of containers from others on the host, and allows the containers to refer to each other by their service name for network connections.
### Traefik Reverse Proxy
Often we'd like to access our docker services using names rather than port, which is where a reverse proxy comes in. If you don't know, a reverse proxy acts as a sort of "front door" for various web services, allowing you to have the reverse proxy listen on the HTTP/HTTPS ports and redirect requests to your services based on a set of defined rules. Today we're going to set up the Traefik reverse proxy to redirect based on the `<service name>.rr.efektion.net` rule. 

> **Note:** Adding a record for a local IP address in public DNS is generally considered bad practice. This record has been setup for your convenience during the workshop and will be removed later. If you have your own domain, you can setup internal DNS for your private IPs, or add your own public record for a private IP. Having a private IP in public DNS is still much safer than exposing any of your services to the internet.

1. Create a new directory called `traefik-compose`.
2. Create a new file called `traefik.yml` in the new directory with the following contents:

```yml
# traefik-compose/traefik.yml
providers:
  docker: {}

api:
  insecure: true
  
entryPoints:
  web:
    address: ":80"
```

3. Create a new compose file in the same directory with the following:

```yaml
# traefik-compose/docker-compose.yml
services:
  traefik:
    image: traefik:v3.4
    ports:
      - "80:80"
      - "8080:8080"
    volumes:
      - ./traefik.yml:/etc/traefik/traefik.yml
      - /var/run/docker.sock:/var/run/docker.sock
  whoami:
    image: traefik/whoami
    labels:
      - "traefik.http.routers.whoami.rule=Host(`whoami.rr.efektion.net`)"
```

4. Bring the services up with the `compose` command.
5. View the `whoami` service by navigating to `http://whoami.rr.efektion.net`.
6. Open the Traefik dashboard by navigating to `http://localhost:8080`.

In the `whoami` page you can see some details of the IPs being used by Dockers internal network, these will look something like `172.18.0.0`. In the Traefik dashboard we can see some details about the services it's detected. On the `whoami` service in the compose file we've set up a label to tell Traefik how to accept traffic to the `whoami` service. You can read more about Traefik rules here: https://doc.traefik.io/traefik/routing/routers/#rule

7.  Go to the HTTP tab in the Traefik dashboard and look at the rules for the difference services.

We've now setup Traefik to accept our requests and forward them to other services, but there are a couple of issues with this setup. We have to manually set each `Host` rule for a service, and we see all running Docker containers within Traefik. Leave Traefik running and go back to the `mario-compose` folder and bring that compose file up. If we go back to the Traefik dashboard, the `mario` service shows up automatically without us having said we want Traefik to handle it. While this isn't an issue with our current configuration as the host it sets by default isn't accessible, when we change Traefik to auto assign our `*.rr.efektion.net` hosts we don't want to accidentally expose any services that we didn't mean to. We can bring our `mario` service back down again now.

8.  Modify the `traefik.yml` config to the following: 

```yaml
# traefik-compose/traefik.yml
providers:
  docker:
    exposedByDefault: false
    defaultRule: "Host(`{{ index .Labels \"com.docker.compose.service\" }}.rr.efektion.net`)"
  file:
    directory: "/etc/traefik/config"

api: {}

entryPoints:
  web:
    address: ":80"
    http:
      middlewares:
        - "compress@file"
```

We've made a few changes here so let's go through it.
-  `exposedByDefault: false` This tells Traefik not to handle a service unless we explicitly tell it to
- `defaultRule: ...` This is where we set our automatic host rule. This rule refers to the service name in the compose file via a Docker label. You can see other labels on your containers by running `docker inspect <Container ID>` and finding the `Labels` section. See https://doc.traefik.io/traefik/providers/docker/#defaultrule for more info.
- `file:` Here we're adding a second provider to extend Traefik's functionality
- `directory: ...` This specifies the location of the files for the new provider. This path will map to our `traefik-compose` director via a new bind mount, and we'll add a new file here in a second.
- `compress@file` Here we're adding a new middleware (which we'll define in our file provider) to enable response compression on Traefik.

> **Note:** Response compression is just general good practice, but you can skip this if you really want to. You can read more about response compression here: https://developer.mozilla.org/en-US/docs/Web/HTTP/Guides/Compression

9. Modify the `docker-compose.yml` file to the following:

```yaml
# traefik-compose/docker-compose.yml
services:
  traefik:
    image: traefik:v3.4
    ports:
      - "80:80"
    volumes:
      - ./traefik.yml:/etc/traefik/traefik.yml
      - ./config:/etc/traefik/config
      - /var/run/docker.sock:/var/run/docker.sock
    labels:
      - "traefik.enable=true"
      - "traefik.http.routers.api.rule=Host(`traefik.rr.efektion.net`)"
      - "traefik.http.routers.api.service=api@internal"
  whoami:
    image: traefik/whoami
    labels:
      - "traefik.enable=true"
```

Now that we've updated our config to not expose services by default, we need to tell Traefik when we want a service to be handled using the `traefik.enable=true` label. If this label is not present Traefik will also ignore any other labels specified on that container. We've also added the `service=api@internal` label here to tell Traefik that we want the host we've specified to refer to the internal dashboard service, and not the reverse proxy itself.

10. Create the `config` directory within the `traefik-compose` folder and add a file called `middlewares.yml` with the following contents:

```yaml
# traefik-compose/config/middlewares.yml
http:
  middlewares:
    compress:
      compress: {}
```

11. Update the Traefik services by running `docker compose up -d` in the `traefik-compose` directory. There's no need to run `comopse down` as Docker will detect the changes to `docker-compose.yml` and automatically recreate the container.

You should now be able to access the Traefik dashboard at `http://traefik.rr.efektion.net` and still have access to `http://whoami.rr.efektion.net`. The Traefik dashboard is a useful tool to diagnose issues when you start adding extra rules or middlewares.

> **HTTPS:** Adding HTTPS support can be done fairly easily via Let's Encrypt assuming you have a domain name. An appendix will be at the end to show you how to do this using a DNS ACME challenge. This will allow you to use HTTPS certificates internally without requiring you to port forward to your Traefik service.
## Docker Build
## Basic Dockerfile
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
## Putting It All Together
At this point we've learnt enough to put together a basic service stack that you can then build on. We're going to be putting this together in a modular way, so you can pick and choose which of the following you want to add to your stack. There are two paths you can follow here. If you like the idea of using Portainer to manage your Docker services, follow the instructions under the **Using Portainer** section. If you'd prefer to just use `docker` commands to manage your services, follow the instructions under the **Using Docker Commands** section.

> If you do not own a domain name you will not be able to continue using domains for Traefik after the workshop. You should modify the compose configurations to remove the Traefik service and the Traefik labels on the other containers, and use the `ports:` setting in the compose files instead to open those services to your local network.
### Using Portainer
Before we start, ensure you've stopped and deleted any containers or compose stacks from the previous tasks. We'll need a directory to store config and data files for our services. Create a new directory and note the path.
#### Portainer Setup
To start, we'll create our Portainer instance so we can manage all of our other services using the Portainer UI. We'll add Portainer to Traefik once we set it up, but we also want to leave a port for Portainer open for access if something goes wrong with Traefik.

1. Create a data volume using `docker volume create portainer_data`
2. Bring the Portainer service up with `docker run -d -p 9443:9443 --name portainer --restart=always -v /var/run/docker.sock:/var/run/docker.sock -v portainer_data:/data portainer/portainer-ce:lts --label traefik.enable=true`

This will: Create a container with the `portainer/portainer-ce` image, open the `9443` port so we can access the web UI, ensure the container restarts if it is stopped, map the Docker socket into the container so Portainer can manage Docker, and map the `portainer_data` volume to the `/data` directory in the container.

3. Navigate to `https://localhost:9443`. You will receive a warning that the SSL certificate is self signed. Accept this warning, and proceed to the Portainer setup screen.
4. Setup a username and password of your choice and we're ready to go!
#### Watchtower Setup
Watchtower is service that will automatically update containers for us without intervention. This can cause issues sometimes if an update includes a breaking change, so we'll add a filter to Watchtower so it only updates particular services.

1. If you haven't already, select the `local` environment in Portainer to view the dashboard for the local Docker instance

> You can use Portainer to manage remote Docker hosts as well, providing a central location for you to easily manage multiple servers.

2. Open the **Stacks** page in the local environment, and create a new stack.
3. Name the stack whatever you'd like (e.g. `watchtower-stack`) and use the following compose file:

```yaml
# Watchtower Compose Stack
services:
  watchtower:
    image: beatkind/watchtower
    environment:
      - WATCHTOWER_LABEL_ENABLE=true
    volumes:
      - /var/run/docker.sock:/var/run/docker.sock
```

4. Click **Deploy the stack** to bring the compose stack up. This may take a short while as the `watchtower` image is downloaded.

Watchtower will now run a daily check and update any containers with updated images. As we've specified the `WATCHTOWER_LABEL_ENABLE=true` environment variable, we'll need to add the `com.centurylinklabs.watchtower.enable=true` label to any containers we want Watchtower to update.
### Hello World Setup
Here we'll add our Flask Hello World app to our services. 
#### Traefik Setup
Now we'll add our reverse proxy to access everything. We'll need to configure some rules to access Portainer as well, as we didn't add any Traefik labels to its container.

1. Create a new folder called `traefik` in your service data directory.
2. Add a `traefik.yml` file with the following configuration (the same config we used before):

```yaml
# traefik/traefik.yml
providers:
  docker:
    exposedByDefault: false
    defaultRule: "Host(`{{ index .Labels \"com.docker.compose.service\" }}.rr.efektion.net`)"
  file:
    directory: "/etc/traefik/config"

api: {}

entryPoints:
  web:
    address: ":80"
    http:
      middlewares:
        - "compress@file"
```

3. Create the `config` directory within Traefik and add our `middlewares.yml` file with the compress middleware:

```yaml
# traefik/config/middlewares.yml
http:
  middlewares:
    compress:
      compress: {}
```

5. Add another file in the `config` folder called `services.yml` where we'll define our Portainer service for Traefik:

```yaml
# traefik/config/`services.yml
http:
  services:
    portainer:
      loadBalancer:
        servers:
          - url: "http://localhost:9000/"
```

This one is new so we'll touch on what we're doing. Here we're defining a new `portainer` service for Traefik to pickup, and telling it how to get there. These services are normally auto defined by Traefik but because we've 

6. Create a new stack called `traefik-stack` using the following compose file:

```yaml
# Traefik Compose Stack
services:
  traefik:
    image: traefik:v3.3
    restart: always
    networks:
      - beszel_network
      - hello_network
      - hedgedoc_network
    ports:
     - "80:80"
     - "443:443"
    volumes:
      - /var/run/docker.sock:/var/run/docker.sock
      - /path/to/your/data/traefik/logs:/var/log
      - /path/to/your/data/traefik:/etc/traefik
    labels:
      - "traefik.enable=true"
      - "traefik.http.routers.api.rule=Host(`traefik.rr.efektion.net`)"
      - "traefik.http.routers.api.service=api@internal"
      - "traefik.http.routers.portainer.rule=Host(`portainer.ara.dotefekts.net`)"
      - "traefik.http.routers.portainer.service=portainer@file"

networks:
  beszel_network:
    external: true
  hello_network:
    external: true
  hedgedoc_network:
    external: true
```

### Using Docker Commands
Before we start, ensure you've stopped and deleted any containers or compose services from the previous tasks. Create a new directory to hold all of your different services. Each service will have it's own directory within this main directory with it's own compose file.
#### Watchtower Setup
Watchtower is service that will automatically update containers for us without intervention. This can cause issues sometimes if an update includes a breaking change, so we'll add a filter to Watchtower so it only updates particular services.

1. Create a new directory called `watchtower-service` and a `docker-compose.yml` file within with the following:

```yaml
# watchtower-service/docker-compose.yml
services:
  watchtower:
    image: beatkind/watchtower
    environment:
      - WATCHTOWER_LABEL_ENABLE=true
    volumes:
      - /var/run/docker.sock:/var/run/docker.sock
```

2. Bring the Watchtower service up with `docker compose up -d`.

Watchtower will now run a daily check and update any containers with updated images. As we've specified the `WATCHTOWER_LABEL_ENABLE=true` environment variable, we'll need to add the `com.centurylinklabs.watchtower.enable=true` label to any containers we want Watchtower to update.
#### Traefik Setup

# Finally, a Note
**Do not expose any of these services to the internet. Do not do it.**
## Appendix: Adding HTTPS
For our services, we've used insecure HTTP connections for convenience. If you don't own a domain, this will be fine for use for internal services on your home network, though you will  need to go back to using ports for service connections instead of using a reverse proxy. If you do own a domain, we can use the Traefik `certificatesResolvers:` option to configure HTTPS certificates for our services. These instructions will use the `cloudflare` DNS provider option, but you can find other provider options here: https://doc.traefik.io/traefik/https/acme/#providers. We will **NOT** be covering TLS or HTTP challenge options, as these require your services to be publicly accessible which is *highly unrecommended*.

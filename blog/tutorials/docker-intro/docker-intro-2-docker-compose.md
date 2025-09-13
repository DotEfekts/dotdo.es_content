# Two Weeks to Git Good - Intro to Docker

[Basic Commands](docker-intro-1-basic-commands.md)
[**Docker Compose**](docker-intro-2-docker-compose.md)
[Docker Build](docker-intro-3-docker-build.md)
[Putting it All Together](docker-intro-4-homelab-creation.md)
## Docker Compose
### Basic Compose File
Let's take our Mario game container and run it in `compose` instead. 

1. Create a directory called `mario-compose` (or whatever else you like) and then create a file in that directory called `docker-compose.yml` (NOT whatever else you like) with the following contents:

```yaml
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

```yaml
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

```yaml
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

12. Bring the services down with `docker compose down`.

Next: [Docker Build](docker-intro-3-docker-build.md)
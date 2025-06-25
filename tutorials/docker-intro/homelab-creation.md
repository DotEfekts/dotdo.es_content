# Two Weeks to Git Good - Intro to Docker

[Basic Commands](/tutorials/docker-intro/basic-commands)
[Docker Compose](/tutorials/docker-intro/docker-compose)
[Docker Build](/tutorials/docker-intro/docker-build)
[**Putting it All Together**](/tutorials/docker-intro/homelab-creation)
## Putting It All Together
At this point we've learnt enough to put together a basic service stack that you can then build on. We're going to be putting this together in a modular way, so you can pick and choose which of the following you want to add to your stack.

> If you do not own a domain name you will not be able to continue using domains for Traefik after the workshop. You should modify the compose configurations to remove the Traefik service and the Traefik labels on the other containers, and use the `ports:` setting in the compose files instead to open those services to your local network.
### Using Portainer
Before we start, ensure you've stopped and deleted any containers or compose stacks from the previous tasks. We'll need a directory to store config and data files for our services. Create a new directory and note the path. Replace any references to `/path/to/your/data` with this directory.
#### Portainer Setup
To start, we'll create our Portainer instance so we can manage all of our other services using the Portainer UI. We'll add Portainer to Traefik once we set it up, but we also want to leave a port for Portainer open for access if something goes wrong with Traefik.

1. Create a data volume using `docker volume create portainer_data`
2. Create a new network using `docker network create portainer-network`
3. Create a folder in your data directory called `portainer`
4. Bring the Portainer service up with `docker run -d -p 9443:9443 --name portainer --restart=always -v /var/run/docker.sock:/var/run/docker.sock -v portainer_data:/data -v /path/to/your/data/portainer:/external --network portainer-network portainer/portainer-ce:lts`

This will: Create a container with the `portainer/portainer-ce` image, open the `9443` port so we can access the web UI, ensure the container restarts if it is stopped, map the Docker socket into the container so Portainer can manage Docker, map the `portainer_data` volume to the `/data` directory in the container, map the `portainer` directory to the `/external` directory in the container, and add the container to the `portainer-network` network.

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
Here we'll add our Flask Hello World app to our services. Copy the `helloflask-build` folder into our `portainer` directory. Rename it to `helloflask` for convenience.

1. Go to the **Networks** and create a new network called `hello-network`
2. Add a new stack called `hello-stack` using this compose file:

```yaml
# Hello World Compose Stack
services:
  helloworld:
    build: /external/helloflask
    container_name: flask-hello
    networks:
      - hello-network
    environment:
      - HELLO_TARGET=Portainer
    labels:
      - 'traefik.enable=true'
networks:
  hello-network:
    external: true
```

On the container, we're telling Docker to add the container to the `hello-network` network. In the `networks` section we're defining which Docker networks compose should use. As we've made the `hello-network` outside the compose stack, we need to mark it as `external`.

3. Deploy the stack. We won't be able to access this service until we've deployed Traefik but want to setup all our networks for the rest of the services before we do that.
### HedgeDoc Setup
We're going to setup HedgeDoc here as a practical service we can actually do something with. You can skip this if you'd prefer if you don't expect to have any use for it.

1. Add a new network called `hedgeapp-network`.
2. Add a new stack called `hedgedoc-stack`. We'll be using mostly the same compose file as before but with some modifications to work with Trafik:

```yaml
# HedgeDoc Compose Stack
services:
  doc-database:
    image: postgres:13.4-alpine
    networks:
      - hedgedb-network
    environment:
      - POSTGRES_USER=hedgedoc
      - POSTGRES_PASSWORD=password
      - POSTGRES_DB=hedgedoc
    volumes:
      - database:/var/lib/postgresql/data
    restart: always
  docs:
    image: quay.io/hedgedoc/hedgedoc:1.10.3
    networks:
      - hedgeapp-network
      - hedgedb-network
    environment:
      - CMD_DB_URL=postgres://hedgedoc:password@doc-database:5432/hedgedoc
      - CMD_DOMAIN=docs.rr.efektion.net
      - CMD_URL_ADDPORT=false
    volumes:
      - uploads:/hedgedoc/public/uploads
    labels:
      - "traefik.enable=true"
      - "com.centurylinklabs.watchtower.enable=true"
    restart: always
    depends_on:
      - doc-database
volumes:
  database:
  uploads:
networks:
  hedgeapp-network:
    external: true
  hedgedb-network:
    internal: true
```

Here we're adding our `hedgeapp-network` to the application container. We're also adding another network that's managed by the compose stack called `hedgedb-network`. The internal tag in this case does not mark it as managed by compose, as that's the default, but that the network does not require external network access, i.e. does not need access to the internet.

3. Deploy the stack.
### Beszel Setup
Beszel is a simple server monitoring panel that can track system performance and Docker container usage. If you have multiple servers in your homelab you can monitor them all from the one place.

1. Create a new folder in your service data directory called `beszel`.
2. Create a new network called `beszel-network`.
3. Add a new stack called `beszel-stack` using the following compose file:

```yaml
services:
  beszel:
    image: henrygd/beszel:latest
    container_name: beszel
    networks:
      - beszel-network
    restart: unless-stopped
    volumes:
      - /path/to/your/data/beszel:/beszel_data
      - /path/to/your/data/beszel/beszel_socket:/beszel_socket
    labels:
      - "traefik.enable=true"
      - "com.centurylinklabs.watchtower.enable=true"

  beszel-agent:
    image: henrygd/beszel-agent:latest
    container_name: beszel-agent
    restart: unless-stopped
    network_mode: host
    volumes:
      - /path/to/your/data/beszel/beszel_socket:/beszel_socket
      - /var/run/docker.sock:/var/run/docker.sock:ro
    environment:
      LISTEN: /beszel_socket/beszel.sock
      KEY: 'UPDATE WITH YOUR PUBLIC KEY (copy from "Add system" dialog)'
    labels:
      - "com.centurylinklabs.watchtower.enable=true"
networks:
  beszel-network:
    external: true
```

The key variable we'll update once we've setup Traefik and have access to the web UI for Bezsel.

4. Deploy the stack.
#### Traefik Setup
Finally we'll add our reverse proxy to access everything. We'll need to configure some rules to access Portainer as well, as we didn't add any Traefik labels to its container.

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
# traefik/config/services.yml
http:
  services:
    portainer:
      loadBalancer:
        servers:
          - url: "http://portainer:9000/"
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
      - portainer-network
      - beszel-network
      - hello-network
      - hedgeapp-network
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
      - "traefik.http.routers.portainer.rule=Host(`portainer.rr.efektion.net`)"
      - "traefik.http.routers.portainer.service=portainer@file"
      - "com.centurylinklabs.watchtower.enable=true"

networks:
  portainer-network:
    external: true
  beszel-network:
    external: true
  hello-network:
    external: true
  hedgeapp-network:
    external: true
```

We should now have access to all of our services!
- The Traefik dashboard at `http://traefik.rr.efektion.net/`
- The Portainer admin panel at `http://portainer.rr.efektion.net/`
- The Beszel dashboard at `http://beszel.rr.efektion.net/`
- The HedgeDoc app at `http://docs.rr.efektion.net/`
- The Hello World app at `http://helloworld.rr.efektion.net/`

### Finishing the Beszel Setup
We need to obtain the key from the Beszel dashboard to finish setting up our monitoring. Go to the web UI at `http://beszel.rr.efektion.net/` and create your admin account.

1. Click **Add System** in the top right.
2. Enter a name for your local device and use `/beszel_socket/beszel.sock` for the **Host / IP** field.
3. Copy the public key and then click **Add System**.
4. Go back to Portainer and open the `beszel-stack` page, then click the **Editor** tab.
5. Update the `KEY:` variable with the public key you copied from the Bezsel UI. Make sure the key is within the quotes, and includes the `ssh-ed25519` portion.
6. Click **Update the stack**.

After a few moment the local server you added to the Beszel panel should come online (this may take a little time).
# Finally, a Note
**Do not expose any of these services to the internet. Do not do it.**
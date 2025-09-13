# Two Weeks to Git Good - Intro to Docker

[**Basic Commands**](docker-intro-1-basic-commands.md)
[Docker Compose](docker-intro-2-docker-compose.md)
[Docker Build](docker-intro-3-docker-build.md)
[Putting it All Together](docker-intro-4-homelab-creation.md)
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

Next: [Docker Compose](docker-intro-2-docker-compose.md)
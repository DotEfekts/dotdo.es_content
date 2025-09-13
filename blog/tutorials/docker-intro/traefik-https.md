# Two Weeks to Git Good - Intro to Docker

[Basic Commands](basic-commands)
[Docker Compose](docker-compose)
[Docker Build](docker-build)
[Putting it All Together](homelab-creation)
[**Appendix: Adding HTTPS**](traefik-https)


> **HTTPS:** Adding HTTPS support can be done fairly easily via Let's Encrypt assuming you have a domain name. An appendix will be at the end to show you how to do this using a DNS ACME challenge. This will allow you to use HTTPS certificates internally without requiring you to port forward to your Traefik service.
## Appendix: Adding HTTPS
For our services, we've used insecure HTTP connections for convenience. If you don't own a domain, this will be fine for use for internal services on your home network, though you will  need to go back to using ports for service connections instead of using a reverse proxy. If you do own a domain, we can use the Traefik `certificatesResolvers:` option to configure HTTPS certificates for our services. These instructions will use the `cloudflare` DNS provider option, but you can find other provider options here: https://doc.traefik.io/traefik/https/acme/#providers. We will **NOT** be covering TLS or HTTP challenge options, as these require your services to be publicly accessible which is *highly unrecommended*.

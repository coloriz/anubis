Anubis
======

```shell
export COMPOSE_FILE=compose.yaml:compose.prod.yaml
docker-compose up -d
docker-compose exec webapp python manage.py migrate
docker-compose exec webapp python manage.py collectstatic
docker-compose exec webapp python manage.py createsuperuser
docker-compose exec webapp chmod 700 /root/.ssh
```
FROM mysql:latest

ENV MYSQL_DATABASE=emma
ENV MYSQL_ROOT_USER=root
ENV MYSQL_ROOT_PASSWORD=root

EXPOSE 3306

COPY . /docker-entrypoint-initdb.d/

CMD ["mysqld"]

cd "$(realpath db)" && $(which redis-server) "$(realpath db/redis.conf)"
develop:
	pip install -e .[cluster]
	pip install -r ./requirements-dev.txt
.PHONY: develop

redis-cluster:
	docker-compose up -d
	# wait for redis cluster to come up
	for i in 1 2 3 4 5; do redis-cli -c -p 16379 CLUSTER INFO | grep -q 'cluster_state:ok' && break; sleep $$i; done
	redis-cli -c -p 16379 HELLO
	# Create new redis-sentinel cluster
	for i in 1 2 3; do redis-cli -c -p 21379 PING | grep -q 'PONG' && break; sleep $$i; done
	redis-cli -p 21379 SENTINEL MONITOR redis-test 127.0.0.1 23385 1
	redis-cli -p 23386 REPLICAOF 127.0.0.1 23385
	for i in 1 2; do redis-cli -p 21379 SENTINEL CKQUORUM redis-test | grep -q '^OK ' && break; sleep $$i; done
	redis-cli -p 21379 SENTINEL CKQUORUM redis-test
	
.PHONY: redis-cluster

format:
	black sentry_redis_tools/ tests/
.PHONY: format

lint:
	mypy sentry_redis_tools/ tests/ --strict --config-file mypy.ini
	flake8 sentry_redis_tools/ tests/
.PHONY: lint

docs:
	sphinx-build -W -b html docs/ docs/_build
.PHONY: docs

test:
	pytest -vv tests/
.PHONY: test

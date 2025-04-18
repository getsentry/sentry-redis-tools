develop:
	pip install -e .[cluster]
	pip install -r ./requirements-dev.txt
.PHONY: develop

redis-cluster:
	docker-compose up -d
	# wait for redis cluster to come up
	for i in 1 2 3 4 5; do redis-cli -c -p 16379 hello && break; sleep $$i; done
	
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

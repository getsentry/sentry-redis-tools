develop:
	pip install -e .
	pip install -r ./requirements-dev.txt
.PHONY: develop

lint: develop
	black sentry_redis_tools/
	mypy sentry_redis_tools/ --strict --config-file mypy.ini
	flake8 sentry_redis_tools/
.PHONY: lint

docs: develop
	sphinx-build -W -b html docs/ docs/_build

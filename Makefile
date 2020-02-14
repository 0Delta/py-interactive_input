test-deploy:
	pipenv run python3 setup.py bdist_wheel
	pipenv run twine upload --repository-url https://test.pypi.org/legacy/ dist/*

master-deploy:
	pipenv run python3 setup.py bdist_wheel
	pipenv run twine upload --repository pypi dist/*

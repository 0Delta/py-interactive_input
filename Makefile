test-deploy:
	pipenv run python3 setup.py bdist_wheel
	pipenv run twine upload --repository-url https://test.pypi.org/legacy/ dist/*

master-deploy:
	git tag v(grep "version" setup.py | awk -F"'" '{print $2}')
	git push --tags
	pipenv run python3 setup.py bdist_wheel
	pipenv run twine upload --repository pypi dist/*

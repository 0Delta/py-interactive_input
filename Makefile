test-deploy:
	pipenv run python3 setup.py bdist_wheel
	pipenv run twine upload --repository pypitest dist/*

master-deploy-tag:
	make pushtag
	make master-deploy

pushtag:
	git tag v$$(grep "version" setup.py | awk -F"'" '{print $$2}')
	git push --tags


master-deploy:
	pipenv run python3 setup.py bdist_wheel
	pipenv run twine upload --repository pypi dist/*

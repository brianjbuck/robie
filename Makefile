
test:
	py.test tests/

test_with_coverage:
	py.test --cov=robie tests/ && coverage html

teams_of_note:
	python -m robie --teams=data/teams.txt --uri=data/gamesfiles/cbbga17.txt | grep -E "Kentucky|Louisville|Murray|Utah|BYU|Weber|Oklahoma|North Carolina$"

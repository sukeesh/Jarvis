VERSION:=1.0

autopep8:
	@find . -iname "*.py" -not -path "./env/**" | xargs autopep8 --in-place --aggressive --aggressive --max-line-length=140

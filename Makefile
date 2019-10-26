VERSION:=1.0

build_docker:
	docker build -t jarvis:$(VERSION) .

run_docker:
	#Needs "xhost local:docker"
	docker run -it --rm -e DISPLAY=${DISPLAY} -v /tmp/.X11-unix:/tmp/.X11-unix jarvis:$(VERSION)

autopep8:
	@find . -iname "*.py" -not -path "./env/**" | xargs autopep8 --in-place --aggressive --aggressive
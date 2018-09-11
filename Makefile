VERSION:=1.0

build_docker:
	cd $(CURDIR)/docker && docker build -t jarvis:$(VERSION) .

run_docker:
	#Needs "xhost local:docker"
	docker run -it --rm -e DISPLAY=${DISPLAY} -v /tmp/.X11-unix:/tmp/.X11-unix jarvis:$(VERSION)

.PHONY: all
all: server client
server: server.o mytcp.o
	@echo "Buiding server..."
	g++ $(FLAGS) -o server $^
client: client.o mytcp.o
	@echo "Buiding client..."
	g++ $(FLAGS) -o client $^
%.o: %.cpp %.h
	g++ $(FLAGS) -c $<
.PHONY: clean
clean:
	rm *.o

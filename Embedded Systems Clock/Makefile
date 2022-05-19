
# used for compiling using gcc
CFLAGS = -Wall -Wno-comment -Werror -g 
CC     = gcc $(CFLAGS)

PROGRAMS = \
	clock_main \

clock_main : clock_main.o clock_sim.o clock_update.o
	$(CC) -o $@ $^

clock_main.o : clock_main.c clock.h
	$(CC) -c $<

clock_sim.o : clock_sim.c clock.h
	$(CC) -c $<

clock_update.o : clock_update.c clock.h
	$(CC) -c $<
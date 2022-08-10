# Embedded Systems Clock Emulator  

#### This folder contains 7 files:  
- clock_main.c
- clock_update.c
- clock_update_asm.s
- clock_sim.c
- clock.h
- Makefile
- README.md  

To compile and run:  
```bash
$  make clock_main
$  ./clock_main int
```  

**clock_main.c:**  
This file contains the main function for this progam, which takes a command line argument of time of day in seconds from the start of the day and returns a simulated LCD clock screen at that time. The main function takes in an argument, converts it into a global variable, and calls various functions to create an output. Along with the clock display it also prints out other metrics about the underlying information it uses.



**clock_update.c:**  
This file contains 3 functions:  

- **set_tod_from_secs** uses the time of day in seconds to create a struct containg the number of hours, minutes, and seconds to display.   

- **set_display_from_tod** uses bitmasks that are shifted into an empty 32-bit integer. The bitmasks represent different patterns for numbers in the LCD clock display   and the integer is unpacked by another function that displays its contents.  
  
- **clock_update** calls set_tod_from_secs with the global TIME_OF_DAY_SEC variable and uses the struct it creates to call the set_display_from_tod function. Checks both functions for errors.

**clock_update_asm.s:**
This file is not used during runtime, but contains the same functions as clock_update.c in x86-64 Assembly Language. It does the same thing as clock_update, but is optimzed to use as little memory and proceesing as needed to mimic coding on an embedded system.

**clock_sim.c:**  
This file uses the global CLOCK_DISPLAY_PORT to create a printable clock display. It unpacks the masks and uses the correpsonding positions to print a string of the bits used in the masking and the clock display.

**clock.h:**  
This is a header file containing the functions, structs, and variables used in other files of the program.

**Makefile:**  
This is a Makefile used for easy compilation of the program. Usage is shown below.  
```bash
$  make clock_main
```

## Examples and Error Catches  

The TIME_OF_DAY_SECS has a range between 0 and 86400, or the total number of seconds in a day. Examples of inputs inside and outside of that range are shown below.
```bash
$  ./clock_main 0
```
Has the output of:
```
TIME_OF_DAY_SEC set to: 0
result = set_tod_from_secs(     0, &tod );
result: 0
tod = {
  .hours   = 12
  .minutes = 0
  .seconds = 0
  .ampm    = 1
}
Simulated time is: 12 : 00 : 00 am
result = set_display_from_tod(tod, &display);
result: 0
display is
bits:  00 01 0110000 1101101 0111111 0111111
index: 30 28      21      14       7       0

result = clock_update();
result: 0
CLOCK_DISPLAY_PORT is
bits:  00 01 0110000 1101101 0111111 0111111
index: 30 28      21      14       7       0

Clock Display:
   # ####   #### ####
   #    #   #  # #  #
   #    # o #  # #  #
   # ####   #  # #  #
   # #    o #  # #  #
   # #      #  # #  # AM
   # ####   #### ####
```
If a value below 0 is inputted, the clock display will be empty along with the bit strings. Additional warnings will also be printed: 
```
Simulated time is: 6496 : 11396 : 32765 pm   
WARNING: Non-zero value returned
result = set_display_from_tod(tod, &display);
result: 1
display is
bits:  00 00 0000000 0000000 0000000 0000000 
index: 30 28      21      14       7       0 
WARNING: Non-zero value returned

result = clock_update();
result: 1
CLOCK_DISPLAY_PORT is
bits:  00 00 0000000 0000000 0000000 0000000 
index: 30 28      21      14       7       0 
WARNING: Non-zero value returned
```

For values above the maximum, the program doesn't run and a simple error message is printed:
```
TIME_OF_DAY_SEC set to: 5678910
Time 5678910 exceeds max 86400
```

And finally, to demonstrate the AM/PM toggle:  

```bash
$  ./clock_main 43240
```
Ouputs:
```
TIME_OF_DAY_SEC set to: 43240
result = set_tod_from_secs( 43240, &tod );
result: 0
tod = {
  .hours   = 12
  .minutes = 0
  .seconds = 40
  .ampm    = 2
}
Simulated time is: 12 : 00 : 40 pm
result = set_display_from_tod(tod, &display);
result: 0
display is
bits:  00 10 0110000 1101101 0111111 0111111
index: 30 28      21      14       7       0

result = clock_update();
result: 0
CLOCK_DISPLAY_PORT is
bits:  00 10 0110000 1101101 0111111 0111111
index: 30 28      21      14       7       0

Clock Display:
   # ####   #### ####
   #    #   #  # #  #
   #    # o #  # #  #
   # ####   #  # #  #
   # #    o #  # #  #
   # #      #  # #  #
   # ####   #### #### PM
```

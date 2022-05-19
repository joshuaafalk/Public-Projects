
#include <stdio.h>
#include <stdlib.h>
#include <time.h>
#include "clock.h"

int set_tod_from_secs(int time_of_day_sec, tod_t *tod){
	if (time_of_day_sec < 0 || time_of_day_sec >= 86400){return 1;} //conditional for bad input values
	
	tod->hours = time_of_day_sec / 3600; //sets hours
	
	if (tod->hours >=12){tod->ampm = 2;}
	else{tod->ampm = 1;} //setting am/pm based on number of hours
	if (tod->hours ==0){tod->hours = 12;} //midnight
	if (tod->hours >12){tod->hours = tod->hours - 12;}//keeps on a 12 hour time scale
	int rem = time_of_day_sec % 3600; //gets remainder 
	tod->minutes = rem / 60; //sets minutes
	tod->seconds = rem % 60; //remainder is number of seconds left after divifing for minutes
	return 0;
}

int set_display_from_tod(tod_t tod, int *display){
	int masks[] = {0b0111111, 0b0110000, 0b1101101, 0b1111001, 0b1110010, 0b1011011, 0b1011111, 0b0110001, 0b1111111, 0b1111011}; //array of bitmasks
	
	if (tod.hours < 0 || tod.hours >12){return 1;}
	if (tod.minutes < 0 || tod.minutes >59){return 1;}//conditionals for bad values
	if (tod.seconds <0 || tod.seconds >59){return 1;}
	
	int min_ones = tod.minutes %10;
	int min_tens = (tod.minutes /10) %10;//getting digits
	
	int hour_ones = tod.hours %10;
	int hour_tens = (tod.hours /10) %10;
	
	*display = *display ^ *display; //sets display bits to 0
	*display = *display | masks[min_ones];  //setting display
	
	*display = *display | (masks[min_tens] << 7);//minute tens place
	*display = *display | (masks[hour_ones] << 14);//hour ones place
	
	if (hour_tens == 0){
		*display = *display | 0b0000000 << 21;  //conditional for blank in hours tens spot
	}
	else{*display = *display | (masks[1] << 21);}//if not blank then must be 1
	
	if (tod.ampm ==1){
		*display = *display | 1 << 28;  //am pm setter
	}
	else{*display = *display | 1 << 29;}
	
	return 0;
}

int clock_update(){
	tod_t tod;
	int ret = set_tod_from_secs(TIME_OF_DAY_SEC, &tod);//calls helper functions, checks return values
	if (ret ==1){return 1;}
	ret = set_display_from_tod(tod, &CLOCK_DISPLAY_PORT);
	if (ret ==1){return 1;}
	return 0;

}


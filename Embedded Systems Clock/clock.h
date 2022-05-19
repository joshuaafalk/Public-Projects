#ifndef CLOCK_H
#define CLOCK_H 1

// bitsize of certain types
#define INT_BITS   (sizeof(int)*8)
#define SHORT_BITS (sizeof(short)*8)
#define CHAR_BITS  (sizeof(char)*8)

// format for broken down time
typedef struct{
  short hours;
  short minutes;
  short seconds;
  char ampm;  // 1 for am, 2 for pm
} tod_t;

// functions for emulating
int set_tod_from_secs(int time_of_day, tod_t *tod);
int set_display_from_tod(tod_t tod, int *display);
int clock_update();


// global used to control display
extern int CLOCK_DISPLAY_PORT;

// read only time of day in seconds
extern int TIME_OF_DAY_SEC;

// uses CLOCK_DISPLAY_PORT to print time
void print_clock_display();

// used to show bits of an int
char *bitstr(int x, int bits);
char *bitstr_index(int bits);

#endif



#include <stdlib.h>
#include <stdio.h>
#include <strings.h>
#include <sys/timeb.h>
#include <math.h>


#define MAX_LENGTH 256
#define MAX_SIZE 100
#define MAX_TASKS 100

/* data structures ... (ha ha)
 */
typedef unsigned char Bool;
#define TRUE 1
#define FALSE 0



/* commands
 */
char gfilename[MAX_LENGTH];
int gnumber_per_problem;

Bool scan_line(FILE *fdata, 
	       int *N,
	       int *l,
	       int *h,
	       float *htime,
	       int *Slb,
	       int *S,
	       float *Stime,
	       float *time);
int scan_int(FILE *fdata, char c, int *retval);
int scan_float(FILE *fdata, char c, float *retval);
int digitvalue(char c);


/* command line
 */
void usage( void );
Bool process_command_line( int argc, char *argv[] );





int main( int argc, char *argv[] )

{

  FILE *fdata;

  int num_problems = 0, rnd;
  /* 100 problems, 50 rnd runs per problem*/
  int N[100][50], tempN;/* N */
  int l[100][50], templ;/* optimal plan length */
  int h[100][50], temph;/* h of ini state */
  float htime[100][50], temphtime;/* time for computing h fn */
  int Slb[100][50], tempSlb;/* nr of search states for best lb */
  int S[100][50], tempS;/* nr of search states total */
  float Stime[100][50], tempStime;/* search time */
  float time[100][50], temptime;/* total time */
  Bool allsolved[100];

  int i, j;
  int median = (int) gnumber_per_problem/2;
  float mean, var, dev;

  float devh[100];/* h of ini state */
  float devhtime[100];/* time for computing h fn */
  float devSlb[100];/* nr of search states for best lb */
  float devS[100];/* nr of search states total */
  float devStime[100];/* search time */
  float devtime[100];/* total time */

  float meanh[100];/* h of ini state */
  float meanhtime[100];/* time for computing h fn */
  float meanSlb[100];/* nr of search states for best lb */
  float meanS[100];/* nr of search states total */
  float meanStime[100];/* search time */
  float meantime[100];/* total time */
  
  int domaincount = 0;
  int prevN;
  float meandevh = 0;
  float meandevhtime = 0;
  float meandevSlb = 0;
  float meandevS = 0;
  float meandevStime = 0;
  float meandevtime = 0;
  int numberperdomain = 0;

  char domain[20][50] = {
    "Logistics            ",
    "PipesworldNoTankage  ",
    "PipesworldTankage    ",
    "PSR                  ",
    "Satellite            ",
    "TPP                  ",
    "",
    "",
    "",
    "",
    "",
    "",
    "",
    "",
    "",
    "",
    "",
    "",
    "",
    ""
  };


  if ( !process_command_line( argc, argv ) ) {
    usage();
    exit( 1 );
  }



  /* collect data into arrays.
   */
  if ( (fdata = fopen( gfilename, "r")) == NULL ) {
    printf("\n\nCannot open file %s.\n\n", gfilename);
    exit( 1 );
  }
  while (TRUE ) {
    allsolved[num_problems] = TRUE;
    for ( rnd = 0; rnd < gnumber_per_problem; rnd++ ) {
      tempN = -1;
      templ = -1;
      temph = -1;
      temphtime = -1;
      tempSlb = -1;
      tempS = -1;
      tempStime = -1;
      temptime = -1;
      if ( !scan_line(fdata, 
		      &tempN, 
		      &templ, 
		      &temph, 
		      &temphtime, 
		      &tempSlb, 
		      &tempS, 
		      &tempStime, 
		      &temptime) ) break;

      if ( 0 ) {
	printf("%7d %3d %3d %7.2f %9d %9d %7.2f %7.2f\n", 
	       tempN,
	       templ,
	       temph,
	       temphtime,
	       tempSlb,
	       tempS,
	       tempStime,
	       temptime);
	fflush(stdout);
      }
      if ( temptime == -1 ) allsolved[num_problems] = FALSE;


      /* insert ordered... useless here but whatever
       */
      for ( i = 0; i < rnd; i++ ) {
	if ( temptime != -1 && 
	     (time[num_problems][i] >= temptime || time[num_problems][i] == -1) ) break;
      }
      for ( j = rnd; j > i; j-- ) {
	N[num_problems][j] = N[num_problems][j-1];
	l[num_problems][j] = l[num_problems][j-1];
	h[num_problems][j] = h[num_problems][j-1];
	htime[num_problems][j] = htime[num_problems][j-1];
	Slb[num_problems][j] = Slb[num_problems][j-1];
	S[num_problems][j] = S[num_problems][j-1];
	Stime[num_problems][j] = Stime[num_problems][j-1];
	time[num_problems][j] = time[num_problems][j-1];
      } 
      N[num_problems][i] = tempN;
      l[num_problems][i] = templ;
      h[num_problems][i] = temph;
      htime[num_problems][i] = temphtime;
      Slb[num_problems][i] = tempSlb;
      S[num_problems][i] = tempS;
      Stime[num_problems][i] = tempStime;
      time[num_problems][i] = temptime;
    }
    if ( rnd < gnumber_per_problem ) break;

    num_problems++;
  }
  fclose( fdata );

  
  /* debug */
  if ( 0 ) {
    for ( i = 0; i < num_problems; i++ ) {
      printf("allsolved: %d\n", allsolved[i]);
      for ( j = 0; j < gnumber_per_problem; j++ ) {
	printf("%7d %3d %3d %7.2f %9d %9d %7.2f %7.2f\n", 
	       N[i][j],
	       l[i][j],
	       h[i][j],
	       htime[i][j],
	       Slb[i][j],
	       S[i][j],
	       Stime[i][j],
	       time[i][j]);
      }
      printf("\n");
    }
  }



  /* compute std deviation of all parameters, for each batch of 
   * random runs
   */
  for ( i = 0; i < num_problems; i++ ) {

    mean = 0;
    for ( j = 0; j < gnumber_per_problem; j++ ) mean += ((float) h[i][j]);
    mean /= ((float) gnumber_per_problem);
    var = 0;
    for ( j = 0; j < gnumber_per_problem; j++ ) {
      var += (((float) h[i][j]) - mean) * (((float) h[i][j]) - mean);
    }
    var /= ((float) gnumber_per_problem);
    dev = sqrt(var);
    devh[i] = dev;
    meanh[i] = mean;

    mean = 0;
    for ( j = 0; j < gnumber_per_problem; j++ ) mean += htime[i][j];
    mean /= ((float) gnumber_per_problem);
    var = 0;
    for ( j = 0; j < gnumber_per_problem; j++ ) {
      var += (htime[i][j] - mean) * (htime[i][j] - mean);
    }
    var /= ((float) gnumber_per_problem);
    dev = sqrt(var);
    devhtime[i] = dev;
    meanhtime[i] = mean;

    mean = 0;
    for ( j = 0; j < gnumber_per_problem; j++ ) mean += ((float) Slb[i][j]);
    mean /= ((float) gnumber_per_problem);
    var = 0;
    for ( j = 0; j < gnumber_per_problem; j++ ) {
      var += (((float) Slb[i][j]) - mean) * (((float) Slb[i][j]) - mean);
    }
    var /= ((float) gnumber_per_problem);
    dev = sqrt(var);
    devSlb[i] = dev;
    meanSlb[i] = mean;

    mean = 0;
    for ( j = 0; j < gnumber_per_problem; j++ ) mean += ((float) S[i][j]);
    mean /= ((float) gnumber_per_problem);
    var = 0;
    for ( j = 0; j < gnumber_per_problem; j++ ) {
      var += (((float) S[i][j]) - mean) * (((float) S[i][j]) - mean);
    }
    var /= ((float) gnumber_per_problem);
    dev = sqrt(var);
    devS[i] = dev;
    meanS[i] = mean;

    mean = 0;
    for ( j = 0; j < gnumber_per_problem; j++ ) mean += Stime[i][j];
    mean /= ((float) gnumber_per_problem);
    var = 0;
    for ( j = 0; j < gnumber_per_problem; j++ ) {
      var += (Stime[i][j] - mean) * (Stime[i][j] - mean);
    }
    var /= ((float) gnumber_per_problem);
    dev = sqrt(var);
    devStime[i] = dev;
    meanStime[i] = mean;

    mean = 0;
    for ( j = 0; j < gnumber_per_problem; j++ ) mean += time[i][j];
    mean /= ((float) gnumber_per_problem);
    var = 0;
    for ( j = 0; j < gnumber_per_problem; j++ ) {
      var += (time[i][j] - mean) * (time[i][j] - mean);
    }
    var /= ((float) gnumber_per_problem);
    dev = sqrt(var);
    devtime[i] = dev;
    meantime[i] = mean;
  }

  if ( 0 ) {
    for ( i = 0; i < num_problems; i++ ) {
      if ( !allsolved[i] ) continue;
      printf("%7d   |  h: %5.2f (%5.2f)  |  htime: %7.2f (%5.2f)  |  Slb: %10.2f (%5.2f)  |  S: %10.2f (%5.2f)  |  Stime: %7.2f (%5.2f)  |  time: %7.2f (%5.2f)\n",  
	     N[i][0], 
	     devh[i],devh[i]/meanh[i], 
	     devhtime[i],devhtime[i]/meanhtime[i],
	     devSlb[i],devSlb[i]/meanSlb[i],
	     devS[i],devS[i]/meanS[i],
	     devStime[i],devStime[i]/meanStime[i],
	     devtime[i],devtime[i]/meantime[i]);
    }
  }


  domaincount = 0;
  prevN = N[0][0];
  meandevh = 0;
  meandevhtime = 0;
  meandevSlb = 0;
  meandevS = 0;
  meandevStime = 0;
  meandevtime = 0;
  numberperdomain = 0;
  for ( i = 0; i < num_problems; i++ ) {
    if ( N[i][0] != prevN  ) {
      prevN = N[i][0];
      meandevh /= ((float) numberperdomain);
      meandevhtime /= ((float) numberperdomain);
      meandevSlb /= ((float) numberperdomain);
      meandevS /= ((float) numberperdomain);
      meandevStime /= ((float) numberperdomain);
      meandevtime /= ((float) numberperdomain);
      printf("%s   |  h: %5.2f  |  htime: %7.2f  |  Slb: %10.2f  |  S: %10.2f  |  Stime: %7.2f  |  time: %7.2f\n", 
	     domain[domaincount++],
	     meandevh, 
	     meandevhtime,
	     meandevSlb,
	     meandevS,
	     meandevStime,
	     meandevtime);
      meandevh = 0;
      meandevhtime = 0;
      meandevSlb = 0;
      meandevS = 0;
      meandevStime = 0;
      meandevtime = 0;
      numberperdomain = 0;
    }

    meandevh += devh[i];
    meandevhtime += devhtime[i];
    meandevSlb += devSlb[i];
    meandevS += devS[i];
    meandevStime += devStime[i];
    meandevtime += devtime[i];
    numberperdomain++;
  }



  printf("\n\n");
  exit( 0 );

}



Bool scan_line(FILE *fdata, 
	       int *N,
	       int *l,
	       int *h,
	       float *htime,
	       int *Slb,
	       int *S,
	       float *Stime,
	       float *time) 

{

  char c;
  int temp;

  while ( (c = getc(fdata)) != EOF && c != ' ' );
  if ( c == EOF ) return FALSE;

  while ( (c = getc(fdata)) != EOF && c == ' ' );
  if ( c == EOF ) return FALSE;
  temp = scan_int(fdata, c, N);
  if ( temp == 0 ) return FALSE;
  if ( temp == 2 ) {
    while ( (c = getc(fdata)) != EOF && c != '\n' );
    if ( c == EOF ) return FALSE;
    return TRUE;
  }

  while ( (c = getc(fdata)) != EOF && c == ' ' );
  if ( c == EOF ) return FALSE;
  temp = scan_int(fdata, c, l);
  if ( temp == 0 ) return FALSE;
  if ( temp == 2 ) {
    while ( (c = getc(fdata)) != EOF && c != '\n' );
    if ( c == EOF ) return FALSE;
    return TRUE;
  }

  while ( (c = getc(fdata)) != EOF && c == ' ' );
  if ( c == EOF ) return FALSE;
  temp = scan_int(fdata, c, h);
  if ( temp == 0 ) return FALSE;
  if ( temp == 2 ) {
    while ( (c = getc(fdata)) != EOF && c != '\n' );
    if ( c == EOF ) return FALSE;
    return TRUE;
  }

  while ( (c = getc(fdata)) != EOF && c == ' ' );
  if ( c == EOF ) return FALSE;
  temp = scan_float(fdata, c, htime);
  if ( temp == 0 ) return FALSE;
  if ( temp == 2 ) {
    while ( (c = getc(fdata)) != EOF && c != '\n' );
    if ( c == EOF ) return FALSE;
    return TRUE;
  }

  while ( (c = getc(fdata)) != EOF && c == ' ' );
  if ( c == EOF ) return FALSE;
  temp = scan_int(fdata, c, Slb);
  if ( temp == 0 ) return FALSE;
  if ( temp == 2 ) {
    while ( (c = getc(fdata)) != EOF && c != '\n' );
    if ( c == EOF ) return FALSE;
    return TRUE;
  }

  while ( (c = getc(fdata)) != EOF && c == ' ' );
  if ( c == EOF ) return FALSE;
  temp = scan_int(fdata, c, S);
  if ( temp == 0 ) return FALSE;
  if ( temp == 2 ) {
    while ( (c = getc(fdata)) != EOF && c != '\n' );
    if ( c == EOF ) return FALSE;
    return TRUE;
  }

  while ( (c = getc(fdata)) != EOF && c == ' ' );
  if ( c == EOF ) return FALSE;
  temp = scan_float(fdata, c, Stime);
  if ( temp == 0 ) return FALSE;
  if ( temp == 2 ) {
    while ( (c = getc(fdata)) != EOF && c != '\n' );
    if ( c == EOF ) return FALSE;
    return TRUE;
  }

  while ( (c = getc(fdata)) != EOF && c == ' ' );
  if ( c == EOF ) return FALSE;
  temp = scan_float(fdata, c, time);
  if ( temp == 0 ) return FALSE;

  return TRUE;

}



int scan_int(FILE *fdata, char c, int *retval)

{

  char all[20];
  int num = 1, i;
  int result = 0;
  int base = 1;

  all[0] = c;
  while ( (c = getc(fdata)) != EOF && c != ' ' && c != '\n') {
    all[num++] = c;
    base *= 10;
  }
  if ( c == EOF ) return 0;

  for ( i = 0; i < num; i++ ) {
    if ( digitvalue(all[i]) < 0 ) return 2;
    result += base * digitvalue(all[i]);
    base /= 10;
  }

  *retval = result;
  if ( 0 ) {printf("%d ", result);} 

  return 1;

}



int scan_float(FILE *fdata, char c, float *retval)

{

  char all1[20], all2[20];
  int num1 = 1, num2 = 0, i;
  float result = 0;
  float base = 1;

  all1[0] = c;
  while ( (c = getc(fdata)) != EOF && c != '.' && c != ' ' && c != '\n') {
    all1[num1++] = c;
    base *= 10;
  }
  if ( c == EOF ) return 0;
  while ( (c = getc(fdata)) != EOF && c != ' ' && c != '\n') {
    all2[num2++] = c;
  }

  for ( i = 0; i < num1; i++ ) {
    if ( digitvalue(all1[i]) < 0 ) return 2;
    result += base * ((float) digitvalue(all1[i]));
    base /= 10;
  }
  for ( i = 0; i < num2; i++ ) {
    if ( digitvalue(all2[i]) < 0 ) return 2;
    result += base * ((float) digitvalue(all2[i]));
    base /= 10;
  }

  *retval = result;

  return 1;

}



int digitvalue(char c)

{

  switch ( c ) {
    case '0': return 0;
    case '1': return 1;
    case '2': return 2;
    case '3': return 3;
    case '4': return 4;
    case '5': return 5;
    case '6': return 6;
    case '7': return 7;
    case '8': return 8;
    case '9': return 9;
  default:
    return -1;
  }

  exit(1);

}







void usage( void )

{

  printf("\nusage:\n");

  printf("\nOPTIONS   DESCRIPTIONS\n\n");
  printf("-f <str>    name of file\n\n");
  printf("-n <num>    number rnd runs per problem\n\n");

}



Bool process_command_line( int argc, char *argv[] )

{

  char option;


  while ( --argc && ++argv ) {
    if ( *argv[0] != '-' || strlen(*argv) != 2 ) {
      return FALSE;
    }
    option = *++argv[0];
    switch ( option ) {
    default:
      if ( --argc && ++argv ) {
	switch ( option ) {
	case 'f':
	  strncpy( gfilename, *argv, MAX_LENGTH );
	  break;
	case 'n':
	  sscanf( *argv, "%d", &gnumber_per_problem );
	  break;
	default:
	  printf( "\n\nunknown option: %c entered\n\n", option );
	  return FALSE;
	}
      } else {
	return FALSE;
      }
    }
  }

  return TRUE;

}

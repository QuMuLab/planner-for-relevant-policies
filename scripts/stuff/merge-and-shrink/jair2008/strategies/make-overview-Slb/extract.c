

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
Bool gon[8];

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

  int num_problems = 0;
  /* 8 strategies, 100 problems */
  int tempN, l, h, S;
  float htime, Stime;
  int N[100];
  int Slb[8][100];
  float time[8][100];

  char strategy[8][3] = {"11", "21", "31", "41", "12", "13", "14", "DFP"};
  char fname[20];

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

  int i, j, k, prevN = -1, domaincount = 0;
  int current_domain, current_instance;

  float ttime[8][20][100];
  int tSlb[8][20][100];
  Bool solved[8][20][100];
  int numinstances[20];
  int numsolved[8][20];
  Bool allsolved[20][100];
  float allsolvedmean[8][20];
  Bool allsolve;
  int numallsolve;






  gon[0] = TRUE;
  for ( i = 1; i < 8; i++ ) gon[i] = FALSE;

  if ( !process_command_line( argc, argv ) ) {
    usage();
    exit( 1 );
  }



  /* collect data into arrays.
   */
  for ( i = 0; i < 8; i++ ) {
    if ( !gon[i] ) continue;

    sprintf(fname, "../../../../results/jair-2008/strategies/CLEAN-%s", strategy[i]);
    if ( (fdata = fopen( fname, "r")) == NULL ) {
      printf("\n\nCannot open file %s.\n\n", fname);
      exit( 1 );
    }
    j = 0;
    while ( TRUE ) {
      if ( (fscanf(fdata, "%d %d %d %f %d %d %f %f\n",
	     &tempN, &l, &h, &htime, &(Slb[i][j]), &S, &Stime, &(time[i][j]))) == EOF )
	break;
      if ( i == 0 ) {
	N[j] = tempN;
	num_problems++;
      }
      j++;
    }
    fclose( fdata );

    if ( 0 ) printf("%d: %d, %d\n", i, j, num_problems);

    if ( j != num_problems ) {
      printf("num problems does not coincide! %s, %d, %d\n\n", strategy[i], num_problems, j);
      exit(1);
    }
  }




  /* debug */
  if ( 0 ) {
    prevN = -1;
    for ( j = 0; j < num_problems; j++ ) {
      if ( N[j] != prevN  ) {
	prevN = N[j];
	printf("\n%s:\n", domain[domaincount++]);
      }

      for ( i = 0; i < 8; i++ ) {
	if ( !gon[i] ) continue;
	printf("%s: %7d   %7.2f   |   ", strategy[i], Slb[i][j], time[i][j]);
      }
      printf("\n");
    }
  }
  domaincount = 0;
  prevN = -1;
  for ( j = 0; j < num_problems; j++ ) {
    if ( N[j] != prevN  ) {
      prevN = N[j];
      domaincount++;
    }
  }



  /* now create the summary!
   */
  prevN = -1;
  current_domain = -1;
  for ( j = 0; j < num_problems; j++ ) {
    if ( N[j] != prevN  ) {
      prevN = N[j];
      numinstances[current_domain] = current_instance;
      current_domain++;
      current_instance = 0;
      for ( i = 0; i < 8; i++ ) {
	numsolved[i][current_domain] = 0;
      }
    }

    allsolve = TRUE;
    for ( i = 0; i < 8; i++ ) {
      if ( !gon[i] ) continue;

      ttime[i][current_domain][current_instance] =  time[i][j];
      tSlb[i][current_domain][current_instance] =  Slb[i][j];
      if ( time[i][j] != -1 ) {
	solved[i][current_domain][current_instance] = TRUE;
	numsolved[i][current_domain]++;
      } else {
	allsolve = FALSE;
	solved[i][current_domain][current_instance] = FALSE;
      }
      allsolved[current_domain][current_instance] = allsolve;
    }

    current_instance++;
  }
  numinstances[current_domain] = current_instance;

  /* debug */
  if ( 0 ) {
    for ( k = 0; k < domaincount; k++ ) {
      printf("\n%s:\n", domain[k]);

      printf("             ");
      for ( i = 0; i < 8; i++ ) {
	if ( !gon[i] ) continue;
	printf("%s: %9d   |   ", strategy[i], numsolved[i][k]);
      }
      printf("\n");

      for ( j = 0; j < numinstances[k]; j++ ) {
	printf("all: %d   |   ", allsolved[k][j]);

	for ( i = 0; i < 8; i++ ) {
	  if ( !gon[i] ) continue;
	  printf("%s: %7d %7.2f %d   |   ", strategy[i], tSlb[i][k][j], ttime[i][k][j], solved[i][k][j]);
	}
	printf("\n");
      }
    }
  }


  for ( k = 0; k < domaincount; k++ ) {
    for ( i = 0; i < 8; i++ ) {
      allsolvedmean[i][k] = 0;
      numallsolve = 0;
      for ( j = 0; j < numinstances[k]; j++ ) {
	if ( allsolved[k][j] ) {
	  allsolvedmean[i][k] += ((float) tSlb[i][k][j]);
	  numallsolve++;
	}
      }
      allsolvedmean[i][k] = allsolvedmean[i][k] / ((float) numallsolve);
    }
  }



  

  /* absolute data
   */
  for ( k = 0; k < domaincount; k++ ) {
    printf("\n%s:", domain[k]);

    for ( i = 0; i < 8; i++ ) {
      if ( !gon[i] ) continue;
      printf("%s: %3d %10.1f | ", 
	     strategy[i], 
	     numsolved[i][k],
	     allsolvedmean[i][k]);
    }

  }



  printf("\n\n\n");

  /* relative data
   */
  for ( k = 0; k < domaincount; k++ ) {
    printf("\n%s:", domain[k]);

    for ( i = 0; i < 8; i++ ) {
      if ( !gon[i] ) continue;
      printf("%s: %3.2f %10.2f | ", 
	     strategy[i], 
	     (((float)numsolved[i][k])/((float)numsolved[0][k])),
	     ((allsolvedmean[i][k]/allsolvedmean[0][k])));
    }

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
  printf("-1          use 21 strategy\n");
  printf("-2          use 31 strategy\n");
  printf("-3          use 41 strategy\n");
  printf("-4          use 12 strategy\n");
  printf("-5          use 13 strategy\n");
  printf("-6          use 14 strategy\n");
  printf("-7          use DFP strategy\n\n");

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
    case '1':
      gon[1] = TRUE;
      break;
    case '2':
      gon[2] = TRUE;
      break;
    case '3':
      gon[3] = TRUE;
      break;
    case '4':
      gon[4] = TRUE;
      break;
    case '5':
      gon[5] = TRUE;
      break;
    case '6':
      gon[6] = TRUE;
      break;
    case '7':
      gon[7] = TRUE;
      break;
    default:
      if ( --argc && ++argv ) {
	switch ( option ) {
/* 	case 'f': */
/* 	  strncpy( gfilename, *argv, MAX_LENGTH ); */
/* 	  break; */
/* 	case 'n': */
/* 	  sscanf( *argv, "%d", &gnumber_per_problem ); */
/* 	  break; */
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

/*-----------------------------------------------------------------------------
  VAL - The Automatic Plan Validator for PDDL+

  $Date: 2005/06/07 14:00:00 $
  $Revision: 4 $

  Maria Fox, Richard Howey and Derek Long - PDDL+ and VAL
  Stephen Cresswell - PDDL Parser

  maria.fox@cis.strath.ac.uk
  derek.long@cis.strath.ac.uk
  stephen.cresswell@cis.strath.ac.uk
  richard.howey@cis.strath.ac.uk

  By releasing this code we imply no warranty as to its reliability
  and its use is entirely at your own risk.

  Strathclyde Planning Group
  http://planning.cis.strath.ac.uk
 ----------------------------------------------------------------------------*/
#include "random.h"

namespace VAL {
  
NormalGen Generators::randomNumberNormGenerator = NormalGen();
UniformGen Generators::randomNumberUniGenerator = UniformGen(0,0,1);

//return a random number with norm prob over -1 to 1
double getRandomNumberNormal()
{
     double randomNumber;
     do
     {
       randomNumber = Generators::randomNumberNormGenerator()*0.25;
     }while(randomNumber > 1.0 || randomNumber < -1.0);

     //cout << randomNumber << " \\\\\n";
     return randomNumber;
};

//return a random number with uniform prob over 0 to 1
double getRandomNumberUniform()
{
     //double randomNumber = double(rand()) / double(RAND_MAX);
     double randomNumber = Generators::randomNumberUniGenerator();

     return randomNumber;
};

double getRandomNumberPsuedoNormal()
{
  
  int noToAverage = 4;
  double total = 0;

  for(int i = 1; i <= noToAverage; ++i)
  {
     total += getRandomNumberUniform();
  };

  return total/noToAverage;
};

};

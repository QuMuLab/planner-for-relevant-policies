/* ----------------------------------------------------------------------------
   Macros for diagnostic output.
   These generate code to output both name and value of a field,
   and to deal with pretty-printing indentation in a consistent way.

   Edit this file to change the output format of the syntax trees.

   $Date: 2001/10/23 15:04:06 $
   $Revision: 3.2 $

   stephen.cresswell@cis.strath.ac.uk
  
   Strathclyde Planning Group
   --------------------------------------------------------------------------*/

// #  expands arg into quoted string
// ## concatenates arg

// Output NAME - used for name of class
#define TITLE(NAME) indent(ind); cout << '(' << #NAME << ')';

// Display a data member that is a parse_category
#define FIELD(NAME) indent(ind); cout << #NAME << ": "; if (NAME != NULL) NAME->display(ind+1); else cout << "(NULL)";  

// Used for display of list element
#define ELT(NAME) { if ((NAME) != NULL) (NAME)->display(ind+1); else cout << "(NULL)"; }

// Display NAME only
#define LABEL(NAME) indent(ind); cout << #NAME << ':'; 

// Output a data member that is not a parse_category
#define LEAF(NAME) indent(ind); cout << #NAME << ": "; cout << NAME;


extern void indent(int ind);



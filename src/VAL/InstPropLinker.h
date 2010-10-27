#ifndef __LITERALPROPLINK
#define __LITERALPROPLINK

namespace VAL {
class SimpleProposition;
class Environment;
};

namespace Inst {

class Literal;
class instantiatedOp;

Literal * toLiteral(const VAL::SimpleProposition *);
VAL::Environment toEnv(instantiatedOp * op);

};

#endif

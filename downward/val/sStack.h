
/* 
  sStack.h

  Simple Stack.  

  $Date: 2001/08/02 16:49:21 $
  $Revision: 3.2 $

  This is an STL deque with a stack-like interface added.  This is an
  insecure stack with all the deque interface deliberately left
  available.  

*/

#ifndef SSTACK_H
#define SSTACK_H

#include <deque>

using std::deque;

namespace VAL {

template <class T>
class sStack : public deque<T>
{
private:
    typedef deque<T> _Base;
public:

    // push elem onto stack
    void push(const T& elem) 
	{
	    _Base::push_front(elem);
	};

     // pop elem from stack and return it
    T pop() 
	{
	    T elem(_Base::front());
	    _Base::pop_front();
	    return elem;
	};

    // return top element, leaving it on the stack
    T& top() 
	{
	    return _Base::front();
	};
};

};

#endif /* SSTACK_H */

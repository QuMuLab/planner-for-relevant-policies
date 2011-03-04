% Written by Wolfgang Faber <wf@wfaber.com>
%
% Input:
% right(L1,L2) : location L2 is right of location L1
% top(L1,L2): location L2 is on top of location L1
% box(L): location L initially holds a box
% solution(L): location L is a target for a box
% sokoban(L): the sokoban is at location L initially
% step(S): S is a step
% next(S1,S2): step S2 is the successor of step S1

% actionstep: can push at any step but the final one
actionstep(S) :- next(S,S1).

% utility predicates: left and bottom
left(L1,L2) :- right(L2,L1).
bottom(L1,L2) :- top(L2,L1).

% utility predicates: adjacent
adj(L1,L2) :- right(L1,L2).
adj(L1,L2) :- left(L1,L2).
adj(L1,L2) :- top(L1,L2).
adj(L1,L2) :- bottom(L1,L2).

% identify locations
location(L) :- adj(L,_).

% Initial configuration.
box_step(B,F) :- box(B), initial_step(F).
sokoban_step(S,F) :- sokoban(S), initial_step(F).

% push(B,D,B1,S):
% At actionstep S push box at location B in direction D (right, left, up, down)
% until location B1.
% The sokoban must be able to get to the location "before" B in order to push
% the box, also there should not be any boxes between B and B1 (and also not
% on B1 itself at step S.
push(B,right,B1,S) | -push(B,right,B1,S) :- reachable(L,S), right(L,B), box_step(B,S), pushable_right(B,B1,S), good_pushlocation(B1), actionstep(S).
push(B,left,B1,S) | -push(B,left,B1,S) :- reachable(L,S), left(L,B), box_step(B,S), pushable_left(B,B1,S), good_pushlocation(B1), actionstep(S).
push(B,up,B1,S) | -push(B,up,B1,S) :- reachable(L,S), top(L,B), box_step(B,S), pushable_top(B,B1,S), good_pushlocation(B1), actionstep(S).
push(B,down,B1,S) | -push(B,down,B1,S) :- reachable(L,S), bottom(L,B), box_step(B,S), pushable_bottom(B,B1,S), good_pushlocation(B1), actionstep(S).

% reachable(L,S):
% Identifies locations L which are reachable by the sokoban at step S.
reachable(L,S) :- sokoban_step(L,S).
reachable(L,S) :- reachable(L1,S), adj(L1,L), not box_step(L,S).

% pushable_right(B,D,S):
% Box at B can be pushed right until D at step S.
% Analogous for left, top, bottom.
pushable_right(B,D,S) :- box_step(B,S), right(B,D), not box_step(D,S), actionstep(S).
pushable_right(B,D,S) :- pushable_right(B,D1,S), right(D1,D), not box_step(D,S).
pushable_left(B,D,S) :- box_step(B,S), left(B,D), not box_step(D,S), actionstep(S).
pushable_left(B,D,S) :- pushable_left(B,D1,S), left(D1,D), not box_step(D,S).
pushable_top(B,D,S) :- box_step(B,S), top(B,D), not box_step(D,S), actionstep(S).
pushable_top(B,D,S) :- pushable_top(B,D1,S), top(D1,D), not box_step(D,S).
pushable_bottom(B,D,S) :- box_step(B,S), bottom(B,D), not box_step(D,S), actionstep(S).
pushable_bottom(B,D,S) :- pushable_bottom(B,D1,S), bottom(D1,D), not box_step(D,S).

% The sokoban is at a new location after a push and no longer at its original
% position.
sokoban_step(L,S1) :- push(_,right,B1,S), next(S,S1), right(L,B1).
sokoban_step(L,S1) :- push(_,left,B1,S), next(S,S1), left(L,B1).
sokoban_step(L,S1) :- push(_,up,B1,S), next(S,S1), top(L,B1).
sokoban_step(L,S1) :- push(_,down,B1,S), next(S,S1), bottom(L,B1).
-sokoban_step(L,S1) :- push(B,_,B1,S), next(S,S1), sokoban_step(L,S), B!=B1.

% Also the box_step has moved after having been pushed.
box_step(B,S1) :- push(_,_,B,S), next(S,S1).
-box_step(B,S1) :- push(B,_,B1,S), next(S,S1), B!=B1.

% Inertia: Boxes and the sokoban usually remain where they are.
box_step(LB,S1) :- box_step(LB,S), next(S,S1), not -box_step(LB,S1).
sokoban_step(LS,S) :- sokoban_step(LS,S), next(S,S1), not -sokoban_step(LS,S1).

% Don't push two different boxes in one step.
:- push(B,_,_,S), push(B1,_,_,S), B != B1.
% Don't push a box in different directions in one step.
:- push(B,D,_,S), push(B,D1,_,S), D != D1.
% Don't push a box onto different locations in one step.
:- push(B,D,B1,S), push(B,D,B11,S), B1 != B11.

% Avoid pushing boxes into dead ends. There should be a location to the left
% and right or to top and bottom. Otherwise the box cannot be taken out again,
% for instance from corners. Obviously if the location is a target, these
% restrictions do not apply, as the box may remain there forever.
good_pushlocation(L) :- right(L,_), left(L,_).
good_pushlocation(L) :- top(L,_), bottom(L,_).
good_pushlocation(L) :- solution(L).

final_step(S) :- step(S), not no_final_step(S).
no_final_step(S) :- next(S,S1).

initial_step(S) :- step(S), not no_initial_step(S).
no_initial_step(S) :- next(S1,S).

push_happens(S) :- push(_,_,_,S).
push_missing :- actionstep(S), not push_happens(S).
:- push_missing.
solution_notfound_step(S) :- solution(L), step(S), not box_step(L,S).
solution_notfound :- solution_notfound_step(S), final_step(S).
:- solution_notfound.

reachablespecialbox(right,B,S) :- reachable(L,S), right(L,B), box_step(B,S), actionstep(S), not solution_notfound_step(S).
reachablespecialbox(left,B,S) :- reachable(L,S), left(L,B), box_step(B,S), actionstep(S), not solution_notfound_step(S).
reachablespecialbox(up,B,S) :- reachable(L,S), top(L,B), box_step(B,S), actionstep(S), not solution_notfound_step(S).
reachablespecialbox(down,B,S) :- reachable(L,S), bottom(L,B), box_step(B,S), actionstep(S), not solution_notfound_step(S).

nsmallestspecial(D,B) :- reachablespecialbox(D,B,S), reachablespecialbox(D1,B1,S), B>B1.
nsmallestspecial(D,B) :- reachablespecialbox(D,B,S), reachablespecialbox(D1,B,S), D>D1.
smallestspecial(D,B) :- reachablespecialbox(D,B,S), not nsmallestspecial(D,B).

push(B,D,B,S) :- reachablespecialbox(D,B,S), smallestspecial(D,B).


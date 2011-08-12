% graph nodes
node(N) :- jet(N). node(N) :- junction(N). node(N) :- tank(N).

% lengths of paths to goal, bounded by the number of valves, recording also
% the number of leaking valves on the path
dist(J,0,0) :- goal(J).
dist(N,DN,LN) :- dist(K,DK,LK), link(N,K,V), DN=DK+1, LN=LK+1, numValves(NV), DN <= NV, leaking(V).
dist(N,DN,LK) :- dist(K,DK,LK), link(N,K,V), DN=DK+1, numValves(NV), DN <= NV, not leaking(V).

% minimum leaking distance of a node to the goal node
nodemindist(N,DN,LDN) :- node(N), minLkDist(N,LDN), minDist(N,DN,LDN).

minLkDist(N,LDN) :- dist(N,Fv1,LDN), not existLdnLessThan(N,LDN).
existLdnLessThan(N,LDN) :- dist(N,Fv1,LDN), dist(N,Fv2,LDN1), LDN1<LDN.

minDist(N,DN,LDN) :- dist(N,DN,LDN), not existDnLessThan(N,DN,LDN).
existDnLessThan(N,DN,LDN) :- dist(N,DN,LDN), dist(N,DN1,LDN), DN1<DN.

% minimum leaking distance of a full tank to the goal node
fulltankmindist(T,DT,LDT) :- tank(T), full(T), nodemindist(T,DT,LDT).

% Fail if no full tank can be reached from the goal.
reachablefulltankexists :- fulltankmindist(T,DT,LDT).
:- not reachablefulltankexists.

% the full tanks and their minimum leaking distances to the goal node, which
% have the minimum leaking distance over all full tanks
bestfulltankldist(T,SD,SDL) :- fulltankmindist(T,SD,SDL), not existFTLLessThan(SDL).
existFTLLessThan(SDL) :- fulltankmindist(Fv1,Fv2,SDL), fulltankmindist(Fv3,Fv4,SDL1), SDL1<SDL.

% among the full tanks with minimum leaking distance choose those with
% minimum distance from the goal
bestfulltankdist(T,SD,SDL) :- bestfulltankldist(T,SD,SDL), not existFTLessThan(SD, SDL).
existFTLessThan(SD,SDL) :- fulltankmindist(Fv1,SD,SDL), fulltankmindist(Fv2,SD1,SDL), SD1<SD.

goodtank(T) :- bestfulltankdist(T,Fv1,Fv2).

% "Choose" the lexicographically smallest good tank, as any will do.
nbesttank(T) :- goodtank(T), goodtank(T1), T1 < T.
besttank(T) :- goodtank(T), not nbesttank(T).

% Now go back to the goal, starting from the chosen tank.
reached(T,SD,SDL) :- bestfulltankdist(T,SD,SDL).

% In any step, choose the smallest valve among those linking the
% reached node of distance D to other nodes of distance D-1, tracking
% also the leaking distance (stays equal for non-leaking valves,
% decreases by one for leaking valves).
cand(V1,D1,LD1) :- reached(N,D,LD), LD1=LD-1, D1=D-1, link(N,N1,V1), nodemindist(N1,D1,LD1), leaking(V1).
cand(V1,D1,LD) :- reached(N,D,LD), D1=D-1, link(N,N1,V1), nodemindist(N1,D1,LD), not leaking(V1).

nsmallestvalve(V2,D1,LD2) :- cand(V1,D1,LD1), cand(V2,D1,LD2), V1 < V2.

smallestvalve(V1,D1,LD1) :- cand(V1,D1,LD1), not nsmallestvalve(V1,D1,LD1).

% Reverse order for switching on (moving from tank to jet, starting from 0).
switchon(V,DN) :- smallestvalve(V,D,Fv1), bestfulltankdist(Fv2,BD,Fv3), DX=BD-D, DN=DX-1.

% Now choose the smallest node linked by the chosen valve as being reached.
nsmallestnodeforvalve(N1,D1,LD1) :- reached(N,D,LD), smallestvalve(V,D1,LD1), nodemindist(N1,D1,LD1), nodemindist(N2,D1,LD1), N1 > N2, link(N,N1,V), link(N,N2,V).

smallestnodeforvalve(N1,D1,LD1) :- smallestvalve(V,D1,LD1), reached(N,D,LD), D1=D-1, link(N,N1,V), not nsmallestnodeforvalve(N1,D1,LD1).

reached(N,D,LD) :- smallestnodeforvalve(N,D,LD).

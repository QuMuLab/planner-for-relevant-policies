%  #######
%  #@ .. ##
%  # $ #  #
%  # #$$  #
%  #   #  #
%  #.  #  #
%  ########
% 
top(col2row2,col2row1).
top(col2row3,col2row2).
top(col2row4,col2row3).
top(col2row5,col2row4).
right(col2row5,col3row5).
top(col3row5,col3row4).
right(col3row4,col4row4).
top(col4row4,col4row3).
top(col4row3,col4row2).
top(col4row2,col4row1).
right(col4row1,col5row1).
right(col5row1,col6row1).
top(col6row2,col6row1).
top(col6row3,col6row2).
top(col6row4,col6row3).
top(col6row5,col6row4).
right(col6row5,col7row5).
top(col7row5,col7row4).
top(col7row4,col7row3).
top(col7row3,col7row2).
right(col6row4,col7row4).
right(col6row3,col7row3).
right(col5row3,col6row3).
right(col6row2,col7row2).
top(col3row2,col3row1).
right(col3row2,col4row2).
right(col3row1,col4row1).
right(col4row3,col5row3).
top(col4row5,col4row4).
right(col3row5,col4row5).
right(col2row4,col3row4).
right(col2row2,col3row2).
right(col2row1,col3row1).
box(col4row3).
box(col5row3).
box(col3row2).
solution(col2row5).
solution(col4row1).
solution(col5row1).
sokoban(col2row1).
step(1).
step(2).
step(3).
step(4).
step(5).
step(6).
step(7).
step(8).
step(9).
step(10).
next(1,2).
next(2,3).
next(3,4).
next(4,5).
next(5,6).
next(6,7).
next(7,8).
next(8,9).
next(9,10).

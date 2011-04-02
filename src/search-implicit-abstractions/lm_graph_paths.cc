#include "lm_graph_paths.h"

#include <math.h>

LmGraphPaths::LmGraphPaths(LandmarksGraph& lgraph) {
	// Sorting nodes topologically and setting the initial coloring (numbering)
	vector<int> nodes;
	int max_id = 0;
	// Loop on all landmarks, take singletons out
	for (set<LandmarkNode*>::const_iterator it = lgraph.get_nodes().begin(); it
			!= lgraph.get_nodes().end(); it++) {
		LandmarkNode& curr_land = **it;
    	int curr_id = curr_land.id;
    	if (curr_land.children.empty()) { 	    // The node is sink
        	if (curr_land.parents.empty()) {    // The node is singleton
//        		cout << "Adding singleton " << curr_id << endl;
        	    initially_no_edges.push_back(*it);
        	    continue;
        	}
        	sorted_nodes.push_back(curr_id);
        	target_nodes.push_back(curr_id);
//    		cout << "Sink node " << curr_id << endl;
    	} else { // Going over the children and adding an edge.
        	if (curr_land.parents.empty()) {    // The node is source
        		source_nodes.push_back(curr_id);
        	}
    	    for (hash_map<LandmarkNode*, edge_type, hash_pointer>::const_iterator
    	            child_it = curr_land.children.begin(); child_it
    	            != curr_land.children.end(); child_it++) {
    	    	// Adding the edges
		        LandmarkNode* child_p = child_it->first;
		        to_nodes[curr_id].push_back(child_p->id);
//	    		cout << "Adding edge (" << curr_id << "," << child_p->id << ")" << endl;
    	    }
    	}

    	if (curr_id > max_id)
	    	max_id = curr_id;
	    nodes.push_back(curr_id);
//		cout << "Adding node " << curr_id << endl;
	    landmarks_by_id[curr_id] = *it;
	}
//	cout << "Done adding nodes" << endl;

	// set initial marking, order nodes topologically.
	land_color.assign(max_id+1,-1);

	// Sorting nodes in topological order (bottom first)
	for (int i=0; i < sorted_nodes.size(); i++) {
		land_color[sorted_nodes[i]] = 0;
	}

	while (sorted_nodes.size() < nodes.size()) {
		for (int i=0; i < nodes.size(); i++) {
			if (land_color[nodes[i]] != -1)   // Already marked
				continue;

			bool to_mark = true;
			int mark = 0;
			vector<int> children = to_nodes[nodes[i]];
			for (int j=0; j < children.size(); j++) {
		    	if (land_color[children[j]] == -1) {
		    		to_mark = false;
		    		break;
		    	}
		    	if (land_color[children[j]] > mark)
		    		mark = land_color[children[j]];
			}

		    if (to_mark) {
		    	land_color[nodes[i]] = mark + 1;
		    	sorted_nodes.push_back(nodes[i]);
		    }
		}
	}
/*	cout << "Done ordering nodes" << endl;
	for (int i=0; i < sorted_nodes.size(); i++) {
    	cout << "Node " << sorted_nodes[i] << " mark " << land_color[sorted_nodes[i]] << endl;
	}*/
}


LmGraphPaths::~LmGraphPaths() {

}

void LmGraphPaths::update_marking() {
	for (int i=0; i < sorted_nodes.size(); i++) {
		int mark = -1;
		vector<int> children = to_nodes[sorted_nodes[i]];
		for (int j=0; j < children.size(); j++) {
	    	if (land_color[children[j]] > mark)
	    		mark = land_color[children[j]];
		}
    	land_color[sorted_nodes[i]] = mark + 1;
//    	cout << "Node " << sorted_nodes[i] << " mark " << land_color[sorted_nodes[i]] << endl;
	}
}
bool LmGraphPaths::is_max_child(int node_id, int child_id) const {
	return (land_color[child_id] == land_color[node_id] - 1);
}

void LmGraphPaths::erase_link(int node_id, int to_index) {

	vector<int> children = to_nodes[node_id];
	children.erase(children.begin()+to_index);

	if (children.size() > 0) {
		to_nodes[node_id] = children;
	} else {
		hash_map<int, vector<int> >::iterator it = to_nodes.find(node_id);
		if (it != to_nodes.end())
			to_nodes.erase(it);
	}
}

LandmarkNode* LmGraphPaths::extract_max_child_node(int node_id) {
	vector<int> children = to_nodes[node_id];
	int max_ch = -1, ch_sz = children.size();
	for (int ch = 0; ch < ch_sz; ch++) {
		if (is_max_child(node_id,children[ch])) {
			max_ch = children[ch];
			erase_link(node_id,ch);
//			children.erase(children.begin()+ch);
			break;
		}
	}
/*
	if (children.size() > 0) {
		to_nodes[node_id] = children;
	} else {
		hash_map<int, vector<int> >::iterator it = to_nodes.find(node_id);
		if (it != to_nodes.end())
			to_nodes.erase(it);
	}
*/
	assert(max_ch != -1);
	return landmarks_by_id[max_ch];
}

int LmGraphPaths::get_max_node() const {
	int max_len = 0;
	int max_node = -1;
	for (int i=0; i < sorted_nodes.size(); i++) {
		if (land_color[sorted_nodes[i]] > max_len) {
			max_len = land_color[sorted_nodes[i]];
			max_node = sorted_nodes[i];
		}
	}
	return max_node;
}

void LmGraphPaths::remove_shortcuts(vector<LandmarkNode*>& path) {

	for (int i=0; i < path.size() - 2; i++) {
		for (int j=i+2; j < path.size(); j++) {
			// Removing shortcut from i to j
			int to = path[i]->id;
			int from = path[j]->id;
//			cout << "Erasing link (" << from << "," << to << ")" << endl;
			for (int ch=0; ch < to_nodes[from].size(); ch++) {
//				cout << to_nodes[from][ch];
				if (to_nodes[from][ch] == to) {
//					cout << "  Found!" << endl;
					erase_link(from, ch);
					break;
				}
//				cout << endl;
			}
		}
	}
}


void LmGraphPaths::extract_longest_path(vector<LandmarkNode*>& path) {

	assert(path.size()==0);
	int next_node = get_max_node();
	int max_len = land_color[next_node];
//	cout << "Next node: " << next_node << " distance " << max_len <<endl;
	// Collecting the path, removing links, updating the marks of nodes.
/*	path.reserve(max_len+1);
	path[max_len] = landmarks_by_id[next_node];
	cout << path[max_len]->id ;
	for (int i=max_len-1; i >= 0; i--) {
		path[i] = extract_max_child_node(next_node);
		cout << "  " << path[i]->id ;
		next_node = path[i]->id;
	}
	cout << endl;*/

	path.push_back(landmarks_by_id[next_node]);
	for (int i=0; i < max_len; i++) {
		LandmarkNode* node = extract_max_child_node(next_node);
		path.insert(path.begin(),node);
		next_node = node->id;
	}
	remove_shortcuts(path);
	update_marking();
}

int LmGraphPaths::get_num_paths() const {

	int num_nodes = land_color.size();

	int** A = new int *[num_nodes];
	for( int i = 0 ; i < num_nodes ; i++ )
		A[i] = new int [num_nodes];

	for( int i = 0 ; i < num_nodes ; i++ )
		for( int j = 0 ; j < num_nodes ; j++ )
			A[i][j] = 0;

	// Initiating the adjacent matrix
	for (hash_map<int, vector<int> >::const_iterator it = to_nodes.begin(); it
					!= to_nodes.end(); it++) {
		int from = it->first;
		vector<int> to = it->second;
		for (int i=0; i<to.size(); i++) {
			A[from][to[i]] = 1;
		}
	}
/*
	for( int i = 0 ; i < num_nodes ; i++ ) {
		for( int j = 0 ; j < num_nodes ; j++ )
			cout << A[i][j] << " " ;

		cout << endl;
	}
*/
	// Counting the number of s-t paths
	for( int i = 0 ; i < num_nodes ; i++ )
		for( int j = 0 ; j < num_nodes ; j++ )
			for( int k = 0 ; k < num_nodes ; k++ )
				A[i][j] += A[i][k]*A[k][j];

	int val = 0;
	// Getting the total number of paths
	for( int i = 0 ; i < source_nodes.size() ; i++ ) {
		for( int j = 0 ; j < target_nodes.size() ; j++ ) {
			val += A[source_nodes[i]][target_nodes[j]];
		}
	}

	for( int i = 0 ; i < num_nodes ; i++ )
		delete [] A[i];

	delete [] A;

	return val;

}



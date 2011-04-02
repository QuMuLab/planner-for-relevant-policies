#ifndef LM_GRAPH_PATHS_H
#define LM_GRAPH_PATHS_H


#include "landmarks/landmarks_graph.h"
#include "landmarks/landmark_status_manager.h"

class LmGraphPaths {

	hash_map<int, LandmarkNode*> landmarks_by_id;
	vector<LandmarkNode*> initially_no_edges;  // Landmarks with no edges
	vector<int> sorted_nodes;
	hash_map<int, vector<int> > to_nodes;
	vector<int> land_color;
	vector<int> source_nodes, target_nodes;

	int get_max_node() const;
	bool is_max_child(int node_id, int child_id) const;
	LandmarkNode* extract_max_child_node(int node_id);
	void update_marking();
	void remove_shortcuts(vector<LandmarkNode*>& path);
	void erase_link(int node_id, int to_index);

public:
	LmGraphPaths(LandmarksGraph& lgraph);
	~LmGraphPaths();

	bool is_edgeless() const {
		if (to_nodes.empty()) return true;
		int node = get_max_node();
		return (-1 == node);
//		cout << "Checking if empty - node " << node << " mark " << land_color[node] << endl;
//		return (land_color[node] == 0);
/*		for (hash_map<int, vector<int> >::const_iterator it = to_nodes.begin(); it
				!= to_nodes.end(); it++) {
			int from = it->first;
			cout << "From " << from << endl;
			vector<int> to = it->second;
			for (int i=0; i<to.size(); i++) {
				cout << "(" << from << "," << to[i] << ")" << endl;
			}

		}
		return false;*/
	}
	vector<LandmarkNode*>& get_singleton_nodes() { return initially_no_edges; }
	void extract_longest_path(vector<LandmarkNode*>& path);

	int get_num_paths() const;

};

#endif

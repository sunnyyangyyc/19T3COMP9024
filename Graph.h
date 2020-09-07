// Graph ADT interface ... COMP9024 19T3
#include <stdbool.h>

typedef struct GraphRep *Graph;

typedef struct node{
    int train;
    int time;
    char stop_name[32];
    int next_stop_time;
    char *next_stop;
    struct node *next;
}Node;

Node *joinLL(Node *, Node *);
Node *newNode(int,int,char *);
void showLL(Node*);
Node *nextLL(Node *);
void addTimeAndNextStop(Node*,int,char*);

Graph newGraph(int);
void insertGraph(Graph, int,Node*);
Node* getStationLL(Graph, char*);
void  showGraph(Graph);
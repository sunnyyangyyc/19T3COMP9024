// Graph ADT
// Adjacency Matrix Representation ... COMP9024 19T3
#include "Graph.h"
#include <assert.h>
#include <stdlib.h>
#include <stdio.h>
#include <string.h>

typedef struct GraphRep {
    Node **edges;
    int nV;
} GraphRep;


Node *joinLL(Node *head, Node *new) {
    assert(new != NULL);
    if (head == NULL) {
        head = new;
    } else if (new->time > head->time) {
        new->next = head;
        head = new;
    } else {
        Node *p = head;
        while (p->next != NULL && p->next->time > new->time) {
            p->next;
        }
        new->next = p->next;
        p->next = new;
    }
    return head;
}


Node *newNode(int train, int time, char *s) {
    Node *new = malloc(sizeof(Node));
    assert(new != NULL);
    new->train = train;
    new->time = time;
    strcpy(new->stop_name, s);

    new->next_stop_time = -1;
    new->next_stop = NULL;
    new->next = NULL;
    return new;
}

Node *nextLL(Node *ll) {
    return ll->next;
}

int lenLL(Node *ll) {
    Node *p;
    int count = 0;
    p = ll;
    while (p != NULL) {
        count++;
        p = p->next;
    }
    return count;
}


void showLL(Node *ll) {
    Node *p;
    for (p = ll; p != NULL; p = p->next) {
        printf("(%d %d %s %d %s)", p->train, p->time, p->stop_name, p->next_stop_time, p->next_stop);
        if (p->next != NULL) {
            printf("->");
        }
        putchar('\n');
    }
}

void showNode(Node *p) {
    if (p != NULL) {
        printf("(%d %d %s %d %s)", p->train, p->time, p->stop_name, p->next_stop_time, p->next_stop);
    }
}

void freeLL(Node *ll) {
    Node *p = ll;
    while (p != NULL) {
        Node *temp = p->next;
        free(p);
        p = temp;
    }
}

void addTimeAndNextStop(Node *ll, int time, char *next_stop) {
    ll->next_stop_time = time;
    ll->next_stop = malloc(32 * sizeof(char));
    strcpy(ll->next_stop, next_stop);
}


Graph newGraph(int v) {
    assert(v >= 0);
    int i;

    Graph g = malloc(sizeof(GraphRep));
    assert(g != NULL);
    g->nV = v;

    g->edges = malloc(v * sizeof(Node *));
    assert(g->edges != NULL);
    for (int j = 0; j < v; ++j) {
        g->edges[j] = NULL;
    }
    return g;
}


void showGraph(Graph g) {
    for (int i = 0; i < g->nV; ++i) {
        printf("station %d:\n", i);
        Node *p = g->edges[i];
        showLL(p);
    }

}

void insertGraph(Graph g, int index, Node *ll) {
    ll = joinLL(g->edges[index], ll);
    g->edges[index] = ll;
}

Node *getStationLL(Graph g, char *station) {
    Node *ll = NULL;
    for (int i = 0; i < g->nV; ++i) {
        if (g->edges[i] && strcmp(g->edges[i]->stop_name, station) == 0) {
            return g->edges[i];
        }
    }
    return ll;
}

#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <assert.h>
#include "Graph.h"

#define MAX_CHAR 32


typedef struct path {
    int nb_of_stop;
    Node **stops;
} path;

path *initialize_path(void) {
    path *res = malloc(sizeof(path));
    res->nb_of_stop = 0;
    res->stops = malloc(100 * sizeof(Node *));
    return res;
}

int get_index(char array_of_str[][MAX_CHAR], int length, char *target) {
    for (int i = 0; i < length; ++i) {
        if (strcmp(array_of_str[i], target) == 0) {
            return i;
        }
    }
    return -1;
}


void display_path(path *p) {
    if (p->nb_of_stop == 0) {
        printf("\nNo connection found\n");
        return;
    }
    printf("\n");
    for (int i = 0; i < p->nb_of_stop; ++i) {
        Node *stop = p->stops[i];

        if (stop->time < 1000) putchar('0');
        printf("%d %s\n", stop->time, stop->stop_name);
        if (i < p->nb_of_stop - 1 && stop->train != p->stops[i + 1]->train) {
            if (stop->next_stop_time < 1000) putchar('0');
            printf("%d %s\n", stop->time, stop->stop_name);
            printf("Change at %s\n", stop->next_stop);
        }
    }
    Node *seconde_to_last_stop = p->stops[p->nb_of_stop - 1];
    if (seconde_to_last_stop->next_stop_time < 1000) putchar('0');
    printf("%d %s\n", seconde_to_last_stop->next_stop_time, seconde_to_last_stop->next_stop);

    printf("\n");
}

void update_best_path(path *best_path, path *cur_path) {
    if (best_path->nb_of_stop == 0) {


        for (int i = 0; i < cur_path->nb_of_stop; ++i) {
            best_path->stops[i] = cur_path->stops[i];
        }
        best_path->nb_of_stop = cur_path->nb_of_stop;
        return;
    }

    int best_depart_time = best_path->stops[0]->time;
    int best_arrive_time = best_path->stops[best_path->nb_of_stop - 1]->next_stop_time;
    int new_depart_time = cur_path->stops[0]->time;
    int new_arrive_time = cur_path->stops[cur_path->nb_of_stop - 1]->next_stop_time;


    if ((best_depart_time < new_depart_time) ||
        (best_depart_time == new_depart_time && best_arrive_time > new_arrive_time)) {


        for (int i = 0; i < cur_path->nb_of_stop; ++i) {
            best_path->stops[i] = cur_path->stops[i];
        }
        best_path->nb_of_stop = cur_path->nb_of_stop;
    }
}


int find_path(Graph g, char *src, char *dst, int cur, int deadline, path *best_path, path *cur_path, int level) {

    int flag = -1;

    if (cur > deadline) {
        return -1;
    } else if (strcmp(src, dst) == 0) {
        update_best_path(best_path, cur_path);
        return 1;
    }

    for (Node *ll = getStationLL(g, src); ll != NULL; ll = ll->next) {

        int time = ll->time;
        int next_time = ll->next_stop_time;
        char *next_stop = ll->next_stop;
        if (time < cur) {
            break;
        }

        cur_path->nb_of_stop = level;
        cur_path->stops[level - 1] = ll;
        if (next_stop != NULL) {
            if (find_path(g, next_stop, dst, next_time, deadline, best_path, cur_path, level + 1) != -1) {

                flag = 1;
            }
        }
    }
    return flag;
}

int main() {
    int nb_of_station = 25, nb_of_train, nb_of_stop;
    Graph graph_ptr;

    int time;
    char stop_name[MAX_CHAR];

    printf("enter the number of station: ");
    scanf("%d", &nb_of_station);
    assert(nb_of_station > 0);
    graph_ptr = newGraph(nb_of_station);
    char stations[nb_of_station][MAX_CHAR];
    for (int i = 0; i < nb_of_station; ++i) {
        scanf("%s", stations[i]);
    }


    printf("enter the number of trains: ");
    scanf("%d", &nb_of_train);
    for (int j = 0; j < nb_of_train; ++j) {
        printf("enter the number of stops: ");
        scanf("%d", &nb_of_stop);
        Node *prev = NULL;
        for (int i = 0; i < nb_of_stop; ++i) {
            scanf("%d", &time);
            scanf("%s", stop_name);

            if (prev != NULL) {
                addTimeAndNextStop(prev, time, stop_name);
            }
            Node *new = newNode(i, time, stop_name);
            insertGraph(graph_ptr, get_index(stations, nb_of_station, stop_name), new);
            prev = new;
        }

    }
//    showGraph(graph_ptr);

    char source[MAX_CHAR], destination[MAX_CHAR];
    int deadline;

    printf("From:");
    scanf("%s", source);
    while (strcmp(source, "done") != 0) {

        path *best_path = initialize_path();
        path *cur_path = initialize_path();
        printf("To:");
        scanf("%s", destination);
        printf("Arrive by:");
        scanf("%d", &deadline);
        find_path(graph_ptr, source, destination, -1, deadline, best_path, cur_path, 1);
        printf("-----------done------------\n");
        display_path(best_path);
        free(best_path->stops);
        free(best_path);
        free(cur_path->stops);
        free(cur_path);
        printf("From:");
        scanf("%s", source);
    }
    printf("Thank you for using myTrain.\n");
    return 0;
}

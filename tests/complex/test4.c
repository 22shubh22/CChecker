#include <stdio.h>
#include <stdbool.h>
#include <assert.h>
#include <limits.h>
#include <stdlib.h>
#include <string.h>

#define MAXN 150002
#define MAXM 150002

typedef unsigned int u32;


struct list {
	u32 degree; // cant. de vecinos del nodo / tamaño de la lista
	u32 busy; //cant. de slots ocupados
	u32 color_of_node;
	u32* neighbors;
};

struct graph {
	u32 n; // #nodos
	u32 m; // #aristas
	struct list* AdjList; //lista de adyacencia de grafo 
};

struct graph empty_graph(u32 n) { //crea un grafo vacio con n nodos
	struct graph g;
	g.n=n;
	g.m=0;
	g.AdjList = (struct list*) malloc(n*sizeof(struct list));
	return g;
}

struct list empty_list(u32 v) { //crea una lista con espacio para v vecinos
	struct list list;
	list.degree=v;
	list.busy=0;
	list.color_of_node=0;
	list.neighbors = (u32*) malloc(v*sizeof(u32));
	return list;
}

struct list add_neighbor(struct list list, u32 v) {
	list.neighbors[list.busy]=v;
	list.busy++;
	return list;
}

struct graph append_edge(struct graph g, u32 a, u32 b) {
	g.m++;
	g.AdjList[a]=add_neighbor(g.AdjList[a],b);
	g.AdjList[b]=add_neighbor(g.AdjList[b],a);
	return g;
}

void print_graph(struct graph g) {
	for(int i=0;i<g.n;i++) {
		printf("neigbors of vertex %u are: ",i);
		for(int j=0;j<g.AdjList[i].degree;j++) {
			//printf("%u ",g.AdjList[i].neighbors[j]);
		}
		puts("");
	}
}

bool vis[MAXN];
long long co=0;
u32 cc[MAXN];

void dfs(struct graph g, u32 node) {
	if(!vis[node]) {
		cc[co]=node;
		co++;
		vis[node]=true;
		for(int i=0;i<g.AdjList[node].degree;i++) {
			dfs(g,g.AdjList[node].neighbors[i]);
		}
	}
}

int main() {
	memset(vis,0,sizeof(vis));
	memset(cc,0,sizeof(cc));
	u32 n,m;
	scanf("%u %u",&n,&m); //n es la cantidad de nodos y m la de aristas que me van a inputear
	struct graph g = empty_graph(n);
	u32 degrees[MAXN]; //acá voy a guardar los degrees de todos los nodos
	memset(degrees,0,sizeof(degrees));
	u32 edges[MAXM][2]; //acá voy a guardarme cuales son las aristas que me inputearon
	for(int i=0;i<m;i++) {
		u32 a,b;
		scanf("%u %u",&a,&b);
		a--,b--;
		edges[i][0]=a,edges[i][1]=b;
		degrees[a]++,degrees[b]++;
	}
	for(int i=0;i<n;i++) {
		g.AdjList[i]=empty_list(degrees[i]);
	}
	for(int i=0;i<m;i++) {
		g = append_edge(g,edges[i][0],edges[i][1]);
	}
	for(int k=0;k<n;k++) {
		if(!vis[k]) {
			co=0;
			dfs(g,k);
			long long S=0;
			for(int i=0;i<co;i++) {
				S+=g.AdjList[cc[i]].degree;
			}
			if(S!=co*(co-1)) {
				puts("NO");
				return 0;
			}
		}
	}
	puts("YES");
	return 0;
}
